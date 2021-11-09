from app import db
from app.services.china.biz_central.services import ChinaBizCentralService
from app.services.china.repay.services import ChinaRepayService
from app.model.Model import TestCase, RunCaseLog


class BizCentralTest(object):

    def __init__(self, env, environment):
        self.env = env
        self.environment = environment
        self.central = ChinaBizCentralService(env, environment)
        self.repay = ChinaRepayService(env, environment)
        self.item_no = None
        self.run_case_log = RunCaseLog()

    def prepare_asset(self, case):
        # 放款新资产
        self.item_no = self.repay.auto_loan(**case.test_cases_asset_info)
        # 存入本次使用资产
        self.run_case_log.run_case_log_case_run_item_no = self.item_no
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

    @staticmethod
    def get_case_list(case_id_list, case_group, case_scene):
        cases = []
        if case_id_list:
            cases = TestCase.query.filter(TestCase.in_(tuple(case_id_list))).all()
        elif case_group:
            cases = TestCase.query.filter(TestCase.test_cases_group == case_group).all()
        elif case_scene:
            cases = TestCase.query.filter(TestCase.test_cases_scene == case_scene).all()
        return cases

    def run_cases(self, case_id_list, case_group, case_scene):
        cases = self.get_case_list(case_id_list, case_group, case_scene)
        for case in cases:
            try:
                self.run_single_case(case)
                self.set_case_success()
            except Exception as e:
                self.set_case_fail(str(e))
                continue
            finally:
                self.run_case_log = RunCaseLog()

    def set_case_success(self):
        self.run_case_log.run_case_log_case_run_result = 'success'
        db.session.add(self)
        db.session.flush()

    def set_case_fail(self, error_message):
        self.run_case_log.run_case_log_case_run_result = 'fail'
        self.run_case_log.run_case_log_case_run_result = error_message
        db.session.add(self.run_case_log)
        db.session.flush()

    def run_single_case(self, case):
        # 资产准备
        self.prepare_asset(case)
        # 还款准备-mock
        self.prepare_mock(case)
        # 还款准备-kv
        self.prepare_kv(case)
        # 还款
        self.repay_asset(case)
        # 执行本次逻辑
        getattr(self, 'run_{0}'.format(case.case_scene))(case)
        # 检查资方推送
        self.check_interface()
        # 检查settlement状态
        self.check_settlement()
        # 检查生成新的推送
        self.check_capital_notify()

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
        """提前结清场景"""
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
