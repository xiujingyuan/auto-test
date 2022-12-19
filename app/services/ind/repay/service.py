from app.services.ind.grant.service import IndGrantService
from app.services.repay import OverseaRepayService


class IndRepayService(OverseaRepayService):
    def __init__(self, env, run_env, mock_name, check_req=False, return_req=False):
        self.repay_host = "http://biz-repay-ind-test{0}.c99349d1eb3d045a4857270fb79311aa0.cn-shanghai.al" \
                          "icontainer.com".format(env)
        super(IndRepayService, self).__init__('ind', env, run_env, mock_name, check_req, return_req)
        self.grant = IndGrantService(env, run_env, mock_name, check_req, return_req)
