from app.services.pak.grant.service import PakGrantService
from app.services.repay import OverseaRepayService


class PakRepayService(OverseaRepayService):
    def __init__(self, env, run_env, mock_name, check_req=False, return_req=False):
        self.repay_host = "https://biz-gateway-proxy.starklotus.com/pak_repay{0}".format(env)
        super(PakRepayService, self).__init__('pak', env, run_env, mock_name, check_req, return_req)
        self.grant = PakGrantService(env, run_env, mock_name, check_req, return_req)