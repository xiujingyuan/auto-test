from app.test_cases.china.biz_central import BizCentralTest


class QinnongCentralAutoTest(BizCentralTest):

    def run_interface_scene(self, case):
        """返回测试"""
        pass

    def run_compensate_scene(self, case):
        """代偿场景"""
        pass

    def run_normal_scene(self, case):
        """正常还款场景"""
        # 执行UserRepay任务
        self.central.run_task_by_order_no(self.item_no, task_type='UserRepay')
        # 执行notify任务
        self.central.run_task_by_order_no(self.item_no, task_type='GenerateCapitalNotify')
        # check capital_notify 时间，类型，期次
        capital_plan_at = self.check_capital_notify()
        # 捞取推送
        self.central.run_capital_push(capital_plan_at)
        self.central.run_task_by_order_no(self.item_no, task_type='QinnongCapitalPush')

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
