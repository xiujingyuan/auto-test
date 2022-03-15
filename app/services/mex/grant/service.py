from app.services import OverseaGrantService


class MexGrantService(OverseaGrantService):
    def __init__(self, env, run_env, check_req=False, return_req=False):
        self.grant_host = "http://grant{0}-mex.c99349d1eb3d045a4857270fb79311aa0.cn-shanghai.alicontainer.com".format(
            env)
        self.repay_host = "http://repay{0}-mex.c99349d1eb3d045a4857270fb79311aa0.cn-shanghai.alicontainer.com".format(
            env)
        super(MexGrantService, self).__init__('mex', env, run_env, check_req, return_req)
