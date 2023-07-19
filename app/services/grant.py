import copy
import json
import random
import time

from sqlalchemy import desc

from app.common.http_util import Http
from app.common.log_util import LogUtil
from app.services import BaseService, CapitalAsset
from app.services.china.grant.Model import AssetExtend, AssetCard
from app.services.china.grant.Model import RouterLoadRecord, Sendmsg, Task, Synctask, AssetTran
from app.services.mex.grant.Model import Asset as OverseaAsset
from app.services.china.grant.Model import Asset


class GrantBaseService(BaseService):
    def __init__(self, country, env, run_env, mock_name, check_req, return_req):
        super(GrantBaseService, self).__init__(country, 'grant', env, run_env, mock_name, check_req, return_req)
        self.asset_import_url = self.grant_host + '/paydayloan/asset-sync-new'
        self.repay_capital_asset_import_url = self.repay_host + '/capital-asset/grant'
        self.repay_asset_withdraw_success_url = self.repay_host + "/sync/asset-withdraw-success"
        self.run_task_id_url = self.grant_host + '/task/run?taskId={0}'
        self.run_msg_id_url = self.grant_host + '/msg/run?msgId={0}'
        self.run_task_order_url = self.grant_host + '/task/run?orderNo={0}'

    def get_repay_card_by_item_no(self, item_no):
        id_num_info = self.db_session.query(AssetCard). filter(AssetCard.asset_card_asset_item_no == item_no,
                                                               AssetCard.asset_card_type == 'receive').first()
        return id_num_info.to_dict if id_num_info is not None else ''

    def get_asset(self, item_no):
        asset = self.check_item_exist(item_no)
        if asset is None:
            return {'asset': []}
        asset = asset.to_spec_dict
        four_ele = self.get_repay_card_by_item_no(item_no)
        asset['id_num'] = four_ele['asset_card_account_idnum_encrypt']
        asset['id_num_entry'] = self.decrypt_data(four_ele['asset_card_account_idnum_encrypt'])
        asset['repay_card'] = four_ele['asset_card_account_card_number_encrypt']
        asset['repay_card_entry'] = self.decrypt_data(four_ele['asset_card_account_card_number_encrypt'])
        asset['repay_name'] = four_ele['asset_card_account_name_encrypt']
        asset['repay_name_entry'] = self.decrypt_data(four_ele['asset_card_account_name_encrypt'])
        asset['repay_tel'] = four_ele['asset_card_account_tel_encrypt']
        asset['repay_tel_entry'] = self.decrypt_data(four_ele['asset_card_account_tel_encrypt'])
        asset['item_x'] = self.get_no_loan(item_no)
        return {'asset': [asset]}

    def get_router_loan_record(self, channel):
        router_data = self.db_session.query(RouterLoadRecord).filter(
            RouterLoadRecord.router_load_record_channel == channel,
            RouterLoadRecord.router_load_record_extend_info != '').first()
        return {'extend_info': ''} if router_data is None else router_data.to_spec_dict

    def get_no_loan(self, item_no):
        asset_extend = self.db_session.query(AssetExtend).filter(
            AssetExtend.asset_extend_asset_item_no == item_no).first()
        return asset_extend.asset_extend_ref_order_no

    def update_task_next_run_at_forward_by_task_id(self, task_id):
        task = self.db_session.query(Task).filter(Task.task_id == task_id).first()
        if not task:
            raise ValueError("not fund the task info with task'id {0}".format(task))
        task.task_status = 'open'
        min_diff = 1
        if self.country == 'mex':
            min_diff = -14 * 60
        elif self.country == "tha":
            min_diff = -1 * 60
        task.task_next_run_at = self.get_date(minutes=min_diff)
        self.db_session.add(task)
        self.db_session.commit()

    def check_item_exist(self, item_no):
        asset = self.db_session.query(Asset).filter(
            Asset.asset_item_no == item_no).first()
        return asset

    def get_capital_asset_data(self, item_no):
        capital_asset = self.db_session.query(CapitalAsset).order_by(desc(CapitalAsset.capital_asset_create_at)).first()
        asset = self.db_session.query(Asset).order_by(desc(Asset.asset_item_no == item_no)).first()
        asset_tran_list = self.db_session.query(AssetTran).filter(AssetTran.asset_tran_asset_item_no == item_no,
                                                                  AssetTran.asset_tran_period > 0).all()
        if not capital_asset:
            raise ValueError('not fount capital asset')
        capital_asset.capital_asset_channel = asset.asset_loan_channel
        capital_asset.capital_asset_item_no = asset.asset_item_no
        capital_asset.capital_asset_granted_at = asset.asset_actual_grant_at
        capital_asset.capital_asset_push_at = asset.asset_actual_grant_at
        capital_asset.capital_asset_period_count = asset.asset_period_count
        capital_asset.capital_asset_period_term = asset.asset_product_category
        capital_asset.capital_asset_due_at = asset.asset_due_at
        capital_asset.capital_asset_granted_amount = asset.asset_granted_principal_amount
        capital_asset.capital_asset_cmdb_no = asset.asset_cmdb_product_number
        captial_info = capital_asset.to_spec_dict
        captial_info['capital_transactions'] = []
        for asset_tran in asset_tran_list:
            asset_tran_dict = asset_tran.to_spec_dict
            asset_tran_dict['item_no'] = asset_tran.asset_tran_asset_item_no
            asset_tran_dict['type'] = asset_tran_dict['type'] .replace('repay', '')
            asset_tran_dict['repayment_type'] = 'acpi'
            asset_tran_dict['period_type'] = 'month'
            asset_tran_dict['period_term'] = 1
            asset_tran_dict['rate'] = 0.00000000
            asset_tran_dict['origin_amount'] = asset_tran.asset_tran_amount
            asset_tran_dict['user_repay_at'] = '1000-01-01 00:00:00'
            asset_tran_dict['user_repay_channel'] = ''
            asset_tran_dict['expect_finished_at'] = asset_tran_dict['due_at']
            asset_tran_dict['actual_finished_at'] = ''
            asset_tran_dict['operate_type'] = 'grant'
            captial_info['capital_transactions'].append(asset_tran_dict)
        return captial_info

    def get_withdraw_success_data(self, item_no, old_asset, x_item_no, asset_info):
        now = self.get_date(is_str=True)
        withdraw_success_data = self.get_withdraw_success_info_from_db(old_asset)
        asset = self.db_session.query(Asset).filter(Asset.asset_item_no == item_no).first()
        withdraw_success_data['key'] = self.__create_req_key__(item_no, prefix='GrantSuccess')
        self.set_withdraw_success_dtran_and_fee(withdraw_success_data, item_no, now)
        self.set_withdraw_success_asset(withdraw_success_data, asset, x_item_no)
        self.set_withdraw_success_card_info(withdraw_success_data, asset_info)
        self.set_withdraw_success_loan_record(withdraw_success_data, asset, now)
        return withdraw_success_data

    def set_withdraw_success_dtran_and_fee(self, withdraw_success_data, item_no, now):
        asset_tran_list = self.db_session.query(AssetTran).filter(
            AssetTran.asset_tran_asset_item_no == item_no).all()
        withdraw_success_data["data"]['dtransactions'] = []
        withdraw_success_data["data"]['fees'] = []
        for asset_tran in asset_tran_list:
            asset_tran.asset_tran_finish_at = now if \
                asset_tran.asset_tran_type == 'grant' else asset_tran.asset_tran_finish_at
            asset_tran.asset_tran_status = 'finish' if asset_tran.asset_tran_type == 'grant' else 'nofinish'
            if asset_tran.asset_tran_type in ('grant', 'repayprincipal', 'repayinterest'):
                withdraw_success_data['data']['dtransactions'].append(asset_tran.to_spec_dict)
            else:
                withdraw_success_data['data']['fees'].append(asset_tran.to_spec_dict)

    def get_asset_info(self, item_no):
        asset_info = {}
        asset = self.get_asset(item_no)
        asset_info.update(asset)
        return asset_info

    def set_withdraw_success_asset(self, withdraw_success_data, asset, x_item_no):
        biz_asset = self.biz_central.get_asset_info(asset.asset_item_no)
        asset.asset_status = 'repay'
        asset.asset_version = biz_asset.asset_version + 10
        asset.asset_interest_rate = 5
        asset.asset_item_no = asset.asset_item_no
        asset.asset_actual_grant_at = self.get_date()
        asset.asset_granted_principal_amount = asset.asset_principal_amount
        asset.ref_order_no = x_item_no
        for data_key in withdraw_success_data['data']['asset']:
            new_key = 'asset_' + data_key
            if hasattr(asset, new_key):
                withdraw_success_data['data']['asset'][data_key] = asset.to_dict[new_key]
            if hasattr(asset, data_key):
                withdraw_success_data['data']['asset'][data_key] = getattr(asset, data_key)

    @staticmethod
    def set_withdraw_success_card_info(withdraw_success_data, asset_info):
        for card_key in withdraw_success_data['data']['cards_info']:
            withdraw_success_data['data']['cards_info'][card_key] = asset_info['data'][card_key]

    @staticmethod
    def set_withdraw_success_loan_record(withdraw_success_data, asset, now):
        LogUtil.log_info(withdraw_success_data["data"]['loan_record'])
        if withdraw_success_data["data"]['loan_record'] is not None:
            withdraw_success_data["data"]['loan_record']['grant_at'] = now
            withdraw_success_data["data"]['loan_record']['push_at'] = now
            withdraw_success_data["data"]['loan_record']['finish_at'] = now
            withdraw_success_data["data"]['loan_record']['channel'] = asset.asset_loan_channel
            withdraw_success_data["data"]['loan_record']['amount'] = asset.asset_granted_principal_amount
            withdraw_success_data["data"]['loan_record']['asset_item_no'] = asset.asset_item_no
            withdraw_success_data["data"]['loan_record']['identifier'] = asset.asset_item_no
            withdraw_success_data["data"]['loan_record']['trade_no'] = 'TN' + asset.asset_item_no
            withdraw_success_data["data"]['loan_record']['due_bill_no'] = 'DN' + asset.asset_item_no
            if asset.asset_loan_channel == 'zhongke_hegang':
                withdraw_success_data["data"]['loan_record']['product_code'] = \
                    random.choice(('KN0-CL', 'KN1-CL-HLJ', 'KN1-CL-NOT-HLJ'))

    def set_withdraw_success_asset(self, withdraw_success_data, asset, x_item_no):
        biz_asset = self.biz_central.get_asset_info(asset.asset_item_no)
        asset.asset_status = 'repay'
        asset.asset_version = biz_asset.asset_version + 10
        asset.asset_interest_rate = 5
        asset.asset_item_no = asset.asset_item_no
        asset.asset_actual_grant_at = self.get_date()
        asset.asset_granted_principal_amount = asset.asset_principal_amount
        asset.ref_order_no = x_item_no
        for data_key in withdraw_success_data['data']['asset']:
            new_key = 'asset_' + data_key
            if hasattr(asset, new_key):
                withdraw_success_data['data']['asset'][data_key] = asset.to_dict[new_key]
            if hasattr(asset, data_key):
                withdraw_success_data['data']['asset'][data_key] = getattr(asset, data_key)

    def get_withdraw_success_info_from_db(self, old_asset, get_type='body'):
        send_msg = self.db_session.query(Sendmsg).filter(
            Sendmsg.sendmsg_type == 'AssetWithdrawSuccess',
            Sendmsg.sendmsg_order_no == old_asset).first()
        if not send_msg:
            # raise ValueError('not fount the asset withdraw success msg!')
            return None
        return json.loads(send_msg.sendmsg_content)['body'] if get_type == "body" else send_msg.to_dict

    def get_only_grant_msg(self, old_asset):
        send_msg_list = self.db_session.query(Sendmsg).filter(
            Sendmsg.sendmsg_order_no == old_asset,
            Sendmsg.sendmsg_type.in_(('AssetImportSync', 'GrantCapitalAsset', 'AssetWithdrawSuccess'))
        ).all()
        return [x.to_dict for x in send_msg_list]

    def get_withdraw_success_info_sync_task(self, old_asset):
        task = self.db_session.query(Synctask).filter(
            Synctask.synctask_order_no == old_asset,
            Synctask.synctask_type.in_(('BCAssetImport', 'DSQAssetImport'))
        ).first()
        return task.to_dict if task is not None else {}

    def asset_import_success(self, asset_info):
        resp = Http.http_post(self.asset_import_url, asset_info)
        item_no = asset_info['data']['asset']['item_no']
        if not isinstance(resp, dict):
            raise ValueError('资产导入失败, {0}'.format(resp))
        elif not resp['code'] == 0:
            raise ValueError('资产导入失败, {0}'.format(resp['message']))
        import_task = self.db_session.query(Task).filter(Task.task_order_no == item_no,
                                                         Task.task_type == 'AssetImport').first()
        if not import_task:
            raise ValueError('not found import task!')
        self.run_task_by_id(import_task.task_id)

        import_msg = self.db_session.query(Sendmsg).filter(Sendmsg.sendmsg_order_no == item_no,
                                                           Sendmsg.sendmsg_type == 'AssetImportSync').first()
        if not import_msg:
            raise ValueError("not found the import send msg!")
        asset_info = json.loads(import_msg.sendmsg_content)['body']
        self.biz_central.asset_import(asset_info)
        return asset_info

    def asset_withdraw_success(self, withdraw_success_data):
        resp = Http.http_post(self.repay_asset_withdraw_success_url, withdraw_success_data)
        if not resp['code'] == 0:
            raise ValueError("withdraw task error, {0}".format(resp['message']))

    def insert_router_record(self, item_no, channel, amount, count, element, asset_info, sub_order_type=None, days=0,
                             types='month'):
        # 进件前，在路由表插入一条记录
        extend_info = self.get_router_loan_record(channel)['extend_info']
        router_record = RouterLoadRecord()
        router_record.router_load_record_key = item_no + channel
        router_record.router_load_record_rule_code = (channel + "_" + str(count) + "m") if \
            types == 'month' else channel + "_" + str(count) + "_" + str(days) + types[:1]
        router_record.router_load_record_principal_amount = amount * 100 if self.country == 'china' else amount
        router_record.router_load_record_status = 'routed'
        router_record.router_load_record_channel = channel
        router_record.router_load_record_sub_type = 'multiple'
        router_record.router_load_record_period_count = count
        router_record.router_load_record_period_type = types
        router_record.router_load_record_period_days = days
        router_record.router_load_record_period_days = days
        router_record.router_load_record_extend_info = extend_info
        if sub_order_type is not None:
            router_record.router_load_record_sub_order_type = sub_order_type
        router_record.router_load_record_route_day = self.get_date(fmt="%Y-%m-%d")
        router_record.router_load_record_idnum = element['data']['id_number_encrypt'] if 'data' in element else element['id_num']
        router_record.router_load_record_from_system = asset_info['from_system']
        self.db_session.add(router_record)
        self.db_session.commit()

    def asset_no_loan_import(self, asset_info, import_asset_info, item_no, x_item_no, source_type):
        _, no_old_asset = self.get_asset_info_from_db()
        no_asset_info = copy.deepcopy(asset_info)
        asset_extend = self.db_session.query(AssetExtend).filter(
            AssetExtend.asset_extend_asset_item_no == item_no).first()
        if source_type == 'lieyin':
            no_asset_info['data']['asset']['period_count'] = 5
        no_asset_info['key'] = self.__create_req_key__(x_item_no, prefix='Import')
        no_asset_info['data']['asset']['item_no'] = x_item_no
        no_asset_info['data']['asset']['name'] = x_item_no
        no_asset_info['data']['asset']['source_number'] = item_no
        no_asset_info['data']['asset']['amount'] = self.calc_noloan_amount(import_asset_info, source_type)
        no_asset_info['data']['asset']['source_type'] = source_type
        no_asset_info['data']['asset']['loan_channel'] = 'noloan'
        no_asset_info['data']['asset']['sub_order_type'] = asset_extend.asset_extend_sub_order_type
        return no_asset_info, no_old_asset

    def create_item_no(self):
        return "{0}{1}{2}".format(random.choice(('B', 'S')), self.get_date().year, int(time.time()))

    def get_asset_info_from_db(self, channel='noloan'):
        asset_import_sync_task = self.db_session.query(Synctask) \
            .join(Sendmsg, Sendmsg.sendmsg_order_no == Synctask.synctask_order_no) \
            .join(Asset, Asset.asset_item_no == Synctask.synctask_order_no).filter(
            Asset.asset_loan_channel == channel,
            Sendmsg.sendmsg_type == 'AssetWithdrawSuccess',
            Asset.asset_from_system != 'pitaya',
            Asset.asset_status.in_(('repay', 'payoff')),
            Synctask.synctask_type.in_(('BCAssetImport', 'DSQAssetImport')))\
            .order_by(desc(Synctask.synctask_create_at)).first()
        if asset_import_sync_task is None:
            LogUtil.log_info('not fount the asset import task')
            raise ValueError('not fount the asset import task')
        return json.loads(asset_import_sync_task.synctask_request_data), asset_import_sync_task.synctask_order_no


ChangeCapital = [
                {
                    "action": {
                        "policy": "autoRun"
                    },
                    "matches": [
                        {
                            "code": "4",
                            "messages": [
                                "进件,路由系统返回空"
                            ]
                        },
                        {
                            "code": "1",
                            "messages": [
                                "\\[E20001\\]4",
                                "\\[E20010\\]KN_TIMEOUT_CLOSE_ORDER",
                                "\\[E20001\\]Unpredictable exception occur\\.",
                                "\\[E20001\\]Wallet balance limit exceeded",
                                "\\[E20001\\]Target Account is not registered",
                                "\\[E20001\\]InquirySuccess",
                                "\\[E20001\\]Failed to transfer funds"
                            ]
                        }
                    ]
                },
                {
                    "action": {
                        "policy": "autoRollBackToCanLoan",
                        "next_run_at": "delayDays(1,\"04:00:00\")"
                    },
                    "matches": [
                        {
                            "code": "4",
                            "messages": [
                                ".*校验资金量失败.*"
                            ]
                        }
                    ]
                }
            ]

AssetVoid = [
                {
                    "action": {
                        "policy": "autoRollBackToChangeCapital",
                        "circuit_break_name": "Manual_Job_Autorun_Circuit_Break"
                    },
                    "matches": [
                        {
                            "code": "14",
                            "messages": [
                                "发生冲正,作废资产"
                            ]
                        },
                        {
                            "code": "12",
                            "messages": [
                                ".*切资方,路由系统返回空.*"
                            ]
                        }
                    ]
                }
            ]

GbizManualTaskAutoProcessConfig = {
    "ChangeCapital": {},
    "AssetVoid": {},
    "CapitalAssetReverse": {},
    "BlacklistCollect": {}}


class OverseaGrantService(GrantBaseService):
    def __init__(self, country, env, run_env, mock_name, check_req=False, return_req=False):
        super(OverseaGrantService, self).__init__(country, env, run_env, mock_name, check_req, return_req)
        self.asset_import_url = self.grant_host + '/paydayloan/asset-sync'
        self.repay_asset_withdraw_success_url = self.repay_host + "/sync/asset/from-grant"
        self.capital_asset_success_url = self.repay_host + "/capital-asset/grant"

    def check_item_exist(self, item_no):
        asset = self.db_session.query(OverseaAsset).filter(
            OverseaAsset.asset_item_no == item_no).first()
        return asset

    def capital_asset_success(self, capital_info):
        resp = Http.http_post(self.capital_asset_success_url, capital_info)
        return resp

    def get_withdraw_success_data(self, item_no, old_asset, x_item_no, asset_info, element=None):
        now = self.get_date(is_str=True)
        withdraw_success_data = self.get_withdraw_success_info_from_db(old_asset)
        asset = self.db_session.query(Asset).filter(Asset.asset_item_no == item_no).first()
        asset_tran = self.db_session.query(AssetTran).filter(AssetTran.asset_tran_asset_item_no == item_no).all()
        withdraw_success_data['key'] = self.__create_req_key__(item_no, prefix='GrantSuccess')
        withdraw_success_data['data']['trans'] = list(map(lambda x: x.to_spec_dict, asset_tran))
        if element is not None:
            self.set_withdraw_success_borrow(withdraw_success_data, element)
        self.set_withdraw_success_asset(withdraw_success_data, asset, x_item_no)
        self.set_withdraw_success_loan_record(withdraw_success_data, asset, now)
        return withdraw_success_data

    @staticmethod
    def set_withdraw_success_borrow(withdraw_success_data, element):
        withdraw_success_data['data']['borrower']['borrower_uuid'] = element['data']['card_num']
        withdraw_success_data['data']['borrower']['id_num'] = element['data']['id_number_encrypt']
        withdraw_success_data['data']['borrower']['mobile'] = element['data']['mobile_encrypt']
        withdraw_success_data['data']['borrower']['borrower_card_uuid'] = element['data']['id_number']
        withdraw_success_data['data']['borrower']['individual_uuid'] = element['data']['card_num']

    def asset_import_success(self, asset_info):
        resp = Http.http_post(self.asset_import_url, asset_info)
        item_no = asset_info['data']['asset']['item_no']
        if not isinstance(resp, dict):
            raise ValueError('资产导入失败, {0}'.format(resp))
        elif not resp['code'] == 0:
            raise ValueError('资产导入失败, {0}'.format(resp['message']))
        import_task = self.db_session.query(Task).filter(Task.task_order_no == item_no,
                                                         Task.task_type == 'AssetImport').first()
        self.run_task_by_id(import_task.task_id)
        return asset_info

    def set_withdraw_success_asset(self, withdraw_success_data, asset, x_item_no):
        asset.asset_status = 'repay'
        asset.asset_version = time.time()
        asset.asset_interest_rate = 5
        asset.asset_item_no = asset.asset_item_no
        asset.asset_actual_grant_at = self.get_date()
        asset.asset_granted_principal_amount = asset.asset_principal_amount
        asset.ref_order_no = x_item_no
        for data_key in withdraw_success_data['data']['asset']:
            new_key = 'asset_' + data_key
            if hasattr(asset, new_key):
                withdraw_success_data['data']['asset'][data_key] = asset.to_dict[new_key]
            if hasattr(asset, data_key):
                withdraw_success_data['data']['asset'][data_key] = getattr(asset, data_key)

    def set_asset_asset_info(self, asset_info, item_no, count, channel, amount, source_type, types, days,
                             from_app, from_system):
        asset_info['data']['asset']['item_no'] = item_no
        asset_info['data']['asset']['period_type'] = types
        asset_info['data']['asset']['period_count'] = count
        asset_info['data']['asset']['period_day'] = days
        asset_info['data']['asset']['amount'] = amount
        asset_info['data']['asset']['grant_at'] = self.get_date(is_str=True)
        asset_info['data']['asset']['loan_channel'] = channel
        asset_info['data']['asset']['source_type'] = source_type
        asset_info['data']['asset']['from_app'] = from_app
        asset_info['data']['asset']['source_number'] = item_no + "_no_loan" if '_bill' in source_type else ''
        asset_info['data']['asset']['from_system'] = from_system

    @staticmethod
    def set_asset_borrower(asset_info, element, withdraw_type=''):
        if 'data' in element:
            asset_info['data']['borrower']['id_num'] = element["data"]["id_number_encrypt"]
            asset_info['data']['borrower']['borrower_uuid'] = element["data"]["id_number"] + "0"
            asset_info['data']['borrower']['borrower_card_uuid'] = element["data"]["card_num"]
            asset_info['data']['borrower']['mobile'] = element["data"]["mobile_encrypt"]
            asset_info['data']['borrower']['individual_uuid'] = element["data"]["id_number"] + "1"
        else:
            for key in element:
                asset_info['data']['borrower'][key] = element[key]

        if withdraw_type:
            asset_info['data']['borrower']['withdraw_type'] = withdraw_type

    @staticmethod
    def get_config_data(config_name, channel):
        json_path_dict = copy.deepcopy(eval(config_name.title().replace('_', '')))
        json_path_dict['ChangeCapital'][channel] = ChangeCapital
        json_path_dict['AssetVoid'][channel] = AssetVoid
        return json_path_dict

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
                item_no = asset_import_sync_task.synctask_order_no[0:-len(channel)] if  \
                    channel == 'noloan' else asset_import_sync_task.synctask_order_no.replace(channel, '')
                return json.loads(asset_import_sync_task.synctask_request_data), item_no
            else:
                asset_import_sync_task = self.db_session.query(Synctask).filter(
                    Synctask.synctask_order_no == task.sendmsg_order_no,
                    Synctask.synctask_type.in_(('BCAssetImport', 'DSQAssetImport'))).first()
                if asset_import_sync_task is not None:
                    item_no = asset_import_sync_task.synctask_order_no if \
                        channel == 'noloan' else asset_import_sync_task.synctask_order_no.replace(channel, '')
                    return json.loads(asset_import_sync_task.synctask_request_data), item_no
        LogUtil.log_info('not fount the asset import task')
        raise ValueError('not fount the asset import task')

    def get_four_element(self):
        four_element = super(GrantBaseService, self).get_four_element()
        response = {
            "code": 0,
            "message": "success",
            "data": {
                "bank_account": four_element["data"]["bank_code"],
                "card_num": four_element["data"]["bank_code"],
                "mobile": four_element["data"]["phone_number"],
                "user_name": "Craltonliu",
                "id_number": four_element["data"]["id_number"],
                "address": "Floor 8 TaiPingYang Building TianFuSanGai Chengdu,Sichuan,China",
                "email": four_element["data"]["phone_number"] + "@qq.com",
                "upi": four_element["data"]["phone_number"] + "@upi"
            }
        }
        data = [{"type": 1, "plain": response["data"]["mobile"]},
                {"type": 2, "plain": response["data"]["id_number"]},
                {"type": 3, "plain": response["data"]["card_num"]},
                {"type": 3, "plain": response["data"]["upi"]},
                {"type": 4, "plain": response["data"]["user_name"]},
                {"type": 5, "plain": response["data"]["email"]},
                {"type": 6, "plain": response["data"]["address"]}]
        resp = Http.http_post(url=self.encrypt_url, req_data=data)
        response["data"]["mobile_encrypt"] = resp["data"][0]["hash"]
        response["data"]["id_number_encrypt"] = resp["data"][1]["hash"]
        response["data"]["card_num_encrypt"] = resp["data"][2]["hash"]
        response["data"]["upi_encrypt"] = resp["data"][3]["hash"]
        response["data"]["user_name_encrypt"] = resp["data"][4]["hash"]
        response["data"]["email_encrypt"] = resp["data"][5]["hash"]
        response["data"]["address_encrypt"] = resp["data"][6]["hash"]
        response["data"]["bank_account_encrypt"] = resp["data"][2]["hash"]
        return response

    def asset_no_loan_import(self, asset_info, import_asset_info, item_no, x_item_no, source_type, element):
        _, no_old_asset = self.get_asset_info_from_db()
        no_asset_info = copy.deepcopy(asset_info)
        no_asset_info['key'] = self.__create_req_key__(x_item_no, prefix='Import')
        no_asset_info['data']['asset']['item_no'] = x_item_no
        no_asset_info['data']['asset']['name'] = x_item_no
        no_asset_info['data']['asset']['source_number'] = item_no
        no_asset_info['data']['asset']['amount'] = import_asset_info['data']['asset']['amount'] / 10
        no_asset_info['data']['asset']['source_type'] = source_type
        no_asset_info['data']['asset']['loan_channel'] = 'noloan'
        no_asset_info['data']['asset']['ref_order_type'] = source_type
        self.set_asset_borrower(no_asset_info, element)
        return no_asset_info, no_old_asset

    def asset_import(self, channel, count, day, types, amount, from_system, from_app,
                     source_type, element, withdraw_type, route_uuid='', insert_router_record=True):
        json_path_dict = self.get_config_data('gbiz_manual_task_auto_process_config', channel)
        self.nacos.update_config_by_json_path('gbiz_manual_task_auto_process_config', json_path_dict)
        asset_info, old_asset = self.get_asset_info_from_db(channel)
        item_no = self.create_item_no()
        asset_info['key'] = "_".join((item_no, channel))
        asset_info['from_system'] = from_system
        if route_uuid:
            asset_info['data']['route_uuid'] = route_uuid
        self.set_asset_asset_info(asset_info, item_no, count, channel, amount, source_type, types, day,
                                  from_app, from_system)
        self.set_asset_borrower(asset_info, element, withdraw_type)
        if insert_router_record:
            self.insert_router_record(item_no, channel, amount, count, element, asset_info, days=day, types=types)
        return asset_info, old_asset, item_no
