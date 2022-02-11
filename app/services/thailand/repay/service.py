from app.services import OverseaRepayService


class ThailandRepayService(OverseaRepayService):
    def __init__(self, env, run_env, check_req=False, return_req=False):
        self.repay_host = "http://biz-repay-tha-test{0}.c99349d1eb3d045a4857270fb79311aa0.cn-shanghai.alicontainer.com/".format(env)
        super(ThailandRepayService, self).__init__('thailand', env, run_env, check_req, return_req)


