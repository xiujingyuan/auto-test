from datetime import time

from app.common.db_util import DataBase
from app.common.easy_mock_util import EasyMock
from app.common.nacos_util import Nacos
from app.common.xxljob_util import XxlJob
from app.program_business import BaseAuto


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
        sql = "update asset_tran set asset_tran_status = 'finish',asset_tran_balance_amount =0," \
              "asset_tran_repaid_amount = asset_tran_amount where asset_tran_asset_item_no in (" \
              "'{0}', '{1}') and asset_tran_period < {2}".format(item_no, item_no_x, period)
        self.do_sql(sql)

    def get_no_loan(self, item_no):
        return self.get_data('asset_extend', asset_extend_asset_item_no=item_no,
                             asset_extend_type='ref_order_no')[0]['asset_extend_val']


class ChinaRepayAuto(BaseAuto):
    def __init__(self, env, run_env, check_req=False, return_req=False):
        super(ChinaRepayAuto, self).__init__('china', 'rbiz', env, run_env, check_req, return_req)

    def auto_loan(self, loan_channel, count):
        self.log.log_info("rbiz_loan_tool_auto_import...env=%s, channel_name=%s" % (self.env, loan_channel))
        four_element = self.get_four_element()
        try:
            item_no, item_no_noloan = self.asset_import_and_loan_to_success(loan_channel, four_element, count=count)
            self.log.log_info("大单资产编号：%s" % item_no)
            self.log.log_info("小单资产编号：%s" % item_no_noloan)
        except Exception as e:
            item_no, item_no_noloan = '', ''
            self.log.log_info("%s, 资产生成失败：%s" % (item_no, e))
            return 1, "资产生成失败：%s" % e
        else:
            return item_no, item_no_noloan
