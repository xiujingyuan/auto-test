import json
import math
from datetime import datetime
import pandas as pd

from app.common.assert_util import Assert
from app.services import wait_timeout
from app.services.china.biz_central.service import ChinaBizCentralService
from app.services.china.repay.service import ChinaRepayService
from app.test_cases import BaseAutoTest, run_case_prepare, CaseException


class BizCentralTest(BaseAutoTest):

    def __init__(self, env, environment):
        super().__init__(env, environment)
        self.central = ChinaBizCentralService(env, environment)
        self.repay = ChinaRepayService(env, environment)
        self.repay_info = None
        self.x_item_no = None
        self.capital_notify_id = None
        self.serial_no = None
        self.channel = 'qinnong'
        self.repay_period_start = None
        self.repay_period_end = None
        self.serial_no_asset = None

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
        self.item_no, self.x_item_no = self.repay.auto_loan(**(json.loads(case.test_cases_asset_info)))
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

    def get_real_amount(self, amount_type):
        amount = {}
        if amount_type == 'withhold':
            withhold_detail = self.repay.get_withhold_detail(self.serial_no,
                                                             max_create_at=self.get_date(fmt='%Y-%m-%d', is_str=True))
            for withhold in withhold_detail['withhold_detail']:
                amount[withhold['asset_tran_type'].replace("repay", "")] = withhold['withhold_amount']
        return amount

    def get_expect_settlement_repay(self, finish_time):
        ret = []
        now = self.get_date(fmt='%Y-%m-%d', is_str=True)
        withhold_detail_list = self.repay.get_withhold_detail(self.serial_no,
                                                              max_create_at=now)
        for withhold_detail in withhold_detail_list:
            withhold = self.repay.get_withhold(withhold_detail['serial_no'], max_create_at=now)['withhold']
            ret.append(dict(zip(('user_repay_at', 'amount', 'repaid_amount', 'withhold_result_channel'),
                                (finish_time, withhold_detail['withhold_amount'], withhold_detail['withhold_amount'],
                                 withhold['channel']))))

    def check_interface(self):
        # 检查资方推送
        pass

    def check_settlement_repay(self, except_capital_tran, serial_no):
        """
        落库时检查capital_tran
        :param except_capital_tran:
        :param serial_no:
        :return:
        """
        withhold = self.repay.get_withhold(serial_no, record_type='obj')
        repay_time = withhold.withhold_finish_at
        channel = withhold.withhold_channel
        channel = channel if channel == self.channel else 'qsq'
        amount_key = []
        for except_item in except_capital_tran:
            except_item['withhold_result_channel'] = channel
            except_item['user_repay_time'] = repay_time
            except_item['repaid_amount'] = except_item['total_repaid_amount']
            except_item['amount'] = except_item['total_repaid_amount']
            amount_key.append(except_item['tran_type'])
        actual_capital_tran = self.central.get_capital_tran_info(self.item_no,
                                                                 self.repay_period_start,
                                                                 'grant',
                                                                 'unfinished',
                                                                 amount_key)

    def check_settlement(self, case):
        # 推送后检查settlement状态
        # {
        #     "expect_finished_at": "push+D",
        #     "expect_operate_at": "push+D",
        #     "actual_operate_at": "push+D",
        #     "operation_type": "normal",
        #     "status": "finished",
        #     "amount": "withhold",
        #     "type": ["principal", "interest"]
        # }
        except_capital_tran = json.loads(case.test_cases_check_capital_tran)
        except_capital_tran_key = list(except_capital_tran.keys())
        except_capital_tran['expect_finished_at'] = self.get_real_plan_at(except_capital_tran['expect_finished_at'],
                                                                          self.repay_period_start)
        except_capital_tran['expect_operate_at'] = self.get_real_plan_at(except_capital_tran['expect_operate_at'],
                                                                         self.repay_period_start)
        except_capital_tran['actual_operate_at'] = self.get_real_plan_at(except_capital_tran['actual_operate_at'],
                                                                         self.repay_period_start)
        amount = self.get_real_amount(except_capital_tran['amount'])
        except_capital_tran_list = []
        for item in except_capital_tran['type']:
            item_dict = {}
            for key in except_capital_tran_key:
                if key == 'type':
                    item_dict[key] = item
                elif key == 'amount':
                    item_dict[key] = amount[item]
                else:
                    item_dict[key] = except_capital_tran[key]
            except_capital_tran_list.append(item_dict)
        actual_capital_tran = self.central.get_capital_tran_info(self.item_no,
                                                                 self.repay_period_start,
                                                                 except_capital_tran['operation_type'],
                                                                 except_capital_tran['status'],
                                                                 tuple(except_capital_tran['type']))
        if not actual_capital_tran:
            raise CaseException('not found the expect capital tran!')
        actual_period = set(map(lambda x: x.capital_transaction_period, actual_capital_tran))
        if max(actual_period) > self.repay_period_end:
            raise CaseException('the capital tran change more then except!')
        df_actual_capital_notify = pd.DataFrame.from_records(data=[actual_capital_tran],
                                                             columns=except_capital_tran_key)
        df_expect_capital_notify = pd.DataFrame.from_records([except_capital_tran_list])
        pd_con = df_expect_capital_notify.compare(df_actual_capital_notify,
                                                  align_axis=0)\
            .rename(index={'self': '期望值', 'other': '实际值'}, level=-1)
        if not pd_con.empty:
            raise CaseException("the capital tran check fail with result is: \r\n{0} ".format(pd_con))

    def check_capital_notify_exist(self):
        capital_notify = self.central.get_capital_notify_info_by_id(self.capital_notify_id)
        if not capital_notify.capital_notify_status == 'success':
            raise CaseException('capital_notify status error ,need success,but {0} found'.format(
                capital_notify.capital_notify_status))

    def check_capital_notify(self, check_capital_notify, item_no):
        # 检查生成新的推送
        capital_notify = self.central.get_capital_notify_info(item_no)
        if len(capital_notify) > 1:
            raise CaseException('only one record, but found two!')
        self.capital_notify_id = capital_notify[0].capital_notify_id
        check_key = list(check_capital_notify.keys())
        capital_notify_dict = capital_notify[0].to_spec_dict
        capital_notify_dict['plan_at'] = capital_notify_dict['plan_at'][:-2] + '00'
        df_actual_capital_notify = pd.DataFrame.from_records(data=[capital_notify_dict], columns=check_key)
        df_expect_capital_notify = pd.DataFrame.from_records([check_capital_notify])
        pd_con = df_expect_capital_notify.compare(df_actual_capital_notify,
                                                  align_axis=0)\
            .rename(index={'self': '期望值', 'other': '实际值'}, level=-1)
        if not pd_con.empty:
            raise CaseException("the notify check fail with result is: \r\n{0} ".format(pd_con))

    @wait_timeout
    def run_capital_push(self, plan_at):
        self.central.run_capital_push(plan_at)
        capital_notify = self.central.get_capital_notify_info_by_id(self.capital_notify_id)
        if capital_notify.capital_notify_status == 'ready':
            return capital_notify
        return None

    @wait_timeout
    def run_capital_notify_task(self):
        self.central.run_central_task_by_order_no(self.item_no, task_type='GenerateCapitalNotify')
        central_task = self.central.get_central_task_info(self.item_no, 'GenerateCapitalNotify', status='close')
        return central_task

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
        self.repay_period_start = self.repay_info['period_start']
        self.repay_period_end = self.repay_info['period_end']
        before_capital_tran_type = self.repay_info['before_capital_tran_type']
        capital_notify = self.repay_info['capital_notify']
        mock_name = self.repay_info['mock_name']
        withhold_channel = self.repay_info['withhold_channel']
        repay_type = self.repay_info['repay_type']
        # 修改还款计划状态
        self.repay.set_asset_tran_status(self.repay_period_start, self.item_no)
        # 修改资方还款计划状态
        self.central.set_capital_tran_status(self.item_no, self.repay_period_start, before_capital_tran_type,
                                             capital_notify)
        # 还款准备-mock
        self.prepare_mock(withhold_channel)
        # 还款准备-kv
        self.prepare_kv(case, mock_name)
        # 调整还款计划日期
        self.repay.change_asset(self.item_no, '', 0, -self.repay_period_start)
        # 发起代扣并执行成功
        resp = getattr(self.repay, repay_type)(item_no=self.item_no,
                                               period_start=self.repay_period_start,
                                               period_end=self.repay_period_end,
                                               status=2)
        # 存入本次使用的代扣记录
        order_no_list, serial_no_asset_list = [], []
        for withhold in resp['response']['data']['project_list']:
            project_num = withhold['project_num']
            order_no_list.append(withhold['order_no'])
            if project_num not in serial_no_asset_list:
                serial_no_asset_list.append({project_num: withhold['order_no']})
            else:
                serial_no_asset_list[project_num] = ','.join((serial_no_asset_list[project_num], withhold['order_no']))
        self.serial_no = tuple(order_no_list)
        self.serial_no_asset = serial_no_asset_list
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
