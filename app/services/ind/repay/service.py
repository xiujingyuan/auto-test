from app.services.ind.grant.service import IndGrantService
from app.services.repay import OverseaRepayService


class IndRepayService(OverseaRepayService):
    def __init__(self, env, run_env, mock_name, check_req=False, return_req=False):
        self.repay_host = "http://biz-repay-ind-test{0}.c99349d1eb3d045a4857270fb79311aa0.cn-shanghai.al" \
                          "icontainer.com".format(env)
        super(IndRepayService, self).__init__('ind', env, run_env, mock_name, check_req, return_req)
        self.grant = IndGrantService(env, run_env, mock_name, check_req, return_req)

    def auto_loan(self, channel, period, days, amount, source_type, joint_debt_item='', from_app='ind005'):
        x_item_no = False if channel == 'pico_qr' else True
        return super(IndRepayService, self).auto_loan(channel, period, days, amount, source_type,
                                                      joint_debt_item=joint_debt_item,
                                                      x_item_no=x_item_no, from_app=from_app)