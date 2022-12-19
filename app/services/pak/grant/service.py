from app.services.grant import OverseaGrantService


class PakGrantService(OverseaGrantService):
    def __init__(self, env, run_env, mock_name, check_req=False, return_req=False):
        self.repay_host = "repay{0}-pak.c99349d1eb3d045a4857270fb79311aa0.cn-shanghai.alicontainer.com".format(env)
        self.grant_host = "http://grant{0}-pak.c99349d1eb3d045a4857270fb79311aa0.cn-shanghai.alicontain" \
                          "er.com".format(env)
        super(PakGrantService, self).__init__('pak', env, run_env, mock_name, check_req, return_req)

    def asset_import(self, channel, count, day, types, amount, from_system, from_app,
                     source_type, element, withdraw_type, route_uuid='', insert_router_record=True):
        return super(PakGrantService, self).asset_import(channel, count, day, types, amount, from_system, 'maple',
                                                         source_type, element, withdraw_type, route_uuid=route_uuid,
                                                         insert_router_record=insert_router_record)

