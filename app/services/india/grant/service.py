from app.services import OverseaGrantService


class IndiaGrantService(OverseaGrantService):
    def __init__(self, env, run_env, check_req=False, return_req=False):
        super(IndiaGrantService, self).__init__('india', env, run_env, check_req, return_req)
