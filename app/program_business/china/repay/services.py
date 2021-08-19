
import copy
import json

import time
import datetime
from functools import reduce

from sqlalchemy import desc

from app.common.http_util import Http
from app.common.tools import get_date
from app.program_business import BaseAuto
from app.program_business.china.biz_central.services import ChinaBizCentralAuto
from app.program_business.china.grant.services import ChinaGrantAuto
from app.program_business.china.repay import query_withhold
from app.program_business.china.repay.Model import Asset, AssetExtend, Task, WithholdOrder, AssetTran, \
    SendMsg, Withhold, CapitalAsset, CapitalTransaction


class ChinaRepayAuto(BaseAuto):
    def __init__(self, env, run_env, check_req=False, return_req=False):
        super(ChinaRepayAuto, self).__init__('china', 'repay', env, run_env, check_req, return_req)
        self.host_url = "https://kong-api-test.kuainiujinke.com/rbiz{0}".format(env)
        self.grant = ChinaGrantAuto(env, run_env, check_req, return_req)
        self.biz_central = ChinaBizCentralAuto(env, run_env, check_req, return_req)
        self.decrease_url = self.host_url + "/asset/bill/decrease"
        self.active_repay_url = self.host_url + "/paydayloan/repay/combo-active-encrypt"
        self.fox_repay_url = self.host_url + "/fox/manual-withhold-encrypt"
        self.refresh_url = self.host_url + "/asset/refreshLateFee"
        self.send_msg_url = self.host_url + "/paydayloan/repay/bindSms"
        self.pay_svr_callback_url = self.host_url + "/paysvr/callback"
        self.run_task_id_url = self.host_url + '/task/run?taskId={0}'
        self.run_msg_id_url = self.host_url + '/msg/run?msgId={0}'
        self.run_task_order_url = self.host_url + '/task/run?orderNo={0}'

    def auto_loan(self, loan_channel, count, four_element):
        self.log.log_info("rbiz_loan_tool_auto_import...env=%s, channel_name=%s" % (self.env, loan_channel))
        try:
            item_no, asset_info = self.grant.asset_import(loan_channel, four_element, count=count)
            self.grant.loan_success(item_no)
            item_no_loan = ""
            self.log.log_info("大单资产编号：%s" % item_no)
            self.log.log_info("小单资产编号：%s" % item_no_loan)
        except Exception as e:
            item_no, item_no_loan = '', ''
            self.log.log_info("%s, 资产生成失败：%s" % (item_no, e))
            return "放款失败", "资产生成失败：%s" % e
        else:
            return item_no, item_no_loan

    def send_msg(self, serial_no):
        req_data = {
            "busi_key": "413123123123123",
            "data": {
                "order_no": serial_no
            },
            "from_system": "Rbiz",
            "key": self.__create_req_key__('', prefix='Msg'),
            "sync_datetime": 0,
            "type": "SendBindSms"
        }
        ret = Http.http_post(self.send_msg_url, req_data)
        if ret['code'] != 0:
            raise ValueError('发送短信失败, {0}'.format(ret['message']))
        verify_seq = ret['data']['verify_seq']
        return verify_seq

    def change_asset(self, item_no, item_no_x, item_no_rights, advance_day, advance_month):
        item_tuple = tuple([x for x in [item_no, item_no_x, item_no_rights] if x])
        asset_list = self.db_session.query(Asset).filter(Asset.asset_item_no.in_(item_tuple)).all()
        asset_tran_list = self.db_session.query(AssetTran).filter(
            AssetTran.asset_tran_asset_item_no.in_(item_tuple)).order_by(AssetTran.asset_tran_period).all()
        capital_asset = self.db_session.query(CapitalAsset).filter(
            CapitalAsset.capital_asset_item_no == item_no).first()
        capital_tran_list = self.db_session.query(CapitalTransaction).filter(
            CapitalTransaction.capital_transaction_item_no == item_no).all()
        self.change_asset_due_at(asset_list, asset_tran_list, capital_asset, capital_tran_list, advance_day,
                                 advance_month)
        self.biz_central.change_asset(item_no, item_no_x, item_no_rights, advance_day, advance_month)

    def get_asset_tran_balance_amount_by_period(self, item_no, period_start, period_end):
        asset_tran_list = self.db_session.query(AssetTran).filter(AssetTran.asset_tran_asset_item_no == item_no,
                                                                  AssetTran.asset_tran_period >= period_start,
                                                                  AssetTran.asset_tran_period <= period_end).all()
        return reduce(lambda x, y: x + y.asset_tran_balance_amount, asset_tran_list, 0)

    def get_no_loan(self, item_no):
        item_no_x = ''
        asset_extend = self.db_session.query(AssetExtend).filter(
                AssetExtend.asset_extend_asset_item_no == item_no,
                AssetExtend.asset_extend_type == 'ref_order_no'
            ).first()
        if asset_extend:
            ref_order_type = self.db_session.query(AssetExtend).filter(
                AssetExtend.asset_extend_asset_item_no == item_no,
                AssetExtend.asset_extend_type == 'ref_order_type'
            ).first()
            item_no_x = asset_extend.asset_extend_val if ref_order_type and \
                                                         ref_order_type.asset_extend_val != 'lieyin' else ''
        return item_no_x

    def set_asset_tran_status(self, **kwargs):
        period = kwargs.get('period')
        item_no = kwargs.get('item_no')
        status = kwargs.get('status', 'finish')
        if not period or not item_no:
            raise ValueError('period or item_no can not be none!')
        if status not in ('finish', 'nofinish'):
            raise ValueError('status error, only finish, nofinish!')
        item_no_x = self.get_no_loan(item_no)
        asset_tran_list = self.db_session.query(AssetTran).filter(
            AssetTran.asset_tran_asset_item_no.in_((item_no, item_no_x)), AssetTran.asset_tran_period <= period).all()
        for asset_tran in asset_tran_list:
            asset_tran.asset_tran_balance_amount = 0 if status == 'finish' else asset_tran.asset_tran_amount
            asset_tran.asset_tran_repaid_amount = asset_tran.asset_tran_amount if status == 'finish' else 0
            asset_tran.asset_tran_status = status
            asset_tran.asset_tran_finish_at = get_date() if status == 'finish' else '1000-01-01'
        self.db_session.add_all(asset_tran_list)
        self.db_session.commit()

    @query_withhold
    def active_repay(self, **kwargs):
        if 'item_no' not in kwargs:
            raise ValueError('need item_no, but not found!')
        repay_card = kwargs.pop("repay_card", 1)
        item_no = kwargs.pop("item_no", '')
        item_no_x = self.get_no_loan(item_no) if item_no else ''
        item_no_rights = kwargs.pop("item_no_rights", '')
        if item_no_rights:
            rights_info = self.db_session.query(AssetExtend).filter(
                AssetExtend.asset_extend_asset_item_no == item_no_rights,
                AssetExtend.asset_extend_type == 'ref_order_type',
                AssetExtend.asset_extend_val == 'lieyin').first()
            if not rights_info:
                raise ValueError('The item {0} is not rights asset!'.format(item_no_rights))
        if not item_no and not item_no_rights:
            raise ValueError('need item_no or item_no_rights one is not null!')
        amount = kwargs.pop("amount", 0)
        x_amount = kwargs.pop("x_amount", 0)
        rights_amount = kwargs.pop("rights_amount", 0)
        verify_code = kwargs.pop("verify_code", '')
        verify_seq = kwargs.pop("verify_seq", None)
        agree = kwargs.pop("agree", False)
        period_start = kwargs.pop("period_start", None)
        period_end = kwargs.pop("period_end", None)
        amount = self.__get_repay_amount__(amount, item_no, period_start, period_end)
        x_amount = self.__get_repay_amount__(x_amount, item_no_x, period_start, period_end)
        rights_amount = self.__get_repay_amount__(rights_amount, item_no_rights, period_start, period_end)
        if amount == 0 and x_amount == 0 and rights_amount == 0:
            return "当前已结清", "", [], []
        request_data = self.__get_active_request_data__(item_no, item_no_x, item_no_rights,
                                                        amount, x_amount, rights_amount, repay_card, **kwargs)
        resp = Http.http_post(self.active_repay_url, request_data)
        self.log.log_info("主动代扣发起成功，url:{0},request：{1}，resp：{2}".format(self.active_repay_url,
                                                                         request_data, resp))
        withhold_info = {}
        if resp['code'] == 0 or '正在进行中' in resp['message'] or '有未完成交易，请勿重复提交数据' in resp['message']:
            request_key = request_data['key'] if resp['code'] == 0 else ''
            if item_no:
                withhold_info.update(self.get_withhold_info(item_no, req_key=request_key))
            if item_no_rights:
                withhold_info.update(self.get_withhold_info(item_no_rights, req_key=request_key))
        if resp['code'] == 0 and agree:
            # 协议支付 发短信
            first_serial_no = resp['data']['project_list'][0]['order_no']
            agree_request_data = copy.deepcopy(request_data)
            verify_seq = self.send_msg(first_serial_no) if verify_seq is None else verify_seq
            # 第二次发起
            agree_request_data['key'] = self.__create_req_key__(item_no, prefix='Agree')
            agree_request_data['data']['order_no'] = first_serial_no
            agree_request_data['data']['verify_code'] = verify_code
            agree_request_data['data']['verify_seq'] = verify_seq
            agree_resp = Http.http_post(self.active_repay_url, agree_request_data)
            request_data = [request_data, agree_request_data]
            resp = [resp, agree_resp]
        return request_data, self.active_repay_url, resp, withhold_info

    def __get_repay_amount__(self, amount, item_no, period_start, period_end):
        if amount == 0 and period_start is not None and period_end is not None:
            amount = self.get_asset_tran_balance_amount_by_period(item_no, period_start, period_end)
        return amount

    def __get_active_request_data__(self, item_no, item_no_x, item_no_rights, amount, x_amount, rights_amount,
                                    repay_card, **kwargs):
        card_info = self.get_active_card_info(item_no, repay_card)
        key = self.__create_req_key__(item_no, prefix='Active')
        item_no_priority = kwargs.get("project_num_loan_channel_priority", 12)
        item_no_rights_priority = kwargs.get("project_num_rights_loan_channel_priority", 5)
        item_no_x_priority = kwargs.get("project_num_no_loan_priority", 1)
        coupon_num = kwargs.get("coupon_num", None)
        coupon_amount = kwargs.get("coupon_amount", None)
        order_no = kwargs.get("order_no", "")
        verify_code = kwargs.get("verify_code", "")
        verify_seq = kwargs.get("verify_seq", "")
        active_request_data = {
            "type": "PaydayloanUserActiveRepay",
            "key": key,
            "from_system": "DSQ",
            "data": {
                "total_amount": amount + x_amount + rights_amount,
                "project_list": [],
                "order_no": order_no,
                "verify_code": verify_code,
                "verify_seq": verify_seq
            }
        }
        for four_element_key, four_element_value in self.__get_four_element_key__(repay_card).items():
            active_request_data['data'][four_element_key] = card_info[four_element_value]
        amount_info_list = [(item_no, amount, item_no_priority, None, None),
                            (item_no_rights, rights_amount, item_no_rights_priority, None, None),
                            (item_no_x, x_amount, item_no_x_priority, coupon_num, coupon_amount)]
        amount_info_key = ("project_num", "amount", "priority", "coupon_num", "coupon_amount")
        for amount_info in amount_info_list:
            if amount_info[1] != 0:
                active_request_data['data']['project_list'].append(dict(zip(amount_info_key, amount_info)))
        return active_request_data

    @staticmethod
    def __get_four_element_key__(repay_card):
        repay_key = ('card_num_encrypt', 'card_user_id_encrypt', 'card_user_name_encrypt', 'card_user_phone_encrypt')
        if repay_card == 1:
            card_element = ('card_acc_num_encrypt', 'card_acc_id_num_encrypt', 'card_acc_tel_encrypt',
                            'card_acc_name_encrypt')
        elif repay_card in (0, 2):
            card_element = ('bank_code_encrypt', 'id_number_encrypt', 'user_name_encrypt', 'phone_number_encrypt')
        return dict(zip(repay_key, card_element))

    def get_active_card_info(self, item_no, repay_card):
        # 1-还款卡还款
        card_info = self.get_repay_card_by_item_no(item_no)
        if repay_card in (0, 2):
            # 0-还款人身份证相同银行卡不同;2-还款人身份证和银行卡都不同
            id_num = card_info['card_acc_id_num_encrypt'] if repay_card == 0 else None
            card_info = self.get_four_element(id_num=id_num)['data']
        return card_info

    def get_repay_card_by_item_no(self, item_no):
        sql = "select card_acc_id_num_encrypt, card_acc_num_encrypt, card_acc_tel_encrypt, card_acc_name_encrypt " \
              "from card join card_asset on card_no = card_asset_card_no where " \
              "card_asset_asset_item_no='{0}'and card_asset_type = 'repay'".format(item_no)
        id_num_info = self.db_session.execute(sql)
        return id_num_info[0] if id_num_info else ''

    def get_withhold_info(self, item_no, req_key='', repay_type=''):
        item_no_x = self.get_no_loan(item_no)
        withhold_order_list = self.db_session.query(WithholdOrder).filter(
            WithholdOrder.withhold_order_reference_no.in_((item_no, item_no_x)),
            WithholdOrder.withhold_order_withhold_status == 'ready'
        ).all()
        if repay_type == 'crm_repay':
            withhold_order_list = self.db_session.query(WithholdOrder).filter(
                WithholdOrder.withhold_order_reference_no.in_((item_no, item_no_x)),
                WithholdOrder.withhold_order_withhold_status == 'success',
                WithholdOrder.withhold_order_serial_no.like('%DECREASE%')
            ).order_by(desc(WithholdOrder.withhold_order_create_at)).limit(2).all()
        request_no, serial_no = set([]), set([])
        for withhold_order in withhold_order_list:
            if not req_key or (req_key and withhold_order.withhold_order_req_key == req_key):
                request_no.add(withhold_order.withhold_order_request_no)
                serial_no.add(withhold_order.withhold_order_serial_no)
        id_num_encrypt = self.get_repay_card_by_item_no(item_no)
        return dict(zip(('request_no', 'serial_no', 'id_num'), (list(request_no), list(serial_no), id_num_encrypt)))

    def refresh_late_fee(self, item_no):
        request_data = {
            "from_system": "Biz",
            "type": "RbizRefreshLateInterest",
            "key": self.__create_req_key__(item_no, prefix='Refresh'),
            "data": {
                "asset_item_no": item_no
            }
        }
        resp = Http.http_post(self.refresh_url, request_data)
        return request_data, self.refresh_url, resp

    @staticmethod
    def __create_req_key__(item_no, prefix=''):
        return "{0}{1}_{2}".format(prefix, item_no, int(time.time()))

    def reverse_item_no(self, item_no, serial_no):
        req_data = {
            "from_system": "Biz",
            "key": self.__create_req_key__(item_no, prefix='Reverse'),
            "type": "AssetRepayReverse",
            "data": {
                "asset_item_no": item_no,
                "serial_no": "",
                "operator_name": "dongyuhong",
                "comment": "decrease and repay",
                "fromSystem": "rbiz",
                "send_change_mq": True
            }
        }
        withhold_info = self.db.get_withhold_info_by_serial_no(serial_no)
        req_data['data']['serial_no'] = withhold_info['withhold_channel_key']
        resp = Http.http_post(self.reverse_url, req_data)
        return req_data, self.refresh_url, resp

    @query_withhold
    def crm_repay(self, item_no, amount):
        req_data = {
          "type": "CombineWithholdTaskHandler",
          "key": self.__create_req_key__(item_no, prefix='Crm'),
          "from_system": "DSQ",
          "data": {
            "asset_item_no": item_no,
            "bill_balance_amount": amount,
            "operator": "测试1"
          }
        }
        repay_ret = Http.http_post(self.decrease_url, req_data)
        withhold_info = self.run_crm_task_msg_by_item_no(item_no)
        if '正在进行中' in repay_ret['message']:
            withhold_info = self.get_withhold_info(item_no, repay_type='crm_repay')
        return req_data, self.decrease_url, repay_ret, withhold_info

    @query_withhold
    def repay_callback(self, serial_no, status):
        withhold = self.db_session.query(Withhold).filter(Withhold.withhold_serial_no == serial_no).first()
        if not withhold:
            raise ValueError('代扣记录不存在')
        req_data = {
            "merchant_key": serial_no,
            "channel_name": withhold.withhold_channel if withhold.withhold_channel else 'baofu_4_baidu',
            "channel_key": serial_no,
            "finished_at": self.get_date(is_str=True),
            "transaction_status": status,
            "sign": "6401cd046b5ae44ef208b8ea82d398ab",
            "from_system": "paysvr",
            "channel_message": "交易成功" if status == 2 else '交易失败'
        }
        resp = Http.http_post(self.pay_svr_callback_url, req_data)
        if resp['code'] != 0:
            raise ValueError('执行回调接口失败，返回:{0}'.format(resp))
        self.run_callback_task_and_msg(serial_no, status)
        return req_data, self.pay_svr_callback_url, resp, []

    def run_callback_task_and_msg(self, serial_no, repay_status):
        withhold_order = self.db_session.query(WithholdOrder).filter(
            WithholdOrder.withhold_order_serial_no == serial_no).first()
        request_no, _, id_num_encrypt = self.get_withhold_info(withhold_order.withhold_order_reference_no)
        self.run_task_by_type_and_order_no('withhold_callback_process', withhold_order.withhold_order_reference_no)
        if repay_status == 2:
            # 跑充值还款任务
            self.run_task_by_type_and_order_no('assetWithholdOrderRecharge', serial_no)
        self.run_task_by_type_and_order_no('withhold_order_sync', serial_no)
        self.run_task_by_type_and_order_no('execute_combine_withhold', request_no)
        self.run_msg_by_type_and_order_no('', id_num_encrypt)

    def run_task_by_type_and_order_no(self, task_type, order_no):
        task_list = self.db_session.query(Task).filter(Task.task_type == task_type,
                                                     Task.task_order_no == order_no).all()
        for task in task_list:
            self.run_task_by_id(task.task_id)

    def run_msg_by_type_and_order_no(self, order_no, sendmsg_type=''):
        msg_list = self.db_session.query(SendMsg).filter(SendMsg.sendmsg_type == sendmsg_type,
                                                       SendMsg.sendmsg_order_no == order_no).all()
        for msg in msg_list:
            self.run_msg_by_id(msg.sendmsg_id)

    def run_task_by_order_no(self, order_no, task_type):
        for item_order in order_no:
            task = self.db_session.query(Task).filter(Task.task_order_no == item_order,
                                                      Task.task_type == task_type).first()
            if task:
                req = Http.http_get(self.run_task_id_url.format(task.task_id))
                if req['code'] != 0:
                    return req

    def run_crm_task_msg_by_item_no(self, item_no):
        item_no_x = self.get_no_loan(item_no)
        item_no_x_info = self.db_session.query(Asset).filter(Asset.asset_item_no == item_no_x).first()
        item_no_x_status = item_no_x_info.asset_status if item_no_x_info else ''
        item_list = (item_no, item_no_x) if item_no_x_status == 'repay' else (item_no, )
        serial_no_list, request_no_list = set([]), set([])
        for item in item_list:
            task_info = self.db_session.query(Task).filter(Task.task_order_no == item,
                                                           Task.task_type == 'provisionRecharge',
                                                           Task.task_status == 'open').first()
            if task_info:
                serial_no = json.loads(task_info.task_request_data)['data']['rechargeSerialNo']
                serial_no_list.add(serial_no)
                withhold_order = self.db_session.query(WithholdOrder).filter(
                    WithholdOrder.withhold_order_serial_no == serial_no).first()
                if withhold_order:
                    request_no_list.add(withhold_order.withhold_order_request_no)
                self.run_task_by_id(task_info.task_id)
                self.run_task_by_order_no(serial_no, 'withhold_order_sync')
        id_num_encrypt = self.get_repay_card_by_item_no(item_no)['card_acc_id_num_encrypt']
        return dict(zip(('request_no', 'serial_no', 'id_num'), (list(request_no_list), list(serial_no_list),
                                                                id_num_encrypt)))

    @query_withhold
    def fox_repay(self, **kwargs):
        item_no = kwargs.get('item_no')
        amount = kwargs.get('amount', 0)
        period_start = kwargs.pop("period_start", None)
        period_end = kwargs.pop("period_end", None)
        if amount == 0 and period_start is not None and period_end is not None:
            amount = self.__get_repay_amount__(amount, item_no, period_start, period_end)
        req_key = self.__create_req_key__(item_no, prefix='FOX')
        fox_active_data = {
            "busi_key": "20190731061116179",
            "data": {
              "amount": amount,
              "asset_item_no": item_no,
              "asset_period": None,
              "customer_bank_card_encrypt": "enc_03_2767440037125031936_469",
              "customer_bank_code": "CCB",
              "customer_mobile_encrypt": "enc_01_2764219608117807104_022",
              "manual_user_id_num": None,
              "manual_user_id_num_encrypt": None,
              "manual_user_name": None,
              "manual_user_name_encrypt": None,
              "operator": "zss",
              "serial_no": req_key
            },
            "from_system": "Fox",
            "key": req_key,
            "sync_datetime": None,
            "type": "FoxManualWithhold"
        }
        resp = Http.http_post(self.fox_repay_url, fox_active_data)
        withhold_info = []
        if resp['message'] == '交易处理中' or '正在进行中' in resp['message']:
            req_key = req_key if resp['message'] == '交易处理中' else ''
            withhold_info = self.get_withhold_info(item_no, req_key=req_key)
        return fox_active_data, self.fox_repay_url, resp, withhold_info


if __name__ == "__main__":

    ret = ChinaRepayAuto.cal_months(datetime.date("2021-08-01"), datetime.date("2021-07-31"))
    print(ret)
