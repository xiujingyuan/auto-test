import copy
import json
import random

from sqlalchemy import desc

from app.common.log_util import LogUtil
from app.services import Sendmsg, Asset, Synctask
from app.services.mex.grant.service import MexGrantService
from app.services.repay import OverseaRepayService, TIMEZONE


class MexRepayService(OverseaRepayService):
    def __init__(self, env, run_env, check_req=False, return_req=False):
        self.repay_host = "http://repay{0}-mex.c99349d1eb3d045a4857270fb79311aa0.cn-shanghai." \
                          "alicontainer.com".format(env)
        self.grant = MexGrantService(env, run_env, check_req, return_req)
        super(MexRepayService, self).__init__('mex', env, run_env, check_req, return_req)

    def get_asset_info_from_db(self, channel='noloan'):
        msg_task = self.db_session.query(Sendmsg).join(Asset, Asset.asset_item_no == Sendmsg.sendmsg_order_no)\
            .filter(Sendmsg.sendmsg_type == 'AssetWithdrawSuccess',
                    Asset.asset_status.in_(('repay', 'payoff')),
                    Asset.asset_loan_channel == channel).order_by(desc(Sendmsg.sendmsg_create_at)).limit(100)
        for task in msg_task:
            sync_order = ''.join((task.sendmsg_order_no, channel)) if \
                channel != 'noloan' else task.sendmsg_order_no
            asset_import_sync_task = self.db_session.query(Synctask).filter(
                Synctask.synctask_order_no == sync_order,
                Synctask.synctask_type.in_(('BCAssetImport', 'DSQAssetImport'))).first()
            if asset_import_sync_task is not None:
                item_no = asset_import_sync_task.synctask_order_no[0:-7] if  \
                    channel == 'noloan' else asset_import_sync_task.synctask_order_no.replace(channel, '')
                return json.loads(asset_import_sync_task.synctask_request_data), item_no
        LogUtil.log_info('not fount the asset import task')
        raise ValueError('not fount the asset import task')