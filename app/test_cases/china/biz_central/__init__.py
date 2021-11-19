import json
import math
from datetime import datetime
import pandas as pd

from app.common.assert_util import Assert
from app.services.china.biz_central.services import ChinaBizCentralService
from app.services.china.repay.services import ChinaRepayService
from app.test_cases import BaseAutoTest, run_case_prepare, CaseException


class BizCentralTest(BaseAutoTest):

    def __init__(self, env, environment):
        super().__init__(env, environment)
        self.central = ChinaBizCentralService(env, environment)
        self.repay = ChinaRepayService(env, environment)
        self.repay_info = None
        self.channel = 'qinnong'

    @classmethod
    def add_work_days(cls, date, days):
        if isinstance(date, datetime.date):
            raise TypeError('need date type')
        if days == 0:
            return date
        direct = days / math.abs(days)
        days = math.abs(days)
        while days:
            date = cls.get_date(date, days=direct, fmt='%Y-%m-%d 00:00:00', is_str=True)
            if cls.is_work_day(date):
                days -= 1
        return date

    def is_work_day(self, date):
        holiday = self.central.get_date_is_holiday(date)
        if holiday is not None:
            return holiday
        return self.is_week_day(date)

    @staticmethod
    def is_week_day(date):
        if date.isoweekday() in (6, 7):
            return True
        return False

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

    def get_real_plan_at(self, plan_at, plan_period_start):
        ret_plan_at = ''
        plan_at_list = plan_at.split("+")
        if len(plan_at_list) < 3:
            plan_at_base, plan_at_type, plan_at_day = plan_at_list[0], plan_at_list[1], 0
        else:
            plan_at_base, plan_at_type, plan_at_day = plan_at_list[0], plan_at_list[1], int(plan_at_list[2])
        if plan_at_base.lower() == 'push':
            ret_plan_at = self.get_date()
        elif plan_at_base.lower() == 'user':
            ret_plan_at = self.central.get_capital_principal(self.item_no, plan_period_start)\
                .capital_transaction_expect_finished_at
        elif plan_at_base.lower() == 'due_at':
            ret_plan_at = self.central.get_capital_principal(self.item_no, plan_period_start)\
                .capital_transaction_user_repay_at
        if plan_at_type.upper() == "T":
            ret_plan_at = self.add_work_days(ret_plan_at, plan_at_day)
        elif plan_at_type.upper() == 'D':
            ret_plan_at = self.get_date(date=ret_plan_at, days=plan_at_day, is_str=True)
        return ret_plan_at

    def check_interface(self):
        # 检查资方推送
        pass

    def check_settlement(self):
        # 检查settlement状态
        pass

    def check_capital_notify(self, check_capital_notify, item_no):
        # 检查生成新的推送
        capital_notify = self.central.get_capital_notify_info(item_no)
        if len(capital_notify) > 1:
            raise CaseException('only one record, but found two!')
        check_key = list(check_capital_notify.keys())
        df_actual_capital_notify = pd.DataFrame.from_records(data=[capital_notify[0].to_spec_dict], columns=check_key)
        df_expect_capital_notify = pd.DataFrame.from_records([check_capital_notify])
        pd_con = df_expect_capital_notify.compare(df_actual_capital_notify,
                                                  align_axis=0)\
            .rename(index={'self': '期望值', 'other': '实际值'}, level=-1)
        if not pd_con.empty:
            raise CaseException("the notify check fail with result is: \r\n{0} ".format(pd_con))

    def prepare_mock(self, withhold_channel):
        pass

    def prepare_kv(self, case, mock_name):
        if not self.channel == case.test_cases_channel:
            raise CaseException("the case channel is error!")
        channel_config = self.central.get_kv(self.channel)
        self.central.check_and_add_push_channel(case.test_cases_channel)
        if 'compensate_config' not in channel_config or 'push_guarantee_config' not in channel_config:
            raise CaseException("config is not new config!")
        service_url = self.central.get_system_url()
        if 'gate{0}.k8s-ingress-nginx.kuainiujinke.com'.format(self.env) in service_url:
            self.central.update_service_url(mock_name)
            raise CaseException("the gate config is error,need mock!")

    def repay_asset(self, case):
        self.repay_info = json.loads(case.test_cases_repay_info)
        repay_period_start = self.repay_info['period_start']
        repay_period_end = self.repay_info['period_end']
        before_capital_tran_type = self.repay_info['before_capital_tran_type']
        capital_notify = self.repay_info['capital_notify']
        mock_name = self.repay_info['mock_name']
        withhold_channel = self.repay_info['withhold_channel']
        repay_type = self.repay_info['repay_type']
        # 修改还款计划状态
        self.repay.set_asset_tran_status(repay_period_start, self.item_no)
        # 修改资方还款计划状态
        self.central.set_capital_tran_status(self.item_no, repay_period_start, before_capital_tran_type,
                                             capital_notify)
        # 还款准备-mock
        self.prepare_mock(withhold_channel)
        # 还款准备-kv
        self.prepare_kv(case, mock_name)
        # 调整还款计划日期
        self.repay.change_asset(self.item_no, '', 0, -repay_period_start)
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
