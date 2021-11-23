import json
from datetime import datetime

from app.test_cases import CaseException
from app.test_cases.china.biz_central import BizCentralTest


class QinnongCentralAutoTest(BizCentralTest):

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

    def run_compensate_scene(self, case):
        """代偿场景"""
        pass

    def run_normal_scene(self, case):
        """正常还款场景"""
        # 执行UserRepay任务
        # 先检查代扣结果任务是否已经执行成功
        user_repay_task = self.central.get_central_task_info(self.item_no, task_type='UserRepay')
        if user_repay_task is None:
            raise CaseException("not found the UserRepay task!")
        serial_no = json.loads(user_repay_task.task_request_data)['data']['recharges'][0]['serial_no']
        self.central.run_central_task_by_order_no(serial_no, task_type='WithholdResultImport', status='close')
        self.central.run_central_task_by_order_no(self.item_no, task_type='UserRepay')
        # 检查capital_tran
        self.check_settlement_repay(case)
        # 执行notify任务
        self.run_capital_notify_task()
        # check capital_notify 时间，类型，期次
        except_capital_notify = json.loads(case.test_cases_check_capital_notify)
        real_plan_at = self.get_real_plan_at(except_capital_notify['plan_at'], except_capital_notify['period_start'])
        real_plan_at = self.modify_plan_at(real_plan_at)
        except_capital_notify['plan_at'] = real_plan_at.strftime("%Y-%m-%d %H:%M:00")
        except_capital_notify['asset_item_no'] = self.item_no
        self.check_capital_notify(except_capital_notify, self.item_no)
        # 捞取推送
        self.run_capital_push(real_plan_at.strftime("%Y-%m-%d"))
        self.central.run_central_task_by_order_no(self.item_no, task_type='QinnongCapitalPush')
        # 检查资方推送
        self.check_interface()
        # 检查settlement状态
        self.check_settlement(case)
        # 检查生成新的推送
        self.check_capital_notify_exist()

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
