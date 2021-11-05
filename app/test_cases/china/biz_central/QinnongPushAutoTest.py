from app.test_cases.china.biz_central import BizCentralTest


class QinnongPushAutoTest(BizCentralTest):

    def prepare_asset(self, case):
        item_no = self.repay.auto_loan(**case.test_cases_asset)
        self.repay.set_asset_tran_status(item_no)
        self.central.set_capital_tran_status(item_no)


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
