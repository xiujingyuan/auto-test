import json
import random
from copy import deepcopy
from datetime import datetime

from sqlalchemy import desc

from app.program_business import BaseAuto
from app.common.http_util import Http
from app.program_business.china.biz_central.services import ChinaBizCentralAuto
from app.program_business.china.grant import GRANT_ASSET_IMPORT_URL, FROM_SYSTEM_DICT, CHANNEL_SOURCE_TYPE_DICT
from app.program_business.china.grant.Model import Asset, Task, Synctask, Sendmsg, RouterLoadRecord, AssetExtend, \
    AssetTran, AssetCard, CapitalAsset


class ChinaGrantAuto(BaseAuto):
    def __init__(self, env, run_env, check_req=False, return_req=False):
        super(ChinaGrantAuto, self).__init__('china', 'grant', env, run_env, check_req, return_req)
        self.biz_central = ChinaBizCentralAuto(env, run_env, check_req, return_req)
        self.asset_import_url = self.grant_host + '/paydayloan/asset-sync-new'
        self.repay_capital_asset_import_url = self.repay_host + '/capital-asset/grant'
        self.repay_asset_withdraw_success_url = self.repay_host + "/sync/asset-withdraw-success"
        self.run_task_id_url = self.grant_host + '/task/run?taskId={0}'
        self.run_msg_id_url = self.grant_host + '/msg/run?msgId={0}'
        self.run_task_order_url = self.grant_host + '/task/run?orderNo={0}'

    @staticmethod
    def create_item_no():
        return '2020' + str(datetime.now().timestamp()).replace('.', '')

    @staticmethod
    def get_from_system_and_ref(from_system_name, source_type):
        from_system = FROM_SYSTEM_DICT[from_system_name] if from_system_name in FROM_SYSTEM_DICT else "dsq"
        source_type = "real36" if from_system_name == "火龙果" else source_type
        return from_system, source_type

    def set_asset_asset_info(self, asset_info, item_no, count, channel, amount, source_type, from_system_name,
                             ref_order_no, sub_order_type):
        asset_info['data']['asset']['item_no'] = item_no
        asset_info['data']['asset']['name'] = "tn" + item_no
        asset_info['data']['asset']['period_type'] = "month"
        asset_info['data']['asset']['period_count'] = count
        asset_info['data']['asset']['period_day'] = 0
        asset_info['data']['asset']['amount'] = amount
        asset_info['data']['asset']['grant_at'] = self.get_date(is_str=True)
        asset_info['data']['asset']['loan_channel'] = channel
        asset_info['data']['asset']['source_type'] = source_type
        asset_info['data']['asset']['from_app'] = from_system_name
        asset_info['data']['asset']['source_number'] = ref_order_no
        asset_info['data']['asset']['sub_order_type'] = sub_order_type

    @staticmethod
    def set_asset_repay_card(asset_info, element):
        asset_info['data']['repay_card']['username_encrypt'] = element['data']['user_name_encrypt']
        asset_info['data']['repay_card']['phone_encrypt'] = element['data']['phone_number_encrypt']
        asset_info['data']['repay_card']['account_num_encrypt'] = element['data']['bank_code_encrypt']
        asset_info['data']['repay_card']['individual_idnum_encrypt'] = element['data']['id_number_encrypt']
        asset_info['data']['repay_card']['credentials_num_encrypt'] = element['data']['id_number_encrypt']

    @staticmethod
    def set_asset_receive_card(asset_info, element):
        asset_info['data']['receive_card']['owner_name_encrypt'] = element['data']['user_name_encrypt']
        asset_info['data']['receive_card']['account_name_encrypt'] = element['data']['user_name_encrypt']
        asset_info['data']['receive_card']['phone_encrypt'] = element['data']['phone_number_encrypt']
        asset_info['data']['receive_card']['owner_id_encrypt'] = element['data']['id_number_encrypt']
        asset_info['data']['receive_card']['num_encrypt'] = element['data']['bank_code_encrypt']

    @staticmethod
    def set_asset_borrower(asset_info, element):
        asset_info['data']['borrower']['name_encrypt'] = element['data']['user_name_encrypt']
        asset_info['data']['borrower']['tel_encrypt'] = element['data']['phone_number_encrypt']
        asset_info['data']['borrower']['idnum_encrypt'] = element['data']['id_number_encrypt']

    @staticmethod
    def set_asset_repayer(asset_info, element):
        asset_info['data']['repayer']['name_encrypt'] = element['data']['user_name_encrypt']
        asset_info['data']['repayer']['tel_encrypt'] = element['data']['phone_number_encrypt']
        asset_info['data']['repayer']['idnum_encrypt'] = element['data']['id_number_encrypt']

    def insert_router_record(self, item_no, channel, amount, count, sub_order_type, element, asset_info):
        # 进件前，在路由表插入一条记录
        router_record = RouterLoadRecord()
        router_record.router_load_record_key = item_no + channel
        router_record.router_load_record_rule_code = channel + "_" + str(count) + "month"
        router_record.router_load_record_principal_amount = amount * 100
        router_record.router_load_record_status = 'routed'
        router_record.router_load_record_channel = channel
        router_record.router_load_record_sub_type = 'multiple'
        router_record.router_load_record_period_count = count
        router_record.router_load_record_period_type = 'month'
        router_record.router_load_record_period_days = '0'
        router_record.router_load_record_sub_order_type = sub_order_type
        router_record.router_load_record_route_day = self.get_date(fmt="%Y-%m-%d")
        router_record.router_load_record_idnum = element['data']['id_number_encrypt']
        router_record.router_load_record_from_system = asset_info['from_system']
        self.db_session.add(router_record)
        self.db_session.commit()

    def get_asset_info_from_db(self, loan=False):
        if loan:
            asset_import_sync_task = self.db_session.query(Synctask)\
                .join(Sendmsg, Sendmsg.sendmsg_order_no == Synctask.synctask_order_no)\
                .join(Asset, Asset.asset_item_no == Synctask.synctask_order_no).filter(
                Asset.asset_loan_channel == 'noloan',
                Asset.asset_status.in_(('repay', 'payoff')),
                Sendmsg.sendmsg_type == 'AssetWithdrawSuccess',
                Synctask.synctask_type.in_(('BCAssetImport', 'DSQAssetImport')))\
                .order_by(desc(Synctask.synctask_create_at)).first()
        else:
            asset_import_sync_task = self.db_session.query(Synctask) \
                .join(Sendmsg, Sendmsg.sendmsg_order_no == Synctask.synctask_order_no) \
                .join(Asset, Asset.asset_item_no == Synctask.synctask_order_no).filter(
                Asset.asset_loan_channel != 'noloan',
                Sendmsg.sendmsg_type == 'AssetWithdrawSuccess',
                Asset.asset_status.in_(('repay', 'payoff')),
                Synctask.synctask_type.in_(('BCAssetImport', 'DSQAssetImport')))\
                .order_by(desc(Synctask.synctask_create_at)).first()
        if not asset_import_sync_task:
            print('not fount the asset import task')
        return json.loads(asset_import_sync_task.synctask_request_data), asset_import_sync_task.synctask_order_no

    def get_no_loan(self, item_no):
        asset_extend = self.db_session.query(AssetExtend).filter(
            AssetExtend.asset_extend_asset_item_no == item_no).first()
        if not asset_extend:
            raise ValueError('not found the asset extend info!')
        return asset_extend.asset_extend_ref_order_no

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

    def set_withdraw_success_card_info(self, withdraw_success_data, asset_info):
        for card_key in withdraw_success_data['data']['cards_info']:
            withdraw_success_data['data']['cards_info'][card_key] = asset_info['data'][card_key]

    @staticmethod
    def set_withdraw_success_loan_record(withdraw_success_data, asset, now):
        print(withdraw_success_data["data"]['loan_record'])
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

    def get_withdraw_success_info_from_db(self, old_asset):
        send_msg = self.db_session.query(Sendmsg).filter(
            Sendmsg.sendmsg_type == 'AssetWithdrawSuccess',
            Sendmsg.sendmsg_order_no == old_asset).first()
        if not send_msg:
            raise ValueError('not fount the asset withdraw success msg!')
        return json.loads(send_msg.sendmsg_content)['body']

    def get_asset_item_info(self, channel, source_type, from_system_name, item_no=None):
        item_no = item_no if item_no else self.create_item_no()
        source_type_list = CHANNEL_SOURCE_TYPE_DICT[channel]
        filter_source = list(filter(lambda x: x[0] == source_type, source_type_list))
        if not filter_source:
            raise ValueError('the channel {0} is not match the source type {1}'.format(channel, source_type))
        source_type, x_source_type, x_right = random.choice(filter_source)
        from_system, source_type = self.get_from_system_and_ref(from_system_name, source_type)
        x_source_type = '' if source_type == 'real36' else x_source_type
        x_right = '' if source_type == 'real36' else x_right
        x_order_no = '{0}_right'.format(item_no) if x_right else ''
        ref_order_no = '{0}_noloan'.format(item_no) if x_source_type else ''
        return item_no, ref_order_no, x_order_no, source_type, x_source_type, x_right, from_system

    def asset_import(self, item_no, channel, element, count, amount, source_type, from_system_name, from_system,
                     ref_order_no, borrower_extend_district=None, sub_order_type='', route_uuid=None,
                     insert_router_record=True):
        asset_info, old_asset = self.get_asset_info_from_db()
        asset_info['key'] = "_".join((item_no, channel))
        asset_info['from_system'] = from_system
        asset_info['data']['route_uuid'] = route_uuid
        if asset_info['data']['borrower_extend']:
            asset_info['data']['borrower_extend']['address_district_code'] = borrower_extend_district
        self.set_asset_asset_info(asset_info, item_no, count, channel, amount, source_type, from_system_name,
                                  ref_order_no, sub_order_type)
        self.set_asset_receive_card(asset_info, element)
        self.set_asset_repay_card(asset_info, element)
        self.set_asset_borrower(asset_info, element)
        self.set_asset_repayer(asset_info, element)

        if insert_router_record:
            self.insert_router_record(item_no, channel, amount, count, sub_order_type, element, asset_info)
        return asset_info, old_asset

    def asset_no_loan_import(self, asset_info, item_no, x_item_no, source_type):
        _, no_old_asset = self.get_asset_info_from_db(loan=True)
        no_asset_info = deepcopy(asset_info)
        asset_extend = self.db_session.query(AssetExtend).filter(
            AssetExtend.asset_extend_asset_item_no == item_no).first()
        if source_type == 'lieyin':
            no_asset_info['data']['asset']['period_count'] = 5
        no_asset_info['key'] = self.__create_req_key__(x_item_no, prefix='Import')
        no_asset_info['data']['asset']['item_no'] = x_item_no
        no_asset_info['data']['asset']['name'] = x_item_no
        no_asset_info['data']['asset']['source_number'] = item_no
        no_asset_info['data']['asset']['amount'] = asset_info['data']['asset']['amount'] / 60
        no_asset_info['data']['asset']['source_type'] = source_type
        no_asset_info['data']['asset']['loan_channel'] = 'noloan'
        no_asset_info['data']['asset']['sub_order_type'] = asset_extend.asset_extend_sub_order_type
        return no_asset_info, no_old_asset

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
        self.biz_central.asset_import(json.loads(import_msg.sendmsg_content)['body'])

    def asset_withdraw_success(self, withdraw_success_data):
        resp = Http.http_post(self.repay_asset_withdraw_success_url, withdraw_success_data)
        if not resp['code'] == 0:
            raise ValueError("withdraw task error, {0}".format(resp['message']))

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

    def capital_asset_success(self, capital_asset):
        Http.http_post(self.repay_capital_asset_import_url, capital_asset)
        resp = Http.http_post(self.biz_central.capital_asset_import_url, capital_asset)
        self.biz_central.run_central_task_by_task_id(resp['data'])

