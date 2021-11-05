from app import BizCentralFactory, RepayFactory


class BizCentralTest(object):

    def __init__(self, country, env, environment):
        self.country = country
        self.env = env
        self.environment = environment
        self.central = BizCentralFactory(country, env, environment)
        self.repay = RepayFactory(country, env, environment)

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
        pass

    def set_case_fail(self, case, reason):
        pass

    def run_single_case(self, case):
        self.prepare_asset(case)
        self.prepare_mock(case)
        self.prepare_kv(case)
        getattr(self, 'run_{0}'.format(case.case_scene))(case)
        # self.run_bussiness_logic(case)

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
