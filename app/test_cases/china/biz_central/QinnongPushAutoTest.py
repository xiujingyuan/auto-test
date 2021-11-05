from app.test_cases.china.biz_central import BizCentralTest


class QinnongPushAutoTest(BizCentralTest):

    def prepare_asset(self, case, result):
        # 放款新资产
        self.item_no = self.repay.auto_loan(**case.test_cases_asset)
        # 存入本次使用资产
        result.test_cases_run_info = {'item_no': self.item_no}
        # 修改还款计划状态
        self.repay.set_asset_tran_status(self.item_no, case.test_cases_asset_tran)
        # 修改资方还款计划状态
        self.central.set_capital_tran_status(self.item_no, case.test_cases_capital_tran)

    def repay_asset(self, case, result):
        # 发起代扣并执行成功
        request_data, _, resp = getattr(self.repay, case.test_cases_repay_info)(self.item_no,
                                                                                period_start=None,
                                                                                period_end=None,
                                                                                status=2)
        # 存入本次使用的代扣记录
        result.test_cases_run_info.update({'withhold': request_data})

    def run_interface_scene(self, case):
        """返回测试"""
        pass

    def run_compensate_scene(self, case):
        """代偿场景"""
        pass

    def run_normal_scene(self, case):
        """正常还款场景"""
        # 执行UserRepay任务
        self.central.run_task_by_order_no(self.item_no, task_type='')
        # 执行notify任务 - check capital_notify 时间，类型，期次

        # 捞取推送

        # 检查settlement状态

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
