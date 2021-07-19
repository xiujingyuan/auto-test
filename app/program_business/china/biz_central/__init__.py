from app.common.db_util import DataBase
from app.common.easy_mock_util import EasyMock
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


class ChinaBizCentralAuto(BaseAuto):
    def __init__(self, env, run_env, check_req=False, return_req=False):
        super(ChinaBizCentralAuto, self).__init__('china', 'biz', env, run_env, check_req, return_req)
