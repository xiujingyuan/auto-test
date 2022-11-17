import json
from datetime import datetime

from app.test_cases import CaseException
from app.test_cases.china.central import BizCentralTest


class YuminzhongbaoCentralAutoTest(BizCentralTest):
    
    def __init__(self, env, environment, mock_name):
        super(YuminzhongbaoCentralAutoTest, self).__init__(env, environment, mock_name)

    def modify_plan_at(self, plan_at):
        plan_at = datetime.strptime(plan_at, "%Y-%m-%d %H:%M:%S")
        channel_config = self.central.get_kv(self.channel)
        push_begin = channel_config['push_time']['push_time_start']
        push_end = channel_config['push_time']['push_time_end']
        config_push_begin = "{0} {1}".format(self.get_date(fmt="%Y-%m-%d", is_str=True), push_begin)
        config_push_begin = datetime.strptime(config_push_begin, "%Y-%m-%d %H:%M:%S")
        config_push_end = "{0} {1}".format(self.get_date(fmt="%Y-%m-%d", is_str=True), push_end)
        config_push_end = datetime.strptime(config_push_end, "%Y-%m-%d %H:%M:%S")
        if (plan_at - config_push_begin).days < 0:
            return config_push_begin
        elif (plan_at - config_push_end).days <= 0:
            return plan_at
        else:
            return self.get_date(date=config_push_begin, days=1)

    def prepare_mock(self, channel):
        # 秦农肯定走我方
        pass

    def run_interface_scene(self, case):
        """返回测试"""
        pass

    def check_settlement_repay(self, case):
        super(YuminzhongbaoCentralAutoTest, self).check_settlement_repay(case)
        pass

    @staticmethod
    def is_principal_finish(task_data):
        for repay in task_data['repays']:
            if repay['tran_type'] == 'repayprincipal':
                return True if repay['status'] == 'finish' else False
        return False

    # def run_normal_scene(self, case):
    #     """正常还款场景"""
    #     pass
    #
    # def run_advance_scene(self, case):
    #     """提前还款场景"""
    #     pass
    #
    # def run_early_settlement_scene(self, case):
    #     """逾期还款场景"""
    #     pass
    #
    # def run_overdue_scene(self, case):
    #     """逾期还款场景"""
    #     pass
    #
    # def run_buyback_scene(self, case):
    #     """回购场景"""
    #     pass
    #
    # def run_grace_scene(self, case):
    #     """宽限期还款场景"""
    #     pass
    #
    # def run_compensate_scene(self, case):
    #     """代偿场景"""
    #     pass
