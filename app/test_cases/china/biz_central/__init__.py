import json
from app.services.china.biz_central.services import ChinaBizCentralService
from app.services.china.repay.services import ChinaRepayService
from app.test_cases import BaseAutoTest, run_case_prepare


class BizCentralTest(BaseAutoTest):

    def __init__(self, env, environment):
        super().__init__(env, environment)
        self.central = ChinaBizCentralService(env, environment)
        self.repay = ChinaRepayService(env, environment)

    def prepare_asset(self, case):
        # 放款新资产
        self.item_no = self.repay.auto_loan(**(json.loads(case.test_cases_asset_info)))
        # 存入本次使用资产
        self.run_case_log.run_case_log_case_run_item_no = self.item_no

    @run_case_prepare
    def run_single_case(self, case):
        # 资产准备
        self.prepare_asset(case)
        # 还款
        self.repay_asset(case)
        # 执行本次业务逻辑
        getattr(self, 'run_{0}_scene'.format(case.test_cases_scene))(case)
        # 检查资方推送
        self.check_interface()
        # 检查settlement状态
        self.check_settlement()
        # 检查生成新的推送
        self.check_capital_notify()

    def check_interface(self):
        # 检查资方推送
        pass

    def check_settlement(self):
        # 检查settlement状态
        pass

    def check_capital_notify(self):
        # 检查生成新的推送
        pass

    def prepare_mock(self, case):
        pass

    def prepare_kv(self, case):
        pass

    def repay_asset(self, case):
        repay_info = json.loads(case.test_cases_repay_info)
        repay_period_start = repay_info['period_start']
        repay_period_end = repay_info['period_end']
        before_capital_tran_type = repay_info['before_capital_tran_type']
        capital_notify = repay_info['capital_notify']
        channel = repay_info['channel']
        repay_type = repay_info['repay_type']
        # 修改还款计划状态
        self.repay.set_asset_tran_status(repay_period_start, self.item_no)
        # 修改资方还款计划状态
        self.central.set_capital_tran_status(self.item_no, repay_period_start, before_capital_tran_type,
                                             capital_notify)
        # 还款准备-mock
        self.prepare_mock(channel)
        # 还款准备-kv
        self.prepare_kv(case)
        # 发起代扣并执行成功
        resp = getattr(self.repay, repay_type)(item_no=self.item_no, period_start=repay_period_start,
                                               period_end=repay_period_end,
                                               status=2)
        # 存入本次使用的代扣记录
        order_no_list = []
        for withhold in resp['response']['data']['project_list']:
            order_no_list.append(withhold['order_no'])
        self.run_case_log.run_case_log_case_run_withhold_no = json.dumps(order_no_list)

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
