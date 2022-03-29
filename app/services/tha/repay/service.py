from app.services.repay import OverseaRepayService
from app.services.tha.grant.service import ThaGrantService


class ThaRepayService(OverseaRepayService):
    def __init__(self, env, run_env, check_req=False, return_req=False):
        self.repay_host = "http://biz-repay-tha-test{0}.c99349d1eb3d045a4857270fb79311aa0.cn-" \
                          "shanghai.alicontainer.com/".format(env)
        self.grant = ThaGrantService(env, run_env, check_req, return_req)
        super(ThaRepayService, self).__init__('tha', env, run_env, check_req, return_req)

    def auto_loan(self, channel, period, days, amount, source_type, joint_debt_item='', from_app='cherry'):
        x_item_no = False if channel == 'pico_qr' else True
        return super(ThaRepayService, self).auto_loan(channel, period, days, amount, source_type,
                                                      joint_debt_item=joint_debt_item,
                                                      x_item_no=x_item_no, from_app=from_app)

