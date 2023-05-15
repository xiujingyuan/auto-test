from app.services.grant import OverseaGrantService


class IndGrantService(OverseaGrantService):
    def __init__(self, env, run_env, mock_name, check_req=False, return_req=False):
        self.repay_host = "https://biz-gateway-proxy.starklotus.com/ind_repay{0}".format(env)
        self.grant_host = "https://biz-gateway-proxy.starklotus.com/ind_grant{0}".format(env)
        super(IndGrantService, self).__init__('ind', env, run_env, mock_name, check_req, return_req)

    def asset_import(self, channel, count, day, types, amount, from_system, from_app,
                     source_type, element, withdraw_type, route_uuid='', insert_router_record=True):
        return super(IndGrantService, self).asset_import(channel, count, day, types, amount, from_system, 'maple',
                                                         source_type, element, withdraw_type, route_uuid=route_uuid,
                                                         insert_router_record=insert_router_record)

