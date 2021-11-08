from app.services.china.biz_central.services import ChinaBizCentralService
from app.services.china.repay.services import ChinaRepayService


class BizCentralTest(object):

    def __init__(self, env, environment):
        self.env = env
        self.environment = environment
        self.central = ChinaBizCentralService(env, environment)
        self.repay = ChinaRepayService(env, environment)
        self.item_no = None
        self.run_case_log = None

    def prepare_asset(self, case):
        # 放款新资产
        self.item_no = self.repay.auto_loan(**case.test_cases_asset_info)
        # 存入本次使用资产
        self.run_case_log.test_cases_run_info = {'item_no': self.item_no}
        # 修改还款计划状态
        self.repay.set_asset_tran_status(self.item_no, case.test_cases_asset_tran)
        # 修改资方还款计划状态
        self.central.set_capital_tran_status(self.item_no, case.test_cases_capital_tran)

    def check_interface(self):
        # 检查资方推送
        pass

    def check_settlement(self):
        # 检查settlement状态
        pass

    def check_capital_notify(self):
        # 检查生成新的推送
        pass

    def repay_asset(self, case):
        # 发起代扣并执行成功
        request_data, _, resp = getattr(self.repay, case.test_cases_repay_info)(self.item_no,
                                                                                period_start=None,
                                                                                period_end=None,
                                                                                status=2)
        # 存入本次使用的代扣记录
        self.run_case_log.test_cases_run_info.update({'withhold': request_data})

    def get_case_list(self, case_id_list, case_group, case_scene):
        cases = []
        return cases

    def run_cases(self, case_id_list, case_group, case_scene):
        cases = self.get_case_list(case_id_list, case_group, case_scene)
        for case in cases:
            try:
                self.run_single_case(case)
                self.set_case_success(case)
            except Exception as e:
                self.set_case_fail(case, str(e))
                continue

    def set_case_success(self, case):
        self.run_case_log.run_case_log_case_run_result = 'success'

    def set_case_fail(self, case, reason):
        self.run_case_log.run_case_log_case_run_result = 'fail'

    def run_single_case(self, case):
        self.prepare_asset(case)
        self.prepare_mock(case)
        self.prepare_kv(case)
        self.repay_asset(case)
        getattr(self, 'run_{0}'.format(case.case_scene))(case)

    def run_interface_scene(self, case):
        """接口请求/返回测试"""
        pass

    def run_compensate_scene(self, case):
        """代偿场景"""
        pass

    def run_normal_scene(self, case):
        """正常还款场景"""
        pass

    def run_advance_scene(self, case):
        """提前还款场景"""
        pass

    def run_early_settlement_scene(self, case):
        """逾期还款场景"""
        pass

    def run_overdue_scene(self, case):
        """逾期还款场景"""
        pass

    def run_buyback_scene(self, case):
        """回购场景"""
        pass

    def run_grace_scene(self, case):
        """宽限期还款场景"""
        pass
