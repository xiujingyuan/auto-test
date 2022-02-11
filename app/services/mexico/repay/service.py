from app.services import OverseaRepayService


class MexicoRepayService(OverseaRepayService):
    def __init__(self, env, run_env, check_req=False, return_req=False):
        self.repay_host = "http://repay{0}-mex.c99349d1eb3d045a4857270fb79311aa0.cn-shanghai.alicontainer.com".format(env)
        super(MexicoRepayService, self).__init__('mexico', env, run_env, check_req, return_req)


