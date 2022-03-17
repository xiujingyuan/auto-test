from app.services.repay import OverseaRepayService
from app.services.tha.grant.service import ThaGrantService


class ThaRepayService(OverseaRepayService):
    def __init__(self, env, run_env, check_req=False, return_req=False):
        self.repay_host = "http://biz-repay-tha-test{0}.c99349d1eb3d045a4857270fb79311aa0.cn-" \
                          "shanghai.alicontainer.com/".format(env)
        self.grant = ThaGrantService(env, run_env, check_req, return_req)
        super(ThaRepayService, self).__init__('tha', env, run_env, check_req, return_req)


