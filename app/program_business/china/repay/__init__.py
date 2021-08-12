import json
import time

from app.common.db_util import DataBase
from app.common.easy_mock_util import EasyMock
from app.common.http_util import Http
from app.common.nacos_util import Nacos
from app.common.tools import CheckExist
from app.common.xxljob_util import XxlJob
from app.program_business import BaseAuto
from app.program_business.china.grant import ChinaGrantAuto


def query_withhold(func):
    def wrapper(self, **kwargs):
        ret = WITHHOLD_RET
        repay_type = kwargs.pop('repay_type')
        item_no = kwargs['item_no']
        ret['request'], ret['request_url'], ret['response'], ret['withhold_info'] = func(self, **kwargs)
        return ret
    return wrapper


WITHHOLD_RET = {"request": {}, "response": {}, "request_url": ""}


class ChinaRepayNacos(Nacos):
    def __init__(self, env):
        self.program = 'repay'
        super(ChinaRepayNacos, self).__init__('china', ''.join((self.program, env)))

    def update_repay_paysvr_config_by_value(self, value):
        super(ChinaRepayNacos, self).update_configs('repay_paysvr_config', value)


class ChinaRepayXxlJob(XxlJob):
    def __init__(self, env):
        super(ChinaRepayXxlJob, self).__init__('china', 'repay', env)


class RepayEasyMock(EasyMock):
    def __init__(self, check_req, return_req):
        super(RepayEasyMock, self).__init__('rbiz_auto_test', check_req, return_req)


class ChinaRepayDb(DataBase):
    def __init__(self, num, run_env):
        super(ChinaRepayDb, self).__init__('rbiz', num, 'china', run_env)

    def set_asset_tran_finish(self, item_no, item_no_x, period):
        sum_money = "select sum(asset_tran_amount) as amount, asset_tran_asset_item_no from asset_tran where " \
                    "asset_tran_asset_item_no in ('{0}', '{1}') " \
                    "and asset_tran_period < {2} group by asset_tran_asset_item_no order by asset_tran_asset_item_no " \
                    "desc ".format(item_no, item_no_x, period)
        money_repaid_list = self.do_sql(sum_money)
        sum_money = "select sum(asset_tran_amount) as amount, asset_tran_asset_item_no from asset_tran where " \
                    "asset_tran_asset_item_no in ('{0}', '{1}') " \
                    "and asset_tran_period >= {2} group by asset_tran_asset_item_no order by asset_tran_asset_item_no " \
                    "desc ".format(item_no, item_no_x, period)
        money_balance_list = self.do_sql(sum_money)
        for index, money_item in enumerate(money_repaid_list):
            update_sql = "update asset set asset_balance_amount={0},asset_repaid_amount={1} where asset_item_no='{2}" \
                         "'".format(money_balance_list[index]['amount'],
                                    money_item['amount'],
                                    money_item['asset_tran_asset_item_no'])
            self.do_sql(update_sql)
        sql = "update asset_tran set asset_tran_status = 'finish',asset_tran_balance_amount = 0," \
              "asset_tran_repaid_amount = asset_tran_amount, asset_tran_finish_at=now() where " \
              "asset_tran_asset_item_no in (" \
              "'{0}', '{1}') and asset_tran_period < {2}".format(item_no, item_no_x, period)
        self.do_sql(sql)

        sql = "update asset_tran set asset_tran_status = 'nofinish',asset_tran_balance_amount = asset_tran_amount," \
              "asset_tran_repaid_amount = 0, asset_tran_finish_at='1000-01-01 00:00:00' where " \
              "asset_tran_asset_item_no in (" \
              "'{0}', '{1}') and asset_tran_period >= {2}".format(item_no, item_no_x, period)
        self.do_sql(sql)

    def get_no_loan(self, item_no):
        item_extend = self.get_data('asset_extend', asset_extend_asset_item_no=item_no,
                                    asset_extend_type='ref_order_no')
        return item_extend[0]['asset_extend_val'] if item_extend else ''

    @CheckExist(check=True)
    def get_asset_info(self, item_no):
        return self.get_data('asset', asset_item_no=item_no)[0]

    @CheckExist(check=True)
    def get_withhold_info_by_serial_no(self, serial_no):
        return self.get_data('withhold', withhold_serial_no=serial_no)[0]

    def get_asset_tran_balance_amount_by_period(self, item_no, period_start, period_end):
        asset_tran_list = self.get_data("asset_tran", asset_tran_asset_item_no=item_no)
        sum_amount = 0
        for asset_item in asset_tran_list:
            if asset_item["asset_tran_period"] in range(period_start, period_end+1):
                sum_amount += int(asset_item["asset_tran_balance_amount"])
        return sum_amount

    @CheckExist(check=True)
    def get_repay_card_by_item_no(self, item_no):
        sql = "SELECT card.* FROM card_asset INNER JOIN card ON card_no=card_asset_card_no WHERE " \
              "card_asset_asset_item_no='{0}' AND card_asset_type='repay'".format(item_no)
        return self.do_sql(sql)[0]

    @CheckExist(check=True)
    def get_withhold_request_info(self, req_key):
        return self.get_data('withhold_request', withhold_request_req_key=req_key)[0]

    @CheckExist(check=True)
    def get_withhold_serial_no_by_request_no(self, request_no):
        return self.get_data('withhold', withhold_request_no=request_no)

    def get_withhold_serial_no_by_item_no(self, item_no):
        return self.get_data('withhold_order', withhold_order_reference_no=item_no,
                             withhold_order_withhold_status='ready')


class ChinaRepayAuto(BaseAuto):
    def __init__(self, env, run_env, check_req=False, return_req=False):
        super(ChinaRepayAuto, self).__init__('china', 'repay', env, run_env, check_req, return_req)
        self.host_url = "https://kong-api-test.kuainiujinke.com/rbiz{0}".format(env)
        self.grant = ChinaGrantAuto(env, run_env, check_req, return_req)
        self.decrease_url = self.host_url + "/asset/bill/decrease"
        self.active_repay_url = self.host_url + "/paydayloan/repay/combo-active-encrypt"
        self.fox_repay_url = self.host_url + "/fox/manual-withhold-encrypt"
        self.refresh_url = self.host_url + "/asset/refreshLateFee"
        self.pay_ver_callback_url = self.host_url + "/paysvr/callback"
        self.run_task_id_url = self.host_url + '/task/run?taskId={0}'
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

    @query_withhold
    def active_repay(self, **kwargs):
        if 'item_no' not in kwargs:
            raise ValueError('need item_no, but not found!')
        repay_card = kwargs.pop("repay_card", 1)
        item_no = kwargs.pop("item_no")
        amount = kwargs.pop("amount", 0)
        x_amount = kwargs.pop("x_amount", 0)
        period_start = kwargs.pop("period_start", None)
        period_end = kwargs.pop("period_end", None)
        item_no_x = self.db.get_no_loan(item_no)
        amount = self.__get_repay_amount__(amount, item_no, period_start, period_end)
        x_amount = self.__get_repay_amount__(x_amount, item_no_x, period_start, period_end)
        if amount == 0 and x_amount == 0:
            return "当前已结清", "", [], []
        request_data = self.__get_active_request_data__(item_no, item_no_x, amount, x_amount, repay_card, **kwargs)
        resp = Http.http_post(self.active_repay_url, request_data)
        self.log.log_info("主动代扣发起成功，url:{0},request：{1}，resp：{2}".format(self.active_repay_url,
                                                                         request_data, resp))
        withhold_info = []
        if resp['code'] == 0:
            withhold_info = self.get_withhold_info(request_data['key'], item_no)
        elif '正在进行中' in resp['message']:
            withhold_info = self.get_withhold_ready_info(item_no)
        return request_data, self.active_repay_url, resp, withhold_info

    def __get_repay_amount__(self, amount, item_no, period_start, period_end):
        if amount == 0 and period_start is not None and period_end is not None:
            amount = self.db.get_asset_tran_balance_amount_by_period(item_no, period_start, period_end)
        return amount

    def __get_active_request_data__(self, item_no, item_no_x, amount, x_amount, repay_card, **kwargs):
        card_info = self.db.get_repay_card_by_item_no(item_no) if repay_card == 1 \
            else self.get_four_element()['data']
        key = self.__create_req_key__(item_no, prefix='Active')
        item_no_priority = kwargs.get("project_num_loan_channel_priority", 12)
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
                "total_amount": amount + x_amount,
                "project_list": [],
                "order_no": order_no,
                "verify_code": verify_code,
                "verify_seq": verify_seq
            }
        }
        for four_element_key, four_element_value in self.__get_four_element_key__(repay_card).items():
            active_request_data['data'][four_element_key] = card_info[four_element_value]
        amount_info_list = [(item_no, amount, item_no_priority, None, None),
                            (item_no_x, x_amount, item_no_x_priority, coupon_num, coupon_amount)]
        amount_info_key = ("project_num", "amount", "priority", "coupon_num", "coupon_amount")
        for amount_info in amount_info_list:
            if amount_info[1] != 0:
                active_request_data['data']['project_list'].append(dict(zip(amount_info_key, amount_info)))
        return active_request_data

    @staticmethod
    def __get_four_element_key__(repay_card):
        repay_key = ('card_num_encrypt', 'card_user_id_encrypt', 'card_user_name_encrypt', 'card_user_phone_encrypt')
        if repay_card:
            card_element = ('card_acc_num_encrypt', 'card_acc_id_num_encrypt', 'card_acc_tel_encrypt',
                            'card_acc_name_encrypt')
        else:
            card_element = ('bank_code_encrypt', 'id_number_encrypt', 'user_name_encrypt', 'phone_number_encrypt')
        return dict(zip(repay_key, card_element))

    def __get_request_data_by_sync_task__(self, req_key):
        sync_task_info = self.get_sync_task_id_by_task_type(req_key, 'CombineWithholdTaskHandler')
        return json.loads(sync_task_info['synctask_request_data'])

    @CheckExist(check=True)
    def __get_withhold_request_no_by_serial_no__(self, serial_no):
        return self.db.get_data('withhold', withhold_serial_no=serial_no)[0]['withhold_request_no']

    def __get_request_no_by_req_key__(self, req_key):
        return self.db.get_withhold_request_info(req_key)['withhold_request_no']

    def __get_withhold_serial_no_by_req_key__(self, req_key):
        withhold_request_no = self.__get_request_no_by_req_key__(req_key)
        return self.__get_withhold_serial_no_by_request_no__(withhold_request_no)

    def __get_withhold_serial_no_by_request_no__(self, request_no):
        withhold_serial_no_list = self.db.get_withhold_serial_no_by_request_no(request_no)
        return list(map(lambda x: x['withhold_serial_no'], withhold_serial_no_list))

    def get_withhold_info(self, req_key, item_no):
        request_no = self.__get_request_no_by_req_key__(req_key)
        serial_no = self.__get_withhold_serial_no_by_request_no__(request_no)
        id_num_encrypt = self.db.get_repay_card_by_item_no(item_no)['card_acc_id_num_encrypt']
        return dict(zip(('request_no', 'serial_no', 'id_num'), (request_no, serial_no, id_num_encrypt)))

    def get_withhold_ready_info(self, item_no):
        withhold_order = self.db.get_withhold_serial_no_by_item_no(item_no)
        request_no = withhold_order[0]['withhold_order_request_no']
        serial_no = list(map(lambda x: x['withhold_order_serial_no'], withhold_order))
        id_num_encrypt = self.db.get_repay_card_by_item_no(item_no)['card_acc_id_num_encrypt']
        return dict(zip(('request_no', 'serial_no', 'id_num'), (request_no, serial_no, id_num_encrypt)))

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
    def crm_repay(self, **kwargs):
        if 'item_no' not in kwargs:
            raise ValueError('need item_no, but not found!')
        if 'amount' not in kwargs:
            raise ValueError('need amount, but not found!')
        item_no, amount = kwargs['item_no'], kwargs['amount']
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
            withhold_info = self.get_withhold_ready_info(item_no)
        return req_data, self.decrease_url, repay_ret, withhold_info

    @query_withhold
    def repay_callback(self, serial_no, repay_status):
        req_data = {
            "merchant_key": serial_no,
            "channel_name": '',
            "channel_key": serial_no,
            "finished_at": time.time(),
            "transaction_status": repay_status,
            "sign": "6401cd046b5ae44ef208b8ea82d398ab",
            "from_system": "paysvr",
            "channel_message": "交易成功" if repay_status == 2 else '交易失败'
        }
        resp = Http.http_post(self.pay_svr_callback_url, req_data)
        return req_data, self.pay_svr_callback_url, resp

    def run_crm_task_msg_by_item_no(self, item_no):
        item_no_x = self.db.get_no_loan(item_no)
        item_no_x_status = self.db.get_asset_info(item_no_x)['asset_status'] if item_no_x else []
        item_list = (item_no, item_no_x) if item_no_x_status == 'repay' else (item_no, )
        serial_no_list, request_no_list = [], []
        for item in item_list:
            task_info = self.get_task_info_by_task_type(item, 'provisionRecharge', timeout=1)
            if task_info:
                serial_no = json.loads(task_info[0]['task_request_data'])['data']['rechargeSerialNo']
                serial_no_list.append(serial_no)
                request_no = self.__get_withhold_request_no_by_serial_no__(serial_no)
                request_no_list.append(request_no)
                self.run_task_by_id(task_info[0]['task_id'])
                self.run_task_by_order_no(serial_no, 'withhold_order_sync')
        id_num_encrypt = self.db.get_repay_card_by_item_no(item_no)['card_acc_id_num_encrypt']
        return dict(zip(('request_no', 'serial_no', 'id_num'), (request_no_list, serial_no_list, id_num_encrypt)))

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
        if resp['message'] == '交易处理中':
            withhold_info = self.get_withhold_info(req_key, item_no)
        elif '正在进行中' in resp['message']:
            withhold_info = self.get_withhold_ready_info(item_no)
        return fox_active_data, self.fox_repay_url, resp, withhold_info
