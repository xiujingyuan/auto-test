import copy
import json
import random

from sqlalchemy import desc

from app.common.log_util import LogUtil
from app.services import Sendmsg, Asset, Synctask
from app.services.mex.grant.service import MexGrantService
from app.services.repay import OverseaRepayService, TIMEZONE


class MexRepayService(OverseaRepayService):
    def __init__(self, env, run_env, mock_name, check_req=False, return_req=False):
        self.repay_host = "https://biz-gateway-proxy.starklotus.com/mex-repay{0}".format(env)
        self.grant = MexGrantService(env, run_env, mock_name, check_req, return_req)
        super(MexRepayService, self).__init__('mex', env, run_env, check_req, return_req)

    def auto_loan(self, channel, period, days, amount, source_type, joint_debt_item='', from_app='ginkgo'):
        x_item_no = False if channel == 'pico_qr' else True
        return super(MexRepayService, self).auto_loan(channel, period, days, amount, source_type,
                                                      joint_debt_item=joint_debt_item,
                                                      x_item_no=x_item_no, from_app=from_app)


