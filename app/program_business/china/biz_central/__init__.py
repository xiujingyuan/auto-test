import json

from app.common.db_util import DataBase
from app.common.easy_mock_util import EasyMock
from app.common.http_util import Http
from app.common.nacos_util import Nacos
from app.common.xxljob_util import XxlJob
from app.program_business import BaseAuto

class ChinaBizCentralNacos(Nacos):
    def __init__(self, env):
        self.program = 'biz-central'
        super(ChinaBizCentralNacos, self).__init__('china', ''.join((self.program, env)))

    def update_repay_paysvr_config_by_value(self, value):
        super(ChinaBizCentralNacos, self).update_configs('repay_paysvr_config', value)


class RepayEasyMock(EasyMock):
    def __init__(self, check_req, return_req):
        super(RepayEasyMock, self).__init__('rbiz_auto_test', check_req, return_req)


class ChinaBizCentralXxlJob(XxlJob):
    def __init__(self, env):
        super(ChinaBizCentralXxlJob, self).__init__('china', 'biz-central', env)


class ChinaBizDb(DataBase):
    def __init__(self, num, run_env):
        super(ChinaBizDb, self).__init__('biz', num, 'china', run_env)

    def set_capital_transaction_operation_type(self, item_no, period, operation_type):
        sql = "update capital_transaction set capital_transaction_repaid_amount = capital_transaction_amount, \
        capital_transaction_status = 'finished', capital_transaction_operation_type ='{2}', \
        capital_transaction_withhold_result_channel = 'qsq' where \
        capital_transaction_asset_item_no = '{0}' and capital_transaction_period < {1}".format(item_no,
                                                                                               period,
                                                                                               operation_type)
        self.do_sql(sql)

    def sync_withhold_to_history(self, item_no):
        sql = "INSERT INTO withhold_history ( withhold_result_id, withhold_result_asset_id, " \
              "withhold_result_asset_item_no, withhold_result_asset_type, withhold_result_asset_period, " \
              "withhold_result_amount, withhold_result_type, withhold_result_status, withhold_result_channel, " \
              "withhold_result_serial_no, withhold_result_create_at, withhold_result_channel_key, " \
              "withhold_result_channel_fee, withhold_result_finish_at, withhold_history_sync_at, " \
              "withhold_result_user_name_encrypt, withhold_result_user_phone_encrypt, " \
              "withhold_result_user_id_card_encrypt, withhold_result_user_bank_card_encrypt)" \
              "SELECT  withhold_result_id, withhold_result_asset_id, withhold_result_asset_item_no," \
              " withhold_result_asset_type, withhold_result_asset_period, withhold_result_amount, " \
              "withhold_result_type, withhold_result_status, withhold_result_channel, withhold_result_serial_no, " \
              "withhold_result_create_at, withhold_result_channel_key, withhold_result_channel_fee, " \
              "withhold_result_finish_at, now(), withhold_result_user_name_encrypt, " \
              "withhold_result_user_phone_encrypt, withhold_result_user_id_card_encrypt, " \
              "withhold_result_user_bank_card_encrypt FROM withhold_result " \
              "WHERE withhold_result_asset_item_no IN ('{0}')".format(item_no)
        self.do_sql(sql)

    def reset_central_task(self, task_id):
        sql = "update central_task set task_next_run_at = now(), task_status = 'open'," \
              " task_version =0, task_retrytimes =0 where task_id = {0}".format(task_id)
        self.do_sql(sql)

    def add_re_push_dcs_task(self, item_no, period_start, period_end):
        req = {
                "item_no": item_no,
                "period_start": period_start,
                "period_end": period_end
               }
        sql = "insert into central_task (task_type, task_order_no, task_key, task_memo, task_status, task_version, " \
              "task_priority, task_request_data, task_response_data, task_retrytimes) values ('RepushToClearing', " \
              "'{0}', '', '', 'open', 0, 1, '{1}', '', 0)".format(item_no, json.dumps(req))
        return self.do_sql(sql, last_id=True)

    def get_send_msg_by_type(self, send_msg_type):
        return self.get_data('central_sendmsg', sendmsg_type=send_msg_type, order_by='sendmsg_id')

    def get_item_info(self, item_no):
        return self.get_data('asset', asset_item_no=item_no)


class ChinaBizCentralAuto(BaseAuto):
    url_host = "http://biz-central-{0}.k8s-ingress-nginx.kuainiujinke.com"

    def __init__(self, env, run_env, check_req=False, return_req=False):
        super(ChinaBizCentralAuto, self).__init__('china', 'biz-central', env, run_env, check_req, return_req)
        self.url_host = self.url_host.format(env)
        self.db = ChinaBizDb(env, run_env)

    def exec_central_task_by_task_id(self, task_id):
        exec_central_task_url = "{0}/job/runTaskById?id={1}".format(self.url_host, task_id)
        Http.http_get(exec_central_task_url)
        return True

    @staticmethod
    def get_item_no(msg):
        msg_list = msg['sendmsg_order_no'].replace('early_settlement', 'earlysettlement').split("_")
        if msg_list[0] not in ('normal', 'advance', 'overdue', 'compensate', 'earlysettlement', 'offline', 'buyback',
                               'chargeback'):
            item_no = "_".join(msg_list[0:-3]) if len(msg_list) > 4 else msg_list[0]
            msg_type = msg_list[-3]
        else:
            item_no = "_".join(msg_list[1:-2]) if len(msg_list) > 4 else msg_list[1]
            msg_type = msg_list[0]
        return item_no, msg_type, msg_list[-2], msg_list[-1]

    def create_push_dcs_task(self):
        all_msg = self.db.get_send_msg_by_type('CapitalTransactionClearing')
        old_data = {}
        max_msg_id = 0
        for index, msg in enumerate(all_msg):
            if index == 0:
                max_msg_id = int(msg['sendmsg_id'])
            item_no, msg_type, start_period, end_period = self.get_item_no(msg)
            old_data["_".join((item_no, msg_type.replace('early_settlement', 'earlysettlement'),
                               start_period, end_period))] = msg['sendmsg_content']
            task_id = self.db.add_re_push_dcs_task(item_no, start_period, end_period)
            if task_id is None:
                raise ValueError('task id is error!')
            self.exec_central_task_by_task_id(task_id)
        all_new_msg = self.db.get_send_msg_by_type('CapitalTransactionClearing')
        for msg in all_new_msg:
            if int(msg['sendmsg_id']) < max_msg_id:
                continue
            item_no, msg_type, start_period, end_period = self.get_item_no(msg)
            msg_key = msg['sendmsg_order_no'] if msg['sendmsg_order_no'] in old_data \
                else "_".join((msg_type.replace('early_settlement', 'earlysettlement'), item_no,
                               start_period,
                               end_period))
            if msg_key in old_data:
                item_info = self.db.get_item_info(item_no)
                if item_info:
                    asset_loan_channel = item_info[0]['asset_loan_channel']
                    print(msg_key, asset_loan_channel,
                          self.compare_data(123, json.loads(old_data[msg['sendmsg_order_no']]),
                                            json.loads(msg['sendmsg_content']), [], 0))
                else:
                    print('not fount the item {0}'.format(item_no))
            else:
                print('not fount the order no {0}'.format(msg['sendmsg_order_no']))


