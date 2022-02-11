from app.services import OverseaGrantService


class ThailandGrantService(OverseaGrantService):
    def __init__(self, env, run_env, check_req=False, return_req=False):
        self.grant_host = "http://grant{0}-tha.c99349d1eb3d045a4857270fb79311aa0.cn-shanghai.alicontainer.com".format(env)
        self.repay_host = "http://biz-repay-tha-test{0}.c99349d1eb3d045a4857270fb79311aa0.cn-shanghai.alicontainer.com/".format(env)
        super(ThailandGrantService, self).__init__('thailand', env, run_env, check_req, return_req)
