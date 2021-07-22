# 业务逻辑
from app.common.db_util import DataBase
from app.common.easy_mock_util import EasyMock
from app.common.nacos_util import Nacos
from app.common.xxljob_util import XxlJob


class BaseAuto(object):

    def __init__(self, country, program, env, run_env, check_req, return_req):
        self.easy_mock = None if program == 'biz-central' else EasyMock(program, check_req, return_req)
        self.xxljob = XxlJob(country, program, env)
        self.nacos = Nacos(country, program)
        self.db = DataBase(country, program, env, run_env)

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
