# 业务逻辑
from app.common.db_util import DataBase
from app.common.easy_mock_util import EasyMock
from app.common.nacos_util import Nacos
from app.common.xxljob_util import XxlJob


class BaseAuto(object):

    def __init__(self, country, program, env, run_env, check_req, return_req):
        self.easy_mock = EasyMock(country, program, check_req, return_req)
        self.xxljob = XxlJob(country, program, env)
        self.nacos = Nacos(country, program, check_req, return_req)
        self.db = DataBase(country, program, env, run_env)
