import copy
import json
import random

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

    def __get_active_request_data__(self, item_no, item_no_x, amount, x_amount, repay_card, payment_type,
                                    item_no_priority=12, item_no_x_priority=1, order_no='', coupon_list=None):
        card_info = self.get_active_card_info(item_no, repay_card)
        coupon_dict = dict(zip((item_no, item_no_x), ([], [])))
        if coupon_list and coupon_list is not None:
            for coupon in coupon_list.split("\n"):
                coupon_or, coupon_num, coupon_amount, coupon_type = coupon.split(",")
                coupon_or = item_no if coupon_or == '1' else item_no_x
                coupon_num = coupon_num if coupon_num else '{0}_{1}'.format(
                    self.get_date(is_str=True, fmt='%Y%m%d%H%M%S'), coupon_type)
                if coupon_amount:
                    coupon_dict[coupon_or].append(dict(zip(('coupon_num', 'coupon_amount', 'coupon_type'),
                                                           (coupon_num, int(coupon_amount), coupon_type))))
        key = self.__create_req_key__(item_no, prefix='Active')
        active_request_data = {
            "type": "PaydayloanUserActiveRepay",
            "key": key,
            "from_system": "DSQ",
            "data": {
                "card_cvv": None,
                "payment_mode": None,
                "user_ip": None,
                "address": None,
                "email": None,
                "user_name": None,
                "individual_uuid": None,
                "payment_type": payment_type,
                "payment_option": random.choice(["oxxo_cash", "bank_account"]) if
                payment_type == 'barcode' else payment_type,
                "card_num_encrypt": None,
                "card_expiry_year": None,
                "card_expiry_month": None,
                "total_amount": amount + x_amount,
                "project_list": [],
                "order_no": order_no,
                "verify_code": None,
                "verify_seq": None
            }
        }

        for four_element_key, four_element_value in self.__get_four_element_key__(repay_card).items():
            active_request_data['data'][four_element_key] = card_info[four_element_value]
        amount_info_list = [(item_no, amount, item_no_priority, None, None, coupon_dict[item_no]),
                            (item_no_x, x_amount, item_no_x_priority, None, None, coupon_dict[item_no_x])]
        amount_info_key = ("project_num", "amount", "priority", "coupon_num", "coupon_amount", "coupon_list")
        for amount_info in amount_info_list:
            if amount_info[1] != 0:
                active_request_data['data']['project_list'].append(dict(zip(amount_info_key, amount_info)))
        return active_request_data

    @query_withhold
    def active_repay(self, item_no, payment_type, amount=0, x_amount=0, period_start=None, period_end=None,
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
        request_data = self.__get_active_request_data__(item_no, item_no_x, amount, x_amount, 1, payment_type,
                                                        coupon_list=coupon_list)
        print(json.dumps(request_data))
        resp = Http.http_post(self.active_repay_url, request_data)
        return request_data, self.active_repay_url, resp

    def repay_callback(self, serial_no, status, back_amount=0, refresh_type=None, max_create_at=None, item_no=None):
        withhold = self.db_session.query(Withhold).filter(Withhold.withhold_serial_no == serial_no).first()
        if not withhold:
            raise ValueError('代扣记录不存在')
        back_amount = back_amount if back_amount else withhold.withhold_amount
        channel = withhold.withhold_channel if \
            withhold.withhold_channel and \
            withhold.withhold_channel not in ('lanzhou_haoyue', 'hami_tianshan') else 'baofu_4_baidu'
        key = self.__create_req_key__(item_no, prefix='CallBack')
        req_data = {
            "from_system": "paysvr",
            "key": key,
            "type": "withhold",
            "data": {
                "amount": back_amount,
                "platform_code": "E20000",
                "payment_mode": "CREDIT_CARD",
                "merchant_key": serial_no,
                "channel_name": channel,
                "channel_key": serial_no,
                "finished_at": self.get_date(is_str=True, timezone=pytz.timezone(TIMEZONE[self.country])),
                "status": status,
                "channel_message": "交易成功" if status == 2 else '交易失败'
            }
        }
        resp = Http.http_post(self.pay_svr_callback_url, req_data)
        if resp['code'] != 0:
            raise ValueError('执行回调接口失败，返回:{0}'.format(resp))
        if refresh_type is not None:
            return self.info_refresh(item_no, refresh_type=refresh_type, max_create_at=max_create_at)
        return req_data, self.pay_svr_callback_url, resp

    def repay_offline_callback(self, item_no, back_amount=0, refresh_type=None, max_create_at=None):
        asset = self.db_session.query(Asset).filter(Asset.asset_item_no == item_no).first()
        if asset is None:
            raise ValueError('not found the asset!')
        back_amount = back_amount if back_amount else asset.asset_balance_amount
        key = self.__create_req_key__(item_no, prefix='OfflineCallBack')
        channel_key = self.__create_req_key__(item_no, prefix='channel_')
        req_data = {
            "from_system": "paysvr",
            "key": key,
            "type": "withhold",
            "data": {
                "amount": back_amount,
                "merchant_key": channel_key,
                "status": "2",
                "finished_at": self.get_date(is_str=True, timezone=pytz.timezone(TIMEZONE[self.country])),
                "channel_key": channel_key,
                "channel_name": "pandapay_alibey_collect",
                "from_system": None,
                "platform_message": "OK",
                "platform_code": "E20000",
                "payment_mode": "",
                "account_no": item_no
            },
            "sync_datetime": None,
            "busi_key": "e82c588cb1fc4885be15b19c130f33f2"
        }
        resp = Http.http_post(self.pay_svr_offline_callback_url, req_data)
        if resp['code'] != 0:
            raise ValueError('执行回调接口失败，返回:{0}'.format(resp))
        self.run_task_by_order_no(channel_key, 'offline_withhold_process')
        self.run_task_by_order_no(channel_key, 'withhold_callback_process')
        if refresh_type is not None:
            return self.info_refresh(item_no, refresh_type=refresh_type, max_create_at=max_create_at)
        return req_data, self.pay_svr_callback_url, resp



