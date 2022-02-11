from app.services import OverseaGrantService


class PhilippinesGrantService(OverseaGrantService):
    def __init__(self, env, run_env, check_req=False, return_req=False):
        self.grant_host = "http://grant{0}-phl.c99349d1eb3d045a4857270fb79311aa0.cn-shanghai.alicontainer.com/".format(
            env)
        self.repay_host = "http://repay{0}-phl.c99349d1eb3d045a4857270fb79311aa0.cn-shanghai.alicontainer.com".format(
            env)
        super(PhilippinesGrantService, self).__init__('philippines', env, run_env, check_req, return_req)
