from app.services.grant import OverseaGrantService


class PhlGrantService(OverseaGrantService):
    def __init__(self, env, run_env, mock_name, check_req=False, return_req=False):
        self.grant_host = "http://grant{0}-phl.c99349d1eb3d045a4857270fb79311aa0.cn-shanghai.alicontainer.com".format(
            env)
        self.repay_host = "http://repay{0}-phl.c99349d1eb3d045a4857270fb79311aa0.cn-shanghai.alicontainer.com".format(
            env)
        super(PhlGrantService, self).__init__('phl', env, run_env, mock_name, check_req, return_req)

    def asset_import(self, channel, count, day, types, amount, from_system, from_app,
                     source_type, element, withdraw_type, route_uuid='', insert_router_record=True):
        return super(PhlGrantService, self).asset_import(channel, count, day, types, amount, from_system, 'phi011',
                                                         source_type, element, withdraw_type, route_uuid=route_uuid,
                                                         insert_router_record=insert_router_record)
