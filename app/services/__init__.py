# 业务逻辑
import calendar as c
import copy
import datetime
import math
import os
import random
import time
import socket

from dateutil.relativedelta import relativedelta
from faker import Faker

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sshtunnel import SSHTunnelForwarder

import app.common as common
from app.common.db_util import DataBase
from app.common.http_util import Http
from app.common.log_util import LogUtil
from app.common.tools import CheckExist, get_date
from app.services.china.repay import time_print
from app.services.china.repay.Model import SendMsg
from app.services.india.repay.Model import Task, CapitalTransaction, CapitalAsset, AssetTran, Asset, AssetExtend
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
        timeout = kwargs.pop("timeout") if 'timeout' in kwargs else 60
        while True:
            ret = func(self, *kw, **kwargs)
            if ret:
                break
            elif (self.get_date() - begin).seconds >= 60:
                raise CaseException('not found the record with {0}， with args is :{1}'.format(timeout, kwargs))
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
        self.easy_mock = common.EasyMockFactory.get_easy_mock(country, program, check_req, return_req)
        self.xxljob = common.XxlJobFactory.get_xxljob(country, program, env)
        self.nacos = common.NacosFactory.get_nacos(country, program, env)
        if country == 'china':
            self.engine = create_engine(AutoTestConfig.SQLALCHEMY_DICT[country][program].format(env), echo=False)
            self.db_session = MyScopedSession(sessionmaker())
            self.db_session.configure(bind=self.engine)
        else:
            ssh_config = AutoTestConfig.SQLALCHEMY_DICT[country]['ssh']
            self.dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            ssh_pkey = os.path.join(self.dir, ssh_config["ssh_private_key"])
            port = self.get_port()
            self.server = SSHTunnelForwarder(
                        (ssh_config["ssh_proxy_host"], 22),
                        ssh_username=ssh_config["ssh_user_name"],
                        ssh_pkey=ssh_pkey,
                        remote_bind_address=(ssh_config["ssh_remote_host"], 3306),
                        local_bind_address=('127.0.0.1', port))
            self.server.start()
            self.engine = create_engine(AutoTestConfig.SQLALCHEMY_DICT[country][program].format(env, port), echo=False)
            self.db_session = MyScopedSession(sessionmaker())
            self.db_session.configure(bind=self.engine)
        self.log = LogUtil()

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

    def run_xxl_job(self, job_type, param=None):
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
        real_now = self.get_date(months=advance_month, days=advance_day).date()
        for asset in asset_list:
            asset.asset_actual_grant_at = real_now
        if capital_asset is not None and capital_asset:
            capital_asset.capital_asset_granted_at = real_now

        for asset_tran in asset_tran_list:
            if interval_day in (7, 14):
                asset_tran_due_at = self.get_date(date=real_now, days=asset_tran.asset_tran_period * interval_day)
            else:
                asset_tran_due_at = self.get_date(date=real_now, months=asset_tran.asset_tran_period)
            if asset_tran.asset_tran_finish_at.year != 1000:
                cal_advance_day = self.cal_days(asset_tran.asset_tran_due_at, asset_tran.asset_tran_finish_at)
                cal_advance_month = self.cal_months(asset_tran.asset_tran_due_at, asset_tran.asset_tran_finish_at)
                asset_tran.asset_tran_finish_at = self.get_date(date=asset_tran_due_at, months=cal_advance_month,
                                                                days=cal_advance_day)
            asset_tran.asset_tran_due_at = asset_tran_due_at

        for capital_tran in capital_tran_list:
            if interval_day in (7, 14):
                expect_finished_at = self.get_date(date=real_now,
                                                   days=capital_tran.capital_transaction_period * interval_day)
            else:
                expect_finished_at = self.get_date(date=real_now, months=capital_tran.capital_transaction_period)
            if capital_tran.capital_transaction_user_repay_at.year != 1000:
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
            if getattr(capital_tran, actual_operate_at).year != 1000:
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
                                                    SendMsg.sendmsg_type == sendmsg_type).first()
        return self.run_msg_by_id(msg.sendmsg_id)

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
    def get_bank_code(cls, bank_name="工商银行", bank_code_suffix=None):
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
    def get_four_element(cls, bank_name='工商银行', bank_code_suffix=None, min_age=25, max_age=45, gender="F", id_num=None):
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


class GrantBaseService(BaseService):
    def __init__(self, country, env, run_env, check_req, return_req):
        super(GrantBaseService, self).__init__(country, 'grant', env, run_env, check_req, return_req)
        self.asset_import_url = self.grant_host + '/paydayloan/asset-sync-new'
        self.repay_capital_asset_import_url = self.repay_host + '/capital-asset/grant'
        self.repay_asset_withdraw_success_url = self.repay_host + "/sync/asset-withdraw-success"
        self.run_task_id_url = self.grant_host + '/task/run?taskId={0}'
        self.run_msg_id_url = self.grant_host + '/msg/run?msgId={0}'
        self.run_task_order_url = self.grant_host + '/task/run?orderNo={0}'


class RepayBaseService(BaseService):
    def __init__(self, country, env, run_env, check_req, return_req):
        super(RepayBaseService, self).__init__(country, 'repay', env, run_env, check_req, return_req)
        self.decrease_url = self.repay_host + "/asset/bill/decrease"
        self.offline_recharge_url = self.repay_host + "/account/recharge-encrypt"
        self.offline_repay_url = self.repay_host + "/asset/repayPeriod"
        self.active_repay_url = self.repay_host + "/paydayloan/repay/combo-active-encrypt"
        self.fox_repay_url = self.repay_host + "/fox/manual-withhold-encrypt"
        self.refresh_url = self.repay_host + "/asset/refreshLateFee"
        self.send_msg_url = self.repay_host + "/paydayloan/repay/bindSms"
        self.pay_svr_callback_url = self.repay_host + "/paysvr/callback"
        self.reverse_url = self.repay_host + "/asset/repayReverse"
        self.withdraw_success_url = self.repay_host + "/sync/asset-withdraw-success"
        self.run_task_id_url = self.repay_host + '/task/run?taskId={0}'
        self.run_msg_id_url = self.repay_host + '/msg/run?msgId={0}'
        self.run_task_order_url = self.repay_host + '/task/run?orderNo={0}'
        self.bc_query_asset_url = self.repay_host + '/paydayloan/projectRepayQuery'

    def refresh_late_fee(self, item_no):
        if not item_no:
            return
        request_data = {
            "from_system": "Biz",
            "type": "RbizRefreshLateInterest",
            "key": self.__create_req_key__(item_no, prefix='Refresh'),
            "data": {
                "asset_item_no": item_no
            }
        }
        asset = self.db_session.query(Asset).filter(Asset.asset_item_no == item_no).first()
        if not asset:
            raise ValueError("not found the asset, check env!")
        resp = Http.http_post(self.refresh_url, request_data)
        asset_x = self.get_no_loan(item_no)
        if asset_x:
            request_x_data = copy.deepcopy(request_data)
            request_x_data['key'] = self.__create_req_key__(asset_x, prefix='Refresh')
            request_x_data['data']['asset_item_no'] = asset_x
            resp_x = Http.http_post(self.refresh_url, request_x_data)
            self.run_task_by_type_and_order_no('AssetAccountChangeNotify', asset_x)
        self.run_task_by_type_and_order_no('AssetAccountChangeNotify', item_no)
        return [request_data, request_x_data] if asset_x else [request_data], self.refresh_url, [resp, resp_x] \
            if asset_x else [resp]

    def run_task_by_type_and_order_no(self, task_type, order_no):
        task_list = self.db_session.query(Task).filter(Task.task_type == task_type,
                                                       Task.task_order_no == order_no,
                                                       Task.task_status == 'open').all()
        for task in task_list:
            self.run_task_by_id(task.task_id)

    @time_print
    def sync_plan_to_bc(self, item_no):
        now = self.get_date(is_str=True, fmt='%Y-%m-%d')
        self.run_xxl_job('syncAssetToBiz', param={'assetItemNo': [item_no]})
        self.run_msg_by_order_no(item_no, 'asset_change_fix_status')
        self.biz_central.run_central_msg_by_order_no(item_no, 'AssetChangeNotify', max_create_at=now)

    def get_no_loan(self, item_no):
        item_no_x = ''
        asset_extend = self.db_session.query(AssetExtend).filter(
            AssetExtend.asset_extend_asset_item_no == item_no,
            AssetExtend.asset_extend_type == 'ref_order_no'
        ).first()
        if asset_extend:
            ref_order_type = self.db_session.query(AssetExtend).filter(
                AssetExtend.asset_extend_asset_item_no == item_no,
                AssetExtend.asset_extend_type == 'ref_order_type'
            ).first()
            item_no_x = asset_extend.asset_extend_val if ref_order_type and \
                                                         ref_order_type.asset_extend_val != 'lieyin' else ''
        return item_no_x

    @time_print
    def change_asset(self, item_no, item_no_rights, advance_day, advance_month, interval_day=30):
        item_no_tuple = tuple(item_no.split(',')) if ',' in item_no else (item_no,)
        for index, item in enumerate(item_no_tuple):
            item_no_x = self.get_no_loan(item)
            item_tuple = tuple([x for x in [item, item_no_x, item_no_rights] if x])
            asset_list = self.db_session.query(Asset).filter(Asset.asset_item_no.in_(item_tuple)).all()
            if not asset_list:
                raise ValueError('not found the asset, check the env!')
            asset_tran_list = self.db_session.query(AssetTran).filter(
                AssetTran.asset_tran_asset_item_no.in_(item_tuple)).order_by(AssetTran.asset_tran_period).all()
            capital_asset = self.db_session.query(CapitalAsset).filter(
                CapitalAsset.capital_asset_item_no == item).first()
            capital_tran_list = self.db_session.query(CapitalTransaction).filter(
                CapitalTransaction.capital_transaction_item_no == item).all()
            self.change_asset_due_at(asset_list, asset_tran_list, capital_asset, capital_tran_list, advance_day,
                                     advance_month, interval_day)
            if self.country == 'china':
                self.biz_central.change_asset(item, item_no_x, item_no_rights, advance_day, advance_month)
        self.refresh_late_fee(item_no)
        self.refresh_late_fee(item_no_rights)
        self.sync_plan_to_bc(item_no)
        return "修改完成"


class OverseaGrantService(GrantBaseService):
    def __init__(self, country, env, run_env, check_req=False, return_req=False):
        super(OverseaGrantService, self).__init__(country, env, run_env, check_req, return_req)


class OverseaRepayService(RepayBaseService):
    def __init__(self, country, env, run_env, check_req=False, return_req=False):
        super(OverseaRepayService, self).__init__(country, env, run_env, check_req, return_req)

    @time_print
    def sync_plan_to_bc(self, item_no):
        self.run_xxl_job('manualSyncAsset', param={'assetItemNo': [item_no]})
        self.run_task_by_order_no(item_no, 'AssetAccountChangeNotify')
        self.run_msg_by_order_no(item_no, 'AssetChangeNotifyMQ')
