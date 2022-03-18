import json

from sqlalchemy import desc

from app.common.log_util import LogUtil
from app.services import Synctask, Sendmsg, Asset
from app.services.grant import OverseaGrantService


class ThaGrantService(OverseaGrantService):
    def __init__(self, env, run_env, check_req=False, return_req=False):
        self.grant_host = "http://grant{0}-tha.c99349d1eb3d045a4857270fb79311aa0.cn-shanghai.alicontainer.com".format(
            env)
        self.repay_host = "http://biz-repay-tha-test{0}.c99349d1eb3d045a4857270fb79311aa0.cn-" \
                          "shanghai.alicontainer.com/".format(env)
        super(ThaGrantService, self).__init__('tha', env, run_env, check_req, return_req)

    def get_asset_info_from_db(self, channel='noloan'):
        msg_task = self.db_session.query(Sendmsg).join(Asset, Asset.asset_item_no == Sendmsg.sendmsg_order_no)\
            .filter(Sendmsg.sendmsg_type == 'AssetWithdrawSuccess',
                    Asset.asset_status.in_(('repay', 'payoff')),
                    Asset.asset_loan_channel == channel).order_by(desc(Synctask.synctask_create_at)).limit(100)
        for task in msg_task:
            asset_import_sync_task = self.db_session.query(Synctask).filter(
                Synctask.synctask_order_no == (task + channel),
                Synctask.synctask_type.in_(('BCAssetImport', 'DSQAssetImport'))).first()
            if asset_import_sync_task is not None:
                return json.loads(asset_import_sync_task.synctask_request_data), asset_import_sync_task.synctask_order_no
        LogUtil.log_info('not fount the asset import task')
        raise ValueError('not fount the asset import task')

    def asset_import(self, channel, count, day, types, amount, from_system, from_app,
                     source_type, element, withdraw_type, route_uuid='', insert_router_record=True):
        return super(ThaGrantService, self).asset_import(channel, count, day, types, amount, from_system, 'THA053',
                                                         source_type, element, withdraw_type, route_uuid=route_uuid,
                                                         insert_router_record=insert_router_record)
