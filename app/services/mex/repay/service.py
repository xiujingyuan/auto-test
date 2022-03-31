import copy
import json
import random

from sqlalchemy import desc

from app.common.log_util import LogUtil
from app.services import Sendmsg, Asset, Synctask
from app.services.mex.grant.service import MexGrantService
from app.services.repay import OverseaRepayService, TIMEZONE


class MexRepayService(OverseaRepayService):
    def __init__(self, env, run_env, check_req=False, return_req=False):
        self.repay_host = "http://repay{0}-mex.c99349d1eb3d045a4857270fb79311aa0.cn-shanghai." \
                          "alicontainer.com".format(env)
        self.grant = MexGrantService(env, run_env, check_req, return_req)
        super(MexRepayService, self).__init__('mex', env, run_env, check_req, return_req)


