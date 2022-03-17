import json
import random
import time
from copy import deepcopy
from datetime import datetime

from sqlalchemy import desc

from app.common.log_util import LogUtil
from app.services.grant import GrantBaseService
from app.common.http_util import Http
from app.services.china.biz_central.service import ChinaBizCentralService
from app.services.china.grant import GRANT_ASSET_IMPORT_URL, FROM_SYSTEM_DICT, CHANNEL_SOURCE_TYPE_DICT
from app.services.china.grant.Model import Asset, Task, Synctask, Sendmsg, RouterLoadRecord, AssetExtend, \
    AssetTran, AssetCard, CapitalAsset


class ChinaGrantService(GrantBaseService):
    def __init__(self, env, run_env, check_req=False, return_req=False):
        self.grant_host = "http://grant{0}.k8s-ingress-nginx.kuainiujinke.com".format(env)
        self.repay_host = "http://repay{0}.k8s-ingress-nginx.kuainiujinke.com".format(env)
        self.cmdb_host = 'http://biz-cmdb-api-1.k8s-ingress-nginx.kuainiujinke.com/v6/rate/standard-calculate'
        super(ChinaGrantService, self).__init__('china', env, run_env, check_req, return_req)
        self.biz_central = ChinaBizCentralService(env, run_env, check_req, return_req)

    def add_msg(self, msg):
        new_msg = Sendmsg()
        for key, value in msg.items():
            if key != 'sendmsg_id':
                setattr(new_msg, key, value)
        new_msg.sendmsg_next_run_at = self.get_date(is_str=True)
        new_msg.sendmsg_status = 'open'
        self.db_session.add(new_msg)
        self.db_session.flush()
        self.db_session.commit()
        self.run_msg_by_id(new_msg.sendmsg_id)

    def get_apr36_total_amount(self, principal_amount, period_count):
        return self.get_total_amount(principal_amount, period_count, 36, "equal")

    def get_irr36_total_amount(self, principal_amount, period_count):
        return self.get_total_amount(principal_amount, period_count, 36, "acpi")

    def get_total_amount(self, principal_amount, period_count, interest_rate, repay_type):
        """
        标准还款计划计算
        :param principal_amount:
        :param period_count:
        :param interest_rate:
        :param repay_type: acpi / equal
        :return:
        """
        cmdb_tran = self.cmdb_standard_calc_v5(principal_amount, period_count, interest_rate, repay_type)
        total_interest = 0
        for item in cmdb_tran['data']['calculate_result']['interest']:
            total_interest += item['amount']
        total_amount = principal_amount + total_interest
        return total_amount

    def cmdb_standard_calc_v5(self, principal_amount, period_count, interest_rate, repay_type,
                              interest_year_type="360per_year", month_clear_day="D+0", clear_day="D+0", sign_date=None):
        req = {
            "type": "CalculateStandardRepayPlan",
            "key": "calculate_${key}",
            "from_system": "bc",
            "data": {
                "sign_date": self.get_date(fmt="%Y-%m-%d", is_str=True),
                "principal_amount": principal_amount,
                "period_count": period_count,
                "period_type": "month",
                "period_term": 1,
                "interest_rate": interest_rate,
                "repay_type": repay_type,
                "interest_year_type": interest_year_type,
                "month_clear_day": month_clear_day,
                "clear_day": clear_day
            }
        }
        resp = Http.http_post(self.cmdb_host, req)
        return resp

    def calc_noloan_amount(self, loan_asset_info, noloan_source_type):
        """
        计算小单金额
        # APR融担小单金额 = APR36总额 - 大单总额
        # IRR融担小单金额 = IRR36总额 - 大单总额
        # IRR权益小单金额 = APR36总额 - IRR36总额
        :param loan_asset_info:
        :param noloan_source_type:
        :return:
        """
        loan_principal_amount = loan_asset_info["data"]["asset"]["amount"] * 100
        loan_period_count = loan_asset_info["data"]["asset"]["period_count"]
        loan_total_amount = loan_asset_info["data"]["asset"]["total_amount"] * 100
        apr36_total = self.get_apr36_total_amount(loan_principal_amount, loan_period_count)
        irr36_total = self.get_irr36_total_amount(loan_principal_amount, loan_period_count)
        noloan_amount_dict = dict(zip(("rongdan", "rongdan_irr", "lieyin"),
                                      (apr36_total - loan_total_amount, irr36_total - loan_total_amount,
                                       apr36_total - irr36_total)))
        return noloan_amount_dict[noloan_source_type] / 100 \
            if noloan_source_type in noloan_amount_dict else loan_principal_amount / 8000

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

    def get_no_loan(self, item_no):
        asset_extend = self.db_session.query(AssetExtend).filter(
            AssetExtend.asset_extend_asset_item_no == item_no).first()
        if not asset_extend:
            raise ValueError('not found the asset extend info!')
        return asset_extend.asset_extend_ref_order_no

    def check_item_exist(self, item_no):
        asset = self.db_session.query(Asset).filter(
            Asset.asset_item_no == item_no).first()
        return asset

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
        asset_info, old_asset = self.get_asset_info_from_db(channel)
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
            self.insert_router_record(item_no, channel, amount, count, element, asset_info,
                                      sub_order_type=sub_order_type)
        return asset_info, old_asset

    def asset_no_loan_import(self, asset_info, import_asset_info, item_no, x_item_no, source_type):
        _, no_old_asset = self.get_asset_info_from_db()
        no_asset_info = deepcopy(asset_info)
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


