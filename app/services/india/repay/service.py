from app.services import OverseaRepayService


class IndiaRepayService(OverseaRepayService):
    def __init__(self, env, run_env, check_req=False, return_req=False):
        self.grant_host = "http://grant{0}-ind.c99349d1eb3d045a4857270fb79311aa0.cn-shanghai.alicontain" \
                          "er.com".format(env)
        self.repay_host = "http://biz-repay-ind-test{0}.c99349d1eb3d045a4857270fb79311aa0.cn-shanghai.al" \
                          "icontainer.com".format(env)
        super(IndiaRepayService, self).__init__('india', env, run_env, check_req, return_req)


