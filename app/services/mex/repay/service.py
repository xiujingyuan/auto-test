import copy
import json

import pytz

from app.common.http_util import Http
from app.services import AssetTran, AssetExtend, Asset
from app.services.china.repay import query_withhold
from app.services.china.repay.Model import Withhold
from app.services.mex.grant.service import MexGrantService
from app.services.repay import OverseaRepayService, TIMEZONE


class MexRepayService(OverseaRepayService):
    def __init__(self, env, run_env, check_req=False, return_req=False):
        self.repay_host = "http://repay{0}-mex.c99349d1eb3d045a4857270fb79311aa0.cn-shanghai." \
                          "alicontainer.com".format(env)
        self.grant = MexGrantService(env, run_env, check_req, return_req)
        super(MexRepayService, self).__init__('mex', env, run_env, check_req, return_req)

    def __get_active_request_data__(self, item_no, item_no_x, amount, x_amount, repay_card, item_no_priority=12,
                                    item_no_x_priority=1, order_no='', coupon_list=None):
        card_info = self.get_active_card_info(item_no, repay_card)
        for coupon in coupon_list.split("\n"):
            coupon_or, coupon_num, coupon_amount, coupon_type = coupon.split(",")
        key = self.__create_req_key__(item_no, prefix='Active')
        active_request_data = {
            "type": "PaydayloanUserActiveRepay",
            "key": key,
            "from_system": "DSQ",
            "data": {
                "total_amount": amount + x_amount,
                "project_list": [],
                "order_no": order_no,
                "verify_code": None,
                "verify_seq": None
            }
        }

        coupon_item = {'coupon_num': "", 'coupon_amount': 0, 'coupon_type': 'cash'}

        for four_element_key, four_element_value in self.__get_four_element_key__(repay_card).items():
            active_request_data['data'][four_element_key] = card_info[four_element_value]
        amount_info_list = [(item_no, amount, item_no_priority, None, None),
                            (item_no_x, x_amount, item_no_x_priority, None, None)]
        amount_info_key = ("project_num", "amount", "priority", "coupon_num", "coupon_amount")
        for amount_info in amount_info_list:
            if amount_info[1] != 0:
                active_request_data['data']['project_list'].append(dict(zip(amount_info_key, amount_info)))
        return active_request_data

    @query_withhold
    def active_repay(self, item_no, amount=0, x_amount=0, period_start=None, period_end=None,
                     coupon_list=''):
        asset_tran = self.db_session.query(AssetTran).filter(AssetTran.asset_tran_asset_item_no == item_no).all()
        max_period = asset_tran[-1].asset_tran_period
        is_overdue = False if self.cal_days(self.get_date(), asset_tran[-1].asset_tran_due_at) > 0 else True
        item_no_x = self.get_no_loan(item_no) if item_no else ''
        if not item_no:
            raise ValueError('need item_no or item_no_rights one is not null!')
        amount = self.__get_repay_amount__(amount, item_no, period_start, period_end, max_period, is_overdue)
        x_amount = self.__get_repay_amount__(x_amount, item_no_x, period_start, period_end, max_period, is_overdue)

        if amount == 0 and x_amount == 0:
            return "当前已结清", "", []
        request_data = self.__get_active_request_data__(item_no, item_no_x, amount, x_amount, 1, coupon_list)
        print(json.dumps(request_data))
        resp = Http.http_post(self.active_repay_url, request_data)
        return request_data, self.active_repay_url, resp

    def repay_callback(self, serial_no, status, back_amount=0, refresh_type=None, max_create_at=None, item_no=None):
        withhold = self.db_session.query(Withhold).filter(Withhold.withhold_serial_no == serial_no).first()
        if not withhold:
            raise ValueError('代扣记录不存在')
        if not back_amount:
            return
        channel = withhold.withhold_channel if \
            withhold.withhold_channel and \
            withhold.withhold_channel not in ('lanzhou_haoyue', 'hami_tianshan') else 'baofu_4_baidu'
        req_data = {
            "amount": back_amount,
            "platform_code": "E20000",
            "payment_mode": "CREDIT_CARD",
            "merchant_key": serial_no,
            "channel_name": channel,
            "channel_key": serial_no,
            "finished_at": self.get_date(is_str=True, timezone=pytz.timezone(TIMEZONE[self.country])),
            "transaction_status": status,
            "sign": "6401cd046b5ae44ef208b8ea82d398ab",
            "from_system": "paysvr",
            "channel_message": "交易成功" if status == 2 else '交易失败'
        }
        resp = Http.http_post(self.pay_svr_callback_url, req_data)
        if resp['code'] != 0:
            raise ValueError('执行回调接口失败，返回:{0}'.format(resp))
        self.run_callback_task_and_msg(serial_no, status)
        if refresh_type is not None:
            return self.info_refresh(item_no, refresh_type=refresh_type, max_create_at=max_create_at)
        return req_data, self.pay_svr_callback_url, resp

