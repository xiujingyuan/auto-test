import json
from datetime import datetime

from sqlalchemy import desc

from app.program_business import BaseAuto
from app.common.http_util import Http
from app.program_business.china.biz_central.services import ChinaBizCentralAuto
from app.program_business.china.grant import GRANT_ASSET_IMPORT_URL, FROM_SYSTEM_DICT
from app.program_business.china.grant.Model import Asset, Task, Synctask, Sendmsg, RouterLoadRecord, AssetExtend, \
    AssetTran, AssetCard


class ChinaGrantAuto(BaseAuto):
    def __init__(self, env, run_env, check_req=False, return_req=False):
        super(ChinaGrantAuto, self).__init__('china', 'grant', env, run_env, check_req, return_req)
        self.host_url = "https://kong-api-test.kuainiujinke.com/gbiz{0}".format(env)
        self.biz_central = ChinaBizCentralAuto(env, run_env, check_req, return_req)
        self.asset_import_url = self.host_url + '/paydayloan/asset-sync-new'
        self.run_task_id_url = self.host_url + '/task/run?taskId={0}'
        self.run_msg_id_url = self.host_url + '/msg/run?msgId={0}'
        self.run_task_order_url = self.host_url + '/task/run?orderNo={0}'

    @staticmethod
    def create_item_no():
        return '2020' + str(datetime.now().timestamp()).replace('.', '')

    @staticmethod
    def get_from_system_and_ref(item_no, from_system_name, source_type):
        from_system = FROM_SYSTEM_DICT[from_system_name] if from_system_name in FROM_SYSTEM_DICT else "dsq"
        source_type = "real36" if from_system_name == "火龙果" else source_type
        ref_order_no = item_no if from_system_name == "火龙果" else item_no + "_noloan"
        return from_system, ref_order_no, source_type

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
        while True:
            if loan:
                asset = self.db_session.query(Asset).filter(Asset.asset_loan_channel == 'noloan').order_by(
                    desc(Asset.asset_create_at)).first()
            else:
                asset = self.db_session.query(Asset).filter(Asset.asset_loan_channel != 'noloan').order_by(
                    desc(Asset.asset_create_at)).first()
            if not asset:
                print('not fount a import asset')
            else:
                asset_import_sync_task = self.db_session.query(Synctask).filter(
                    Synctask.synctask_order_no == asset.asset_item_no,
                    Synctask.synctask_type.in_(('BCAssetImport', 'DSQAssetImport'))).first()
                if not asset_import_sync_task:
                    print('not fount the asset import task!')
                else:
                    break
        return json.loads(asset_import_sync_task.synctask_request_data)

    def get_no_loan(self, item_no):
        asset_extend = self.db_session.query(AssetExtend).filter(
            AssetExtend.asset_extend_asset_item_no == item_no).first()
        if not asset_extend:
            raise ValueError('not found the asset extend info!')
        return asset_extend.asset_extend_ref_order_no

    def get_withdraw_success_data(self, item_no):
        now = self.get_date(is_str=True)
        withdraw_success_data = self.get_withdraw_success_info_from_db()
        asset = self.db_session.query(Asset).filter(Asset.asset_item_no == item_no).first()
        withdraw_success_data['key'] = self.__create_req_key__(item_no, prefix='GrantSuccess')
        self.set_withdraw_success_dtran_and_fee(withdraw_success_data, item_no, now)
        self.set_withdraw_success_asset(withdraw_success_data, asset, now)
        self.set_withdraw_success_card_info(withdraw_success_data, item_no)
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
            if asset_tran.asset_tran_type not in ('grant', 'repayprincipal', 'repayinterest'):
                withdraw_success_data['dtransactions'].append(asset_tran.to_dict)
            else:
                withdraw_success_data['fees'].append(asset_tran.to_dict)

    def set_withdraw_success_asset(self, withdraw_success_data, asset):
        biz_asset = self.biz_central.get_asset_info(asset.asset_item_no)
        asset.asset_status = 'repay'
        asset.asset_version = biz_asset.asset_version + 10
        asset.asset_interest_rate = 5
        for data_key in withdraw_success_data['data']['asset']:
            new_key = 'asset_' + data_key
            if new_key in asset:
                withdraw_success_data['data']['asset'][data_key] = asset[new_key]

    def set_withdraw_success_card_info(self, withdraw_success_data, item_no):
        card_list = self.db_session.query(AssetCard).filter(AssetCard.asset_card_asset_item_no == item_no).order_by(
            AssetCard.asset_card_type).all()
        for card in AssetCard.to_dicts(card_list):
            card_key = card.asset_card_type + "_card"
            for data_key in withdraw_success_data['data']['cards_info'][card_key]:
                new_key = 'asset_card_' + data_key
                if new_key in card:
                    withdraw_success_data['data']['cards_info'][card_key][data_key] = card[new_key]

    @staticmethod
    def set_withdraw_success_loan_record(withdraw_success_data, asset, now):
        withdraw_success_data["data"]['loan_record']['grant_at'] = now
        withdraw_success_data["data"]['loan_record']['push_at'] = now
        withdraw_success_data["data"]['loan_record']['finish_at'] = now
        withdraw_success_data["data"]['loan_record']['amount'] = asset.asset_granted_principal_amount
        withdraw_success_data["data"]['loan_record']['asset_item_no'] = asset.asset_item_no
        withdraw_success_data["data"]['loan_record']['identifier'] = asset.asset_item_no
        withdraw_success_data["data"]['loan_record']['trade_no'] = 'TN' + asset.asset_item_no
        withdraw_success_data["data"]['loan_record']['due_bill_no'] = 'DN' + asset.asset_item_no



    def get_withdraw_success_info_from_db(self):
        while True:
            asset = self.db_session.query(Asset).filter(Asset.asset_status == 'repay').order_by(
                desc(Asset.asset_create_at)).first()
            if not asset:
                print('not fount a import asset')
            else:
                asset_withdraw_success_msg = self.db_session.query(Sendmsg).filter(
                    Sendmsg.sendmsg_order_no == asset.asset_item_no,
                    Sendmsg.sendmsg_type == 'AssetWithdrawSuccess').first()
                if not asset_withdraw_success_msg:
                    print('not fount the asset withdraw success msg!')
                else:
                    break
        return json.loads(asset_withdraw_success_msg.sendmsg_content)['body']

    def asset_import(self, channel, element, count, amount, from_system_name='香蕉', item_no='',
                     borrower_extend_district=None, sub_order_type='', route_uuid=None, insert_router_record=True):
        item_no = item_no if item_no else self.create_item_no()
        source_type = "irr36_quanyi" if channel in ("qinnong", "qinnong_jieyi", "mozhi_jinmeixin") else "apr36"
        x_source_type = "rongdan_irr" if channel in ("qinnong", "qinnong_jieyi", "mozhi_jinmeixin") else "rongdan"
        from_system, ref_order_no, source_type = self.get_from_system_and_ref(item_no, from_system_name, source_type)
        asset_info = self.get_asset_info_from_db()
        asset_info['key'] = "_".join((item_no, channel))
        asset_info['from_system'] = from_system
        asset_info['data']['route_uuid'] = route_uuid if route_uuid else None
        asset_info['data']['borrower_extend']['address_district_code'] = borrower_extend_district if \
            borrower_extend_district else None
        self.set_asset_asset_info(asset_info, item_no, count, channel, amount, source_type, from_system_name,
                                  ref_order_no, sub_order_type)
        self.set_asset_receive_card(asset_info, element)
        self.set_asset_repay_card(asset_info, element)
        self.set_asset_borrower(asset_info, element)
        self.set_asset_repayer(asset_info, element)

        if insert_router_record:
            self.insert_router_record(item_no, channel, amount, count, sub_order_type, element, asset_info)

        resp = Http.http_post(self.asset_import_url, asset_info)
        if not resp['code'] == 0:
            raise ValueError('资产导入失败, {0}'.format(resp['message']))
        return item_no, asset_info

    def asset_import_success(self, item_no):
        import_task = self.db_session.query(Task).filter(Task.task_order_no == item_no,
                                                         Task.task_type == 'AssetImport').first()
        if not import_task:
            raise ValueError('not found import task!')
        self.run_task_by_id(import_task.task_id)

        import_msg = self.db_session.query(Sendmsg).filter(Sendmsg.sendmsg_order_no == item_no,
                                                           Sendmsg.sendmsg_type == 'AssetImportSync').first()
        if not import_msg:
            raise ValueError("not found the import send msg!")
        # self.run_msg_by_id(import_msg.sendmsg_id)
        self.biz_central.asset_import(json.loads(import_msg.sendmsg_content)['body'])


