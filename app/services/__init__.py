# 业务逻辑
import calendar as c
import datetime
import json
import math
import os
import random
import time
import socket

from dateutil.relativedelta import relativedelta
from faker import Faker
from flask import current_app

from sqlalchemy import create_engine, desc
from sqlalchemy.orm import scoped_session, sessionmaker
from sshtunnel import SSHTunnelForwarder

import app.common as common
from app import db
from app.common.db_util import DataBase
from app.common.http_util import Http
from app.common.log_util import LogUtil
from app.common.tools import CheckExist, get_date
from app.model.Model import AutoAsset
from app.services.china.repay import time_print
from app.services.china.repay.Model import SendMsg, Synctask
from app.services.ind.repay.Model import Task, CapitalTransaction, CapitalAsset, AssetTran, Asset, AssetExtend, Sendmsg

from app.test_cases import CaseException
from resource.config import AutoTestConfig

ENCRYPT_URL = "http://kong-api-test.kuainiujinke.com/encryptor-test/encrypt/"
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
        print('begin, ', begin)
        timeout = kwargs.pop("timeout") if 'timeout' in kwargs else 1
        while True:
            ret = func(self, *kw, **kwargs)
            print('begin diff, ', (self.get_date() - begin).seconds)
            if ret:
                break
            elif (self.get_date() - begin).seconds >= 1:
                raise CaseException('not found the record')
        return ret

    return wrapper


class MyScopedSession(scoped_session):

    def execute(self, *args, **kwargs):
        ret = super(MyScopedSession, self).execute(*args, **kwargs)
        return [dict(zip(result.keys(), result)) for result in ret]


class BaseService(object):

    def __init__(self, country, program, env, run_env, check_req, return_req):
        self.env = env
        self.run_env = run_env
        self.country = country
        self.job_url = getattr(self, 'biz_host' if program ==
                                                   'biz_central' else '{0}_host'.format(program)) + "/job/run"
        self.easy_mock = common.EasyMockFactory.get_easy_mock(country, program, check_req, return_req)
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
        self.db_session.configure(bind=self.engine)
        self.log = LogUtil()

    def run_job_by_api(self, job_type, job_params):
        return Http.http_get(self.job_url + "?jobType={0}&param={1}".format(job_type, json.dumps(job_params)))

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
        if invoke_type == 'api':
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
        return "{0}{1}_{2}".format(prefix, item_no, int(time.time()))

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
        for asset in asset_list:
            asset.asset_actual_grant_at = real_now
            if asset.asset_status == 'payoff':
                asset.asset_actual_payoff_at = self.get_date(date=real_now, days=asset.asset_period_count * interval_day)
                asset.asset_payoff_at = self.get_date(date=real_now, days=asset.asset_period_count * interval_day)
        if capital_asset is not None and capital_asset:
            capital_asset.capital_asset_granted_at = real_now
        add_day = 0
        for asset_tran in asset_tran_list:
            if interval_day != 30:
                asset_tran_due_at = self.get_date(date=real_now, days=asset_tran.asset_tran_period * interval_day)
            else:
                asset_tran_due_at = self.get_date(date=real_now, months=asset_tran.asset_tran_period)
            if isinstance(asset_tran.asset_tran_finish_at, datetime.datetime) \
                    and asset_tran.asset_tran_finish_at.year != 1000:
                cal_advance_day = self.cal_days(asset_tran.asset_tran_due_at, asset_tran.asset_tran_finish_at)
                cal_advance_month = self.cal_months(asset_tran.asset_tran_due_at, asset_tran.asset_tran_finish_at)
                asset_tran.asset_tran_finish_at = self.get_date(date=asset_tran_due_at, months=cal_advance_month,
                                                                days=cal_advance_day)
            if asset_tran.asset_tran_type == 'lateinterest':
                asset_tran.asset_tran_due_at = self.get_date(date=asset_tran.asset_tran_due_at, days=add_day)
            else:
                add_day = self.cal_days(asset_tran.asset_tran_due_at, asset_tran_due_at)
                asset_tran.asset_tran_due_at = asset_tran_due_at

        for capital_tran in capital_tran_list:
            if interval_day != 30:
                expect_finished_at = self.get_date(date=real_now,
                                                   days=capital_tran.capital_transaction_period * interval_day)
            else:
                expect_finished_at = self.get_date(date=real_now, months=capital_tran.capital_transaction_period)
            if isinstance(capital_tran.capital_transaction_user_repay_at, datetime.datetime) \
                    and capital_tran.capital_transaction_user_repay_at.year != 1000:
                cal_advance_day = self.cal_days(capital_tran.capital_transaction_expect_finished_at,
                                                capital_tran.capital_transaction_user_repay_at)
                cal_advance_month = self.cal_months(capital_tran.capital_transaction_expect_finished_at,
                                                    capital_tran.capital_transaction_user_repay_at)
                user_repay_at = capital_tran.capital_transaction_user_repay_at
                capital_tran.capital_transaction_user_repay_at = self.get_date(date=expect_finished_at,
                                                                               months=cal_advance_month,
                                                                               days=cal_advance_day,
                                                                               hour=user_repay_at.hour,
                                                                               minute=user_repay_at.minute,
                                                                               second=user_repay_at.second)
            actual_operate_at = 'capital_transaction_actual_operate_at' if \
                hasattr(capital_tran, 'capital_transaction_actual_operate_at') \
                else 'capital_transaction_actual_finished_at'
            if isinstance(getattr(capital_tran, actual_operate_at), datetime.datetime) and \
                    getattr(capital_tran, actual_operate_at).year != 1000:
                cal_advance_day = self.cal_days(capital_tran.capital_transaction_expect_finished_at,
                                                getattr(capital_tran, actual_operate_at))
                cal_advance_month = self.cal_months(capital_tran.capital_transaction_expect_finished_at,
                                                    getattr(capital_tran, actual_operate_at))
                setattr(capital_tran, actual_operate_at, self.get_date(date=expect_finished_at,
                                                                       months=cal_advance_month,
                                                                       days=cal_advance_day))
            if hasattr(capital_tran, 'capital_transaction_expect_operate_at'):
                cal_advance_day = self.cal_days(capital_tran.capital_transaction_expect_finished_at,
                                                capital_tran.capital_transaction_expect_operate_at)
                cal_advance_month = self.cal_months(capital_tran.capital_transaction_expect_finished_at,
                                                    capital_tran.capital_transaction_expect_operate_at)
                capital_tran.capital_transaction_expect_operate_at = self.get_date(
                    date=expect_finished_at, months=cal_advance_month,
                    days=cal_advance_day)
            capital_tran.capital_transaction_expect_finished_at = expect_finished_at
        self.db_session.add_all(asset_list)
        if capital_asset is not None and capital_asset:
            self.db_session.add_all([capital_asset])
        if capital_tran_list:
            self.db_session.add_all(capital_tran_list)
        self.db_session.add_all(asset_tran_list)
        self.db_session.commit()

    def run_task_by_order_no(self, order_no, task_type, status='open', excepts={'code': 0}):
        task = self.db_session.query(Task).filter(Task.task_order_no == order_no,
                                                  Task.task_type == task_type,
                                                  Task.task_status == status).first()
        return self.run_task_by_id(task.task_id, excepts=excepts)

    def update_task_next_run_at_forward_by_task_id(self, task_id):
        task = self.db_session.query(Task).filter(Task.task_id == task_id).first()
        if not task:
            raise ValueError("not fund the task info with task'id {0}".format(task))
        task.task_next_run_at = get_date(minutes=1)
        self.db_session.add(task)
        self.db_session.commit()

    def run_task_by_id(self, task_id, excepts={'code': 0}):
        # self.update_task_next_run_at_forward_by_task_id(task_id)
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
        return ret

    def run_msg_by_order_no(self, order_no, sendmsg_type):
        msg = self.db_session.query(SendMsg).filter(SendMsg.sendmsg_order_no == order_no,
                                                    SendMsg.sendmsg_type == sendmsg_type,
                                                    SendMsg.sendmsg_status == 'open').order_by(desc(SendMsg.sendmsg_id)).all()
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

    @classmethod
    def get_four_element(cls, bank_name='中国银行', bank_code_suffix=None, min_age=25, max_age=45, gender="F", id_num=None):
        fake = Faker("zh_CN")
        id_number = fake.ssn(min_age=min_age, max_age=max_age, gender=gender)
        phone_number = fake.phone_number()
        user_name = fake.name()
        bank_code = cls.get_bank_code(bank_name, bank_code_suffix)
        response = {
            "code": 0,
            "message": "success",
            "data": {
                "bank_code": bank_code,
                "phone_number": phone_number,
                "user_name": user_name,
                "id_number": id_number,

                "bank_code_encrypt": cls.encrypt_data("card_number", bank_code),
                "id_number_encrypt": cls.encrypt_data("idnum", id_number) if id_num is None else id_num,
                "user_name_encrypt": cls.encrypt_data("name", user_name),
                "phone_number_encrypt": cls.encrypt_data("mobile", phone_number),
            }
        }
        return response









