import json

from sqlalchemy import desc

from app.common.log_util import LogUtil
from app.services.grant import Synctask, Sendmsg, Asset
from app.services.grant import OverseaGrantService


class ThaGrantService(OverseaGrantService):
    def __init__(self, env, run_env, mock_name, check_req=False, return_req=False):
        self.grant_host = "https://biz-gateway-proxy.starklotus.com/tha_grant{0}".format(env)
        self.repay_host = "https://biz-gateway-proxy.starklotus.com/tha_repay{0}".format(env)
        super(ThaGrantService, self).__init__('tha', env, run_env, mock_name, check_req, return_req)

    def asset_import(self, channel, count, day, types, amount, from_system, from_app,
                     source_type, element, withdraw_type, route_uuid='', insert_router_record=True):
        return super(ThaGrantService, self).asset_import(channel, count, day, types, amount, from_system, 'THA053',
                                                         source_type, element, withdraw_type, route_uuid=route_uuid,
                                                         insert_router_record=insert_router_record)
