from app.services import OverseaGrantService


class IndGrantService(OverseaGrantService):
    def __init__(self, env, run_env, check_req=False, return_req=False):
        super(IndGrantService, self).__init__('ind', env, run_env, check_req, return_req)
