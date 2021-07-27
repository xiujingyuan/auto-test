# 业务逻辑
import json
import time
from datetime import datetime
from random import random

from dateutil.relativedelta import relativedelta
from faker import Faker

import app.common as common
from app.common.http_util import Http
from app.common.log_util import LogUtil
from app.common.assert_util import Assert

ENCRYPT_URL = "http://kong-api-test.kuainiujinke.com/encryptor-test/encrypt/"
ENCRYPT_DICT = {
            "idnum": 2,
            "mobile": 1,
            "card_number": 3,
            "name": 4,
            "email": 5,
            "address": 6
        }


class BaseAuto(object):

    def __init__(self, country, program, env, run_env, check_req, return_req):
        self.env = env
        self.run_env = run_env
        self.easy_mock = common.EasyMockFactory.get_easy_mock(country, program, check_req, return_req)
        self.xxljob = common.XxlJobFactory.get_xxljob(country, program, env)
        self.nacos = common.NacosFactory.get_nacos(country, program, env)
        self.db = common.DbFactory.get_db(country, program, env, run_env)
        self.log = LogUtil()
        self.host = ''
        self.run_task_id_url = self.host + '/task/run?taskId={0}'
        self.run_task_order_url = self.host + '/task/run?orderNo={0}'

    def run_task(self, order_no, task_type, excepts={'code': 0}):
        self.update_task_next_run_at_forward(order_no)
        task_id = self.db.get_task_id_by_task_type(order_no, task_type)
        ret = Http.http_get(self.run_task_id_url.format(task_id), self.header)
        if excepts:
            Assert.assert_match_json(excepts, ret[0], "task运行结果校验不通过，order_no:%s, task_type:%s" % (order_no,
                                                                                                   task_type))

    def get_task_info_by_task_type(self, order_no, task_type, task_status='open', timeout=60):
        begin = 0
        while True:
            task_list = self.get_data('task', task_type=task_type, task_order_no=order_no, task_status=task_status,
                                      order_by='task_id')
            if task_list:
                return task_list
            if begin >= timeout * 100:
                return []
            begin += 1
            time.sleep(0.01)

    def get_task_id_by_task_type(self, task_type, task_order_no, task_status='open', timeout=60):
        task_info = self.get_task_info_by_task_type(task_type, task_order_no, task_status, timeout)
        if not task_info:
            raise ValueError("not found task info with task type:{0},task order no :{1}".format(task_type,
                                                                                                task_order_no))
        return task_info[0]['task_id']

    def run_task_by_order_no(self, order_no):
        self.update_task_next_run_at_forward(order_no)
        Http.http_get(self.run_task_id_url.format(order_no), self.header)

    def update_task_next_run_at_forward(self, order_no):
        self.db.update_data('task', order_no, 'task_next_run_at',
                            {'task_next_run_at': 'DATE_SUB(now(), interval 20 minute)'})

    def run_task_by_order_no_count(self, order_no, count=2):
        self.update_task_next_run_at_forward(order_no)
        for _ in range(count):
            Http.http_get(self.run_task_order_url.format(order_no), self.header)

    def run_task_for_count(self, order_no, task_type, wait_time=0.5, excepts={'code': 0}, count=1):
        self.update_task_next_run_at_forward(order_no)
        time.sleep(wait_time)
        task_id = self.get_task_id_by_task_type(order_no, task_type)
        for _ in range(count):
            ret = Http.http_get(self.run_task_id_url.format(task_id), self.header)
            if excepts:
                Assert.assert_match_json(excepts, ret[0], "task运行结果校验不通过，order_no:%s, task_type:%s" % (order_no,
                                                                                                       task_type))

    @staticmethod
    def get_date(year=0, month=0, day=0, fmt="%Y-%m-%d %H:%M:%S", timezone=None):
        return (datetime.now(timezone) + relativedelta(years=year, months=month, days=day)).strftime(fmt)

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
        bank_map = {"中国银行": "621394",
                    "工商银行": "621761",
                    "招商银行": "622598",
                    "建设银行": "552245",
                    "民生银行": "622618"}
        bank_code_bin = bank_map[bank_name]
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
        new_data = [data]
        req = Http.http_post(ENCRYPT_URL, json.dumps(new_data), headers=headers)
        result = req.json()
        return result['data'][0]['hash'] if result['code'] == 0 else result

    @classmethod
    def get_four_element(cls, bank_name=None, bank_code_suffix=None, min_age=25, max_age=45, gender="F"):
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
                "id_number_encrypt": cls.encrypt_data("idnum", id_number),
                "phone_number_encrypt": cls.encrypt_data("mobile", phone_number),
                "user_name_encrypt": cls.encrypt_data("name", user_name)
            }
        }
        return response
