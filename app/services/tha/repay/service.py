from app.services.repay import OverseaRepayService
from app.services.tha.grant.service import ThaGrantService


class ThaRepayService(OverseaRepayService):
    def __init__(self, env, run_env, mock_name, check_req=False, return_req=False):
        self.repay_host = "https://biz-gateway-proxy.starklotus.com/tha_repay{0}".format(env)
        self.grant = ThaGrantService(env, run_env, mock_name, check_req, return_req)
        super(ThaRepayService, self).__init__('tha', env, run_env, check_req, return_req)

    def auto_loan(self, channel, period, days, amount, source_type, joint_debt_item='', from_app='mango'):
        x_item_no = False if channel == 'pico_qr' else True
        return super(ThaRepayService, self).auto_loan(channel, period, days, amount, source_type,
                                                      joint_debt_item=joint_debt_item,
                                                      x_item_no=x_item_no, from_app=from_app)

