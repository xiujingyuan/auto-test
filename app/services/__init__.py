# 业务逻辑
import calendar as c
import datetime
import importlib
import json
import math
import os
import random
import time
import socket

from dateutil.relativedelta import relativedelta
from faker import Faker
from flask import current_app
from flask_sqlalchemy import BaseQuery

from sqlalchemy import create_engine, desc
from sqlalchemy.orm import scoped_session, sessionmaker
from sshtunnel import SSHTunnelForwarder

import app.common as common
from app import db
from app.common.db_util import DataBase
from app.common.easy_mock_util import EasyMock
from app.common.es_util import ES
from app.common.http_util import Http
from app.common.log_util import LogUtil
from app.common.tools import CheckExist, get_date
from app.model.Model import AutoAsset, BackendKeyValue, TraceInfo
from app.services.china.repay import time_print
from app.services.china.repay.Model import SendMsg, Synctask
from app.services.ind.repay.Model import Task, CapitalTransaction, CapitalAsset, AssetTran, Asset, AssetExtend, Sendmsg

from app.test_cases import CaseException
from resource.config import AutoTestConfig

ENCRYPT_DICT = {
    "idnum": 2,
    "mobile": 1,
    "card_number": 3,
    "name": 4,
    "email": 5,
    "address": 6
}


def wait_timeout(func):
    def wrapper(self, *kw, **kwargs):
        begin = self.get_date()
        timeout = kwargs.pop("timeout") if 'timeout' in kwargs else 1
        while True:
            ret = func(self, *kw, **kwargs)
            if ret:
                break
            elif (self.get_date() - begin).seconds >= timeout:
                break
        return ret

    return wrapper


class MyScopedSession(scoped_session):

    def execute(self, *args, **kwargs):
        ret = super(MyScopedSession, self).execute(*args, **kwargs)
        return [dict(zip(result.keys(), result)) for result in ret]


ENCRYPT_URL = 'http://encryptor-test.k8s-ingress-nginx.kuainiujinke.com/encrypt/'

DECRYPT_URL = 'http://encryptor-test.k8s-ingress-nginx.kuainiujinke.com/decrypt/plain/'


class BaseService(object):

    def __init__(self, country, program, env, run_env, mock_name, check_req, return_req):
        self.env = env
        self.run_env = run_env
        self.country = country
        self.program = program
        self.mock_name = mock_name
        self.job_url = getattr(self, 'biz_host' if program == 'biz_central' else '{0}_host'.format(program)) + \
                       "/job/run"
        self.easy_mock = common.EasyMockFactory.get_easy_mock(country, program, mock_name, check_req, return_req)
        self.xxljob = common.XxlJobFactory.get_xxljob(country, program, env)
        self.nacos = common.NacosFactory.get_nacos(country, program, env)
        db_key = '{0}_{1}_{2}'.format(country, env, program)
        port = 3306
        # if db_key not in current_app.global_data:
        current_app.global_data[db_key] = {}
        if country != 'china':
            port = self.get_port()
            ssh_config = AutoTestConfig.SQLALCHEMY_DICT[country]['ssh']
            self.dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            ssh_pkey = os.path.join(self.dir, ssh_config["ssh_private_key"])
            self.server = SSHTunnelForwarder(
                (ssh_config["ssh_proxy_host"], 22),
                ssh_username=ssh_config["ssh_user_name"],
                ssh_pkey=ssh_pkey,
                remote_bind_address=(ssh_config["ssh_remote_host"], 3306),
                local_bind_address=('127.0.0.1', port))
            # current_app.global_data[db_key]['server'] = self.server
            self.server.start()
        self.engine = create_engine(AutoTestConfig.SQLALCHEMY_DICT[country][program].format(env, port), echo=False)
        # current_app.global_data[db_key]['engine'] = self.engine
        # else:
        #     self.server = current_app.global_data[db_key]['server']
        #     self.server.start()
        #     self.engine = current_app.global_data[db_key]['engine']

        self.db_session = MyScopedSession(sessionmaker())
        self.db_session.configure(bind=self.engine, query_cls=BaseQuery)
        if country == 'china' and program == 'grant':
            self.engine_contract = create_engine(AutoTestConfig.SQLALCHEMY_DICT[country]['contract'].format(port),
                                                 echo=False)
            self.db_session_contract = MyScopedSession(sessionmaker())
            self.db_session_contract.configure(bind=self.engine_contract)
        self.log = LogUtil()

    def get_trace_info(self, trace_id, creator, services, task_order_no, operation, query_start, query_end):
        es = ES(services)
        trace_info = es.get_request_child_info(operation, query_start, query_end,
                                               order='desc', operation_index=0, orderNo=task_order_no)
        trace_info = self.save_trace_info(trace_id, operation, trace_info, creator)
        print('trace_info', trace_info)

        if trace_info:
            trace_info_first = list(trace_info.keys())[0]
            for item in trace_info[trace_info_first]:
                if '/mock/' in trace_info[trace_info_first][item]['http.url']:
                    easy_mock = EasyMock(trace_info[trace_info_first][item]['http.url'].split("/")[5:][0])
                    api_info = easy_mock.get_api_info_by_api(trace_info[trace_info_first][item]['path'], None)
                    trace_info[trace_info_first][item]['mock'] = api_info['mode']
        return trace_info[list(trace_info.keys())[0]] if trace_info else ''

    def save_trace_info(self, trace_id, operate_type, content, creator):
        trace_info = db.session.query(TraceInfo).filter(TraceInfo.trace_info_program == self.program,
                                                        TraceInfo.trace_info_env == int(self.env),
                                                        TraceInfo.trace_info_trace_id == trace_id).first()
        if content:
            if trace_info is None:
                trace_info = TraceInfo()
                trace_info.trace_info_creator = creator
                trace_info.trace_info_trace_id = trace_id
                trace_info.trace_info_trace_type = operate_type
                trace_info.trace_info_env = int(self.env)
                trace_info.trace_info_program = self.program

            trace_info.trace_info_content = json.dumps(content, ensure_ascii=False)
            db.session.add(trace_info)
            db.session.flush()
        elif trace_info is not None:
            content = trace_info.trace_info_content
        return content
    @staticmethod
    def get_random_str(num=10):
        data = '1234567890abcdefghijklmnopqrstuvwxyz'
        result = ''
        for i in range(num):
            result = result + random.choice(list(data))
        return result

    def get_key_value(self, key_name, is_json=True):
        record = BackendKeyValue.query.filter(BackendKeyValue.backend_group == self.program,
                                              BackendKeyValue.backend_key == key_name,
                                              BackendKeyValue.backend_is_active == 1).first()
        return json.loads(record.backend_value) if is_json else record.backend_value

    def get_detail_info(self, table_name, get_id, get_attr, extend):
        if get_attr == 'trace_info':
            order_no = f'{table_name.replace("central_", "")}_order_no' if \
                table_name.startswith('central_') else 'order_no'
            task_type = f'{table_name.replace("central_", "")}_type' if \
                table_name.startswith('central_') else 'type'
            service_name = f'biz-central-{self.env}' if \
                table_name.startswith('central_') else f'{self.program}{self.env}'
            service_name = f'gbiz{self.env}' if \
                table_name.startswith('grant_') else service_name
            return self.get_trace_info(get_id, extend['creator'], service_name, extend[order_no],
                                       extend[task_type], None, None)
        meta_class = importlib.import_module('app.services.{0}.{1}.Model'.format(self.country, self.program))
        table_name = table_name.replace("grant_", '')
        obj = getattr(meta_class, ''.join(
            tuple(map(lambda x: x.title() if x != 'msg' else 'SendMsg', table_name.split('_')))))
        table_name = table_name.replace('central_', '')
        table_name = table_name if table_name != 'msg' else 'sendmsg'
        item = self.db_session.query(obj).filter(getattr(obj, '{0}_id'.format(table_name)) == get_id).first()
        attr_name = '{0}_{1}'.format(table_name, get_attr) if not get_attr.startswith(table_name) else get_attr
        return getattr(item, attr_name) if hasattr(item, attr_name) else ''

    def run_job_by_api(self, job_type, job_params):
        # return Http.http_get(self.job_url + "?jobType={0}&param={1}".format(job_type, json.dumps(job_params)))
        return Http.http_get(self.job_url + "?jobType={0}&param={1}".format(job_type, job_params))

    @staticmethod
    def get_port():
        port = 0
        for i in range(10):
            ip = '127.0.0.1'
            port = random.randint(20000, 31000)
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = s.connect_ex((ip, port))
            s.close()
            if result == 0:
                LogUtil.log_info("port:%s already been used" % port)
            else:
                LogUtil.log_info("port:%s already been choiced" % port)
                break
            if i == 9:
                raise Exception("未选到合适的端口")
        return port

    def run_xxl_job(self, job_type, param={}, invoke_type='api'):
        if not param:
            get_param = self.xxljob.get_job_info(job_type)[0]['executorParam']
            param = param if param else get_param
        if invoke_type == 'api':
            param = param if isinstance(param, dict) else json.loads(param)
            return self.run_job_by_api(job_type, param)
        else:
            return self.xxljob.trigger_job(job_type, executor_param=param)

    def __del__(self):
        if hasattr(self, 'db_session'):
            self.db_session.close()
        if hasattr(self, 'server'):
            self.server.close()

    @staticmethod
    def __create_req_key__(item_no, prefix=''):
        return "{1}_{0}_{2}".format(prefix, item_no, int(time.time())) if prefix != 'FOX' else "FOX_{0}_{1}".format(
            item_no, int(time.time()))

    @staticmethod
    def cal_days(str1, str2):
        date1 = datetime.datetime.strptime(str1[0:10], "%Y-%m-%d") if isinstance(str1, str) else str1
        date2 = datetime.datetime.strptime(str2[0:10], "%Y-%m-%d") if isinstance(str2, str) else str2
        date1 = date1.date() if isinstance(date1, datetime.datetime) else date1
        date2 = date2.date() if isinstance(date2, datetime.datetime) else date2
        num = (date2 - date1).days
        return num

    @staticmethod
    def cal_months(start_date, end_date):
        # 计算两个日期相隔月差
        start_date = start_date.date() if isinstance(start_date, datetime.datetime) else start_date
        end_date = end_date.date() if isinstance(end_date, datetime.datetime) else end_date
        try:
            same_month_date = datetime.date(end_date.year, end_date.month, start_date.day)
        except:
            same_month_date = datetime.date(end_date.year, end_date.month,
                                            c.monthrange(end_date.year, end_date.month)[1]
                                            )
        hold_months = 0
        decimal_month = 0.0
        if same_month_date > end_date:
            if end_date.month > 1:
                try:
                    pre_month_date = datetime.date(end_date.year, end_date.month - 1, start_date.day)
                except:
                    pre_month_date = datetime.date(end_date.year, end_date.month - 1, c.monthrange(end_date.year,
                                                                                                   end_date.month - 1)[
                        1])
            else:
                try:
                    pre_month_date = datetime.date(end_date.year - 1, 12, start_date.day)
                except:
                    pre_month_date = datetime.date(end_date.year - 1, 12, c.monthrange(end_date.year - 1, 1)[1])
            curr_month_days = (same_month_date - pre_month_date).days
            hold_months = (pre_month_date.year - start_date.year) * 12 + pre_month_date.month - start_date.month
            decimal_month = (end_date - pre_month_date).days / curr_month_days
        elif same_month_date < end_date:
            if end_date.month < 12:
                try:
                    next_month_date = datetime.date(end_date.year, end_date.month + 1, start_date.day)
                except:
                    next_month_date = datetime.date(end_date.year, end_date.month + 1, c.monthrange(end_date.year,
                                                                                                    end_date.month + 1)[
                        1])
            else:
                try:
                    next_month_date = datetime.date(end_date.year + 1, 1, start_date.day)
                except:
                    next_month_date = datetime.date(end_date.year + 1, 1, c.monthrange(end_date.year + 1, 1)[1])
            curr_month_days = (next_month_date - same_month_date).days
            hold_months = (same_month_date.year - start_date.year) * 12 + same_month_date.month - start_date.month
            decimal_month = (end_date - same_month_date).days / curr_month_days
        else:
            hold_months = (end_date.year - start_date.year) * 12 + end_date.month - start_date.month
        return int(math.modf(hold_months + decimal_month)[-1])

    @time_print
    def change_asset_due_at(self, asset_list, asset_tran_list, capital_asset, capital_tran_list, advance_day,
                            advance_month, interval_day):
        if interval_day == 30:
            real_now = self.get_date(months=advance_month, days=advance_day).date()
        else:
            real_now = self.get_date(days=(advance_day + interval_day * advance_month)).date()
        channel, due_bill_no = None, None
        for asset in asset_list:
            asset.asset_actual_grant_at = real_now
            if asset.asset_loan_channel != 'noloan':
                channel = asset.asset_loan_channel
                due_bill_no = asset.asset_due_bill_no if hasattr(asset, 'asset_due_bill_no') else None
            if asset.asset_status == 'payoff':
                asset.asset_actual_payoff_at = self.get_date(date=real_now,
                                                             days=asset.asset_period_count * interval_day)
                asset.asset_payoff_at = self.get_date(date=real_now, days=asset.asset_period_count * interval_day)
        if capital_asset is not None and capital_asset:
            capital_asset.capital_asset_granted_at = real_now
        add_day = 0
        update_capital_plan = []
        update_capital_plan_key = {}
        finish_time = {}
        user_repay_time = {}
        operate_time = {}
        capital_mock = ('lanhai_zhongshi_qj', 'lanzhou_haoyue_qinjia')
        if channel in capital_mock:
            update_capital_grant = {
                "channel": "KN10001",
                "loanNo": due_bill_no,
                "lenderTime": self.get_date(fmt='%Y%m%d%H%M%S', date=self.get_date(months=advance_month,
                                                                                   days=advance_day), is_str=True)
            }
        for asset_tran in asset_tran_list:
            if interval_day != 30:
                asset_tran_due_at = self.get_date(date=real_now, days=asset_tran.asset_tran_period * interval_day)
            else:
                asset_tran_due_at = self.get_date(date=real_now, months=asset_tran.asset_tran_period)
            if str(asset_tran.asset_tran_finish_at) != '1000-01-01 00:00:00':
                if str(asset_tran.asset_tran_finish_at) not in finish_time:
                    cal_advance_day = self.cal_days(asset_tran.asset_tran_due_at, asset_tran.asset_tran_finish_at)
                    cal_advance_month = self.cal_months(asset_tran.asset_tran_due_at, asset_tran.asset_tran_finish_at)
                    finish_at = self.get_date(date=asset_tran_due_at, months=cal_advance_month, days=cal_advance_day,
                                              hours=asset_tran.asset_tran_finish_at.hour,
                                              minutes=asset_tran.asset_tran_finish_at.minute,
                                              seconds=asset_tran.asset_tran_finish_at.second)
                    finish_time[str(asset_tran.asset_tran_finish_at)] = finish_at
                    asset_tran.asset_tran_finish_at = finish_at
                else:
                    asset_tran.asset_tran_finish_at = finish_time[str(asset_tran.asset_tran_finish_at)]
            if asset_tran.asset_tran_type == 'lateinterest':
                asset_tran.asset_tran_due_at = self.get_date(date=asset_tran.asset_tran_due_at, days=add_day)
            else:
                add_day = self.cal_days(asset_tran.asset_tran_due_at, asset_tran_due_at)
                if update_capital_plan_key is not None and asset_tran.asset_tran_period not in update_capital_plan_key:
                    update_capital_plan_key[asset_tran.asset_tran_period] = True
                    update_capital_plan.append({
                        "channel": "KN10001",
                        "num": str(asset_tran.asset_tran_period),
                        "loanNo": due_bill_no,
                        "dueDate": self.get_date(fmt='%Y%m%d', date=asset_tran_due_at, is_str=True)
                    })
                asset_tran.asset_tran_due_at = asset_tran_due_at

        for capital_tran in capital_tran_list:
            if interval_day != 30:
                expect_finished_at = self.get_date(date=real_now,
                                                   days=capital_tran.capital_transaction_period * interval_day)
            else:
                expect_finished_at = self.get_date(date=real_now, months=capital_tran.capital_transaction_period)
            if str(capital_tran.capital_transaction_user_repay_at) != '1000-01-01 00:00:00':
                if str(capital_tran.capital_transaction_user_repay_at) not in user_repay_time:
                    cal_advance_day = self.cal_days(capital_tran.capital_transaction_expect_finished_at,
                                                    capital_tran.capital_transaction_user_repay_at)
                    cal_advance_month = self.cal_months(capital_tran.capital_transaction_expect_finished_at,
                                                        capital_tran.capital_transaction_user_repay_at)
                    user_repay_at = self.get_date(date=expect_finished_at,
                                                  months=cal_advance_month,
                                                  days=cal_advance_day,
                                                  hour=capital_tran.capital_transaction_user_repay_at.hour,
                                                  minute=capital_tran.capital_transaction_user_repay_at.minute,
                                                  second=capital_tran.capital_transaction_user_repay_at.second)
                    user_repay_time[str(capital_tran.capital_transaction_user_repay_at)] = user_repay_at
                    capital_tran.capital_transaction_user_repay_at = user_repay_at
                else:
                    capital_tran.capital_transaction_user_repay_at = user_repay_time[
                        str(capital_tran.capital_transaction_user_repay_at)]
            actual_operate_at = 'capital_transaction_actual_operate_at' if \
                hasattr(capital_tran, 'capital_transaction_actual_operate_at') \
                else 'capital_transaction_actual_finished_at'
            if str(getattr(capital_tran, actual_operate_at)) != '1000-01-01 00:00:00':
                if str(getattr(capital_tran, actual_operate_at)) not in operate_time:
                    cal_advance_day = self.cal_days(capital_tran.capital_transaction_expect_finished_at,
                                                    getattr(capital_tran, actual_operate_at))
                    cal_advance_month = self.cal_months(capital_tran.capital_transaction_expect_finished_at,
                                                        getattr(capital_tran, actual_operate_at))
                    actual_operate_time = self.get_date(date=expect_finished_at,
                                                        months=cal_advance_month,
                                                        days=cal_advance_day)
                    operate_time[str(getattr(capital_tran, actual_operate_at))] = actual_operate_time
                    setattr(capital_tran, actual_operate_at, actual_operate_time)
                else:
                    setattr(capital_tran, actual_operate_at,
                            operate_time[str(getattr(capital_tran, actual_operate_at))])
            if hasattr(capital_tran, 'capital_transaction_expect_operate_at'):
                cal_advance_day = self.cal_days(capital_tran.capital_transaction_expect_finished_at,
                                                capital_tran.capital_transaction_expect_operate_at)
                cal_advance_month = self.cal_months(capital_tran.capital_transaction_expect_finished_at,
                                                    capital_tran.capital_transaction_expect_operate_at)
                capital_tran.capital_transaction_expect_operate_at = self.get_date(date=expect_finished_at,
                                                                                   months=cal_advance_month,
                                                                                   days=cal_advance_day)
            capital_tran.capital_transaction_expect_finished_at = expect_finished_at
        self.db_session.add_all(asset_list)
        if capital_asset is not None and capital_asset:
            self.db_session.add_all([capital_asset])
        if capital_tran_list:
            self.db_session.add_all(capital_tran_list)
        self.db_session.add_all(asset_tran_list)
        self.db_session.commit()

        if channel in capital_mock:
            if update_capital_grant:
                Http.http_post('https://openapitest.qinjia001.com/mockUpdate/MC00002', update_capital_grant)
            if update_capital_plan:
                Http.http_post('https://openapitest.qinjia001.com/mockUpdate/MC00001', update_capital_plan)

    def run_task_by_order_no(self, order_no, task_type, status='open', excepts={'code': 0}):
        task = self.db_session.query(Task).filter(Task.task_order_no == order_no,
                                                  Task.task_type == task_type,
                                                  Task.task_status == status).first()
        return self.run_task_by_id(task.task_id, excepts=excepts)

    def update_task_next_run_at_forward_by_task_id(self, task_id):
        task = self.db_session.query(Task).filter(Task.task_id == task_id).first()
        if not task:
            raise ValueError("not fund the task info with task'id {0}".format(task))
        min_diff = 1
        if self.country == 'mex':
            min_diff = -14 * 60
        elif self.country == "tha":
            min_diff = -1 * 60
        elif self.country == "pak":
            min_diff = -3 * 60
        task.task_next_run_at = get_date(minutes=min_diff)
        task.task_status = 'open'
        self.db_session.add(task)
        self.db_session.commit()

    def run_task_by_id(self, task_id, excepts={'code': 0}):
        self.update_task_next_run_at_forward_by_task_id(task_id)
        ret = Http.http_get(self.run_task_id_url.format(task_id))
        ret = ret[0] if isinstance(ret, list) else ret
        if not isinstance(ret, dict):
            raise ValueError(ret)
        elif not ret['code'] == excepts['code']:
            raise CaseException("run task error, {0}".format(ret['message']))
        elif not ret["code"] == 0:
            raise ValueError("run task error, {0}".format(ret['message']))
        return ret

    def run_msg_by_id(self, msg_id):
        ret = Http.http_get(self.run_msg_id_url.format(msg_id))
        msg = self.db_session.query(SendMsg).filter(SendMsg.sendmsg_id == msg_id).first()
        msg_content = json.loads(msg.sendmsg_content)['body']
        try:
            if msg.sendmsg_type == 'GrantCapitalAsset':
                Http.http_post(self.biz_central.capital_asset_import_url, msg_content)
            elif msg.sendmsg_type == 'AssetImportSync':
                Http.http_post(self.biz_central.asset_import_url, msg_content)
        except:
            pass
        return ret

    def run_msg_by_order_no(self, order_no, sendmsg_type):
        msg = self.db_session.query(SendMsg).filter(SendMsg.sendmsg_order_no == order_no,
                                                    SendMsg.sendmsg_type == sendmsg_type,
                                                    SendMsg.sendmsg_status == 'open').order_by(
            desc(SendMsg.sendmsg_id)).all()
        for item in msg:
            self.run_msg_by_id(item.sendmsg_id)

    def run_task_for_count(self, task_type, order_no, excepts={'code': 0}, count=1):
        task_id = self.get_task_id_by_task_type(task_type, order_no)
        self.db.update_task_next_run_at_forward_by_task_id(task_id)
        for _ in range(count):
            self.run_task_by_id(task_id, excepts=excepts)

    @staticmethod
    def get_date(fmt="%Y-%m-%d %H:%M:%S", date=None, timezone=None, is_str=False, **kwargs):
        date = date if date is not None else datetime.datetime.now(timezone)
        date = date if isinstance(date, (datetime.datetime, datetime.date)) \
            else datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
        new_data = date + relativedelta(**kwargs)
        return new_data.strftime(fmt) if is_str else new_data

    def compare_data(self, set_key, src_data, dst_data, noise_data, num):
        if isinstance(src_data, dict) and isinstance(dst_data, dict):
            """若为dict格式"""
            for key in dst_data:
                if key not in src_data:
                    print("src不存在这个key")
                    noise_data[key] = "src不存在这个key"
            for key in src_data:
                if key in dst_data:
                    if src_data[key] != dst_data[key] and num == 1:
                        noise_data[key] = "容忍不等"
                    if src_data[key] != dst_data[key] and num == 2:
                        noise_data[key] = {}
                        noise_data[key]["primary"] = src_data[key]
                        noise_data[key]["candidate"] = dst_data[key]
                    """递归"""
                    self.compare_data(key, src_data[key], dst_data[key], noise_data, num)
                else:
                    noise_data[key] = ["dst不存在这个key"]
        elif isinstance(src_data, list) and isinstance(dst_data, list):
            """若为list格式"""
            if len(src_data) != len(dst_data) and len(set_key) != 0:
                # print("list len: '{}' != '{}'".format(len(src_data), len(dst_data)))
                noise_data.append({"list src_data": src_data, "dst_data": dst_data})
                # noise_data[set_key]["primary"] = str(src_data)
                # noise_data[set_key]["candidate"] = str(dst_data)
                return noise_data
            if len(src_data) == len(dst_data) and len(src_data) > 1:
                for index in range(len(src_data)):
                    for src_list, dst_list in zip(sorted(src_data[index]), sorted(dst_data[index])):
                        """递归"""
                        self.compare_data("", src_list, dst_list, noise_data, num)
            else:
                for src_list, dst_list in zip(sorted(src_data), sorted(dst_data)):
                    """递归"""
                    self.compare_data("", src_list, dst_list, noise_data, num)
        else:
            if str(src_data) != str(dst_data):
                noise_data.append({"src_data": src_data, "dst_data": dst_data})
        return noise_data

    @classmethod
    def get_bank_code(cls, bank_name="中国银行", bank_code_suffix=None):
        # 621226430｛6｝9710
        bank_map = {"中国银行": "621394",
                    "工商银行": "621761",
                    "招商银行": "622598",
                    "建设银行": "552245",
                    "民生银行": "622618"}
        bank_code_bin = bank_map[bank_name] if bank_name in bank_map else "621761"
        # 生成需要的银行卡并返回
        bank_code = None
        for _ in range(500):
            bank_code = cls.gen_card_num(bank_code_bin, 16)
            if bank_code_suffix is None:
                break
            if bank_code.endswith(bank_code_suffix):
                break
        return bank_code

    @classmethod
    def gen_card_num(cls, start_with, total_num):
        result = start_with

        # 随机生成前N-1位
        while len(result) < total_num - 1:
            result += str(random.randint(0, 9))

        # 计算前N-1位的校验和
        s = 0
        card_num_length = len(result)
        for _ in range(2, card_num_length + 2):
            t = int(result[card_num_length - _ + 1])
            if _ % 2 == 0:
                t *= 2
                s += t if t < 10 else t % 10 + t // 10
            else:
                s += t

        # 最后一位当做是校验位，用来补齐到能够整除10
        t = 10 - s % 10
        result += str(0 if t == 10 else t)
        return result

    @staticmethod
    def encrypt_data(data_type, value):
        data = {"type": ENCRYPT_DICT[data_type], "plain": value} if data_type in ENCRYPT_DICT else None
        headers = {'content-type': 'application/json'}
        req = Http.http_post(ENCRYPT_URL, [data], headers=headers)
        return req['data'][0]['hash'] if req['code'] == 0 else req

    @staticmethod
    def decrypt_data_list(value_list):
        ret = {}
        if isinstance(value_list, list) and value_list:
            for value in value_list:
                ret[value] = BaseService.decrypt_data(value)
        return {'decrypt_data_list': ret}

    @staticmethod
    def decrypt_data(value):
        req = {"hash": value}
        headers = {'content-type': 'application/json'}
        try:
            req = Http.http_post(DECRYPT_URL, [req], headers=headers)
        except ValueError:
            return '解密失败'
        return req['data'][value] if req['code'] == 0 else req

    def get_four_element(self, bank_name='中国银行', bank_code_suffix=None, min_age=25, max_age=45, gender="F",
                         id_num=None):
        fake = Faker("zh_CN")
        id_number = fake.ssn(min_age=min_age, max_age=max_age, gender=gender)
        phone_number = fake.phone_number()
        user_name = fake.name()
        bank_code = self.get_bank_code(bank_name, bank_code_suffix)
        response = {
            "code": 0,
            "message": "success",
            "data": {
                "bank_code": bank_code,
                "phone_number": phone_number,
                "user_name": user_name,
                "id_number": id_number,

                "bank_code_encrypt": self.encrypt_data("card_number", bank_code),
                "id_number_encrypt": self.encrypt_data("idnum", id_number) if id_num is None else id_num,
                "user_name_encrypt": self.encrypt_data("name", user_name),
                "phone_number_encrypt": self.encrypt_data("mobile", phone_number),
            }
        }
        return response
