
import random
from app import db
from sqlalchemy import desc

from app.model.Model import AutoAsset
from app.services import time_print
from app.services.grant import GrantBaseService
from app.common.http_util import Http
from app.services.china.biz_central.service import ChinaBizCentralService
from app.services.china.grant import FROM_SYSTEM_DICT, CHANNEL_SOURCE_TYPE_DICT
from app.services.china.grant.Model import Asset, Task, Sendmsg, AssetExtend, \
    AssetTran, CapitalAsset, AssetLoanRecord, CapitalTransaction, CapitalAccount, RouterCapitalPlan


class ChinaGrantService(GrantBaseService):
    def __init__(self, env, run_env, mock_name, check_req=False, return_req=False):
        self.grant_host = "http://grant{0}.k8s-ingress-nginx.kuainiujinke.com".format(env)
        self.repay_host = "http://repay{0}.k8s-ingress-nginx.kuainiujinke.com".format(env)
        self.cmdb_host = 'http://biz-cmdb-api-1.k8s-ingress-nginx.kuainiujinke.com/v6/rate/standard-calculate'
        super(ChinaGrantService, self).__init__('china', env, run_env, mock_name, check_req, return_req)
        self.biz_central = ChinaBizCentralService(env, run_env, mock_name, check_req, return_req)
        self.task_url = self.grant_host + '/task/run?orderNo={0}'
        self.msg_url = self.grant_host + '/msg/run?orderNo={0}'

    @time_print
    def info_refresh(self, item_no, max_create_at=None, refresh_type=None):
        asset = self.asset
        ret = getattr(self, 'get_{0}'.format(refresh_type))(item_no)
        ret.update(asset)
        return ret

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

    def delete_row_data(self, del_id, del_type):
        obj = eval(del_type.title().replace("_", ""))
        self.db_session.query(obj).filter(getattr(obj, 'id') == del_id).delete()
        self.db_session.flush()
        self.db_session.commit()

    def info_refresh(self, item_no, max_create_at=None, refresh_type=None):
        refresh_type = refresh_type[6:] if refresh_type.startswith("grant_") else refresh_type
        return getattr(self, 'get_{0}'.format(refresh_type))(item_no)

    def update_task_next_run_at_forward_by_order_no(self, order_no):
        clean_task = self.db_session.query(Task).filter(Task.task_order_no == order_no).all()
        if not clean_task:
            raise ValueError("not found the clean_task info with clean_task'id: {0}".format(order_no))
        for task in clean_task:
            task.task_next_run_at = self.get_date(minutes=1)
            self.db_session.add(task)
        self.db_session.commit()

    def run_task_by_task_order_no(self, item_no):
        self.update_task_next_run_at_forward_by_order_no(item_no)
        url = self.task_url.format(item_no)
        ret = Http.http_get(url)
        return ret

    def operate_action(self, item_no, extend, op_type, table_name, run_date):
        table_name = table_name[6:] if table_name.startswith('grant_') else table_name
        extend_name = '{0}_create_at'.format(table_name)
        max_create_at = extend[extend_name] if extend_name in extend else None
        max_create_at = extend['create_at'] if max_create_at is None else None
        real_req = {}
        if op_type == 'run_task_by_task_order_no':
            real_req['order_no'] = item_no
        elif op_type == 'run_task_by_id':
            real_req['task_id'] = extend['id']
        elif op_type == 'run_msg_by_id':
            real_req['msg_id'] = extend['id']
        if op_type == "del_row_data":
            real_req['del_id'] = extend['id']
            real_req['item_no'] = item_no
            real_req['refresh_type'] = table_name
            real_req['max_create_at'] = max_create_at
        ret = getattr(self, op_type)(**real_req)
        if max_create_at is not None:
            return self.info_refresh(item_no, max_create_at, refresh_type=table_name)
        return ret

    def get_grant_info(self, item_no):
        ret = {}
        ret.update(self.get_task(item_no))
        ret.update(self.get_sendmsg(item_no))
        ret.update(self.get_asset_loan_record(item_no))
        return ret

    def get_task(self, item_no):
        task = self.db_session.query(Task).filter(Task.task_order_no == item_no).order_by(desc(Task.task_id)).all()
        return {'grant_task': list(map(lambda x: x.to_spec_dict, task))}

    def get_router_capital_plan(self, item_no):
        router_capital_plan = self.db_session.query(RouterCapitalPlan).order_by(
            desc(RouterCapitalPlan.router_capital_plan_date)).all()
        return {'router_capital_plan': list(map(lambda x: x.to_spec_dict, router_capital_plan))}

    def get_capital_account(self, item_no):
        capital_account = self.db_session.query(CapitalAccount).filter(CapitalAccount.capital_account_item_no == item_no).all()
        return {'capital_account': list(map(lambda x: x.to_spec_dict, capital_account))}

    def get_asset_tran(self, item_no):
        asset_tran = self.db_session.query(AssetTran).filter(AssetTran.asset_tran_asset_item_no == item_no).all()
        return {'asset_tran': list(map(lambda x: x.to_spec_dict, asset_tran))}

    def get_sendmsg(self, item_no):
        msg = self.db_session.query(Sendmsg).filter(Sendmsg.sendmsg_order_no == item_no).order_by(
            desc(Sendmsg.sendmsg_id)).all()
        return {'grant_sendmsg': list(map(lambda x: x.to_spec_dict, msg))}

    def get_asset_loan_record(self, item_no):
        asset_loan_record = self.db_session.query(AssetLoanRecord).filter(
            AssetLoanRecord.asset_loan_record_asset_item_no == item_no).order_by(
            desc(AssetLoanRecord.asset_loan_record_id)).all()
        return {'asset_loan_record': list(map(lambda x: x.to_spec_dict, asset_loan_record))}

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
        loan_channel = loan_asset_info["data"]["asset"]["loan_channel"]
        req_data = {
            "channel": loan_channel,
            "grant_date": "",
            "period_count": loan_period_count,
            "principal": loan_principal_amount
        }
        ret = Http.http_post('http://framework-test.k8s-ingress-nginx.kuainiujinke.com/gbiz-calc-noloan-amount',
                             req_data)
        rongdan = ret['data']['apr融担小单金额']
        lieyin = ret['data']['irr权益小单金额']
        rongdan_irr = ret['data']['irr融担小单金额']
        noloan_amount_dict = dict(zip(("rongdan", "rongdan_irr", "lieyin"),
                                      (rongdan, rongdan_irr, lieyin)))
        return noloan_amount_dict[noloan_source_type] / 100

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

    def copy_asset(self, item_no):
        asset = self.db_session.queyr(Asset).filter(Asset.asset_item_no == item_no).first()
        asset_tran = self.db_session.queyr(AssetTran).filter(AssetTran.asset_tran_asset_item_no == item_no).all()
        task = self.db_session.queyr(Task).filter(Task.task_order_no == item_no).all()
        msg = self.db_session.queyr(Sendmsg).filter(Sendmsg.sendmsg_order_no == item_no).all()
        asset_loan_record = self.db_session.queyr(AssetLoanRecord).filter(AssetLoanRecord.asset_loan_record_asset_item_no == item_no).all()
        capital_asset = self.db_session.queyr(CapitalAsset).filter(CapitalAsset.capital_asset_item_no == item_no).frist()
        capital_tran = self.db_session.queyr(CapitalTransaction).filter(CapitalTransaction.capital_transaction_item_no == item_no).all()
        return None

    def get_asset_item_info(self, channel, source_type, from_system_name, item_no=None):
        item_no = item_no if item_no else self.create_item_no()
        source_type_list = CHANNEL_SOURCE_TYPE_DICT[channel] if channel in CHANNEL_SOURCE_TYPE_DICT \
            else CHANNEL_SOURCE_TYPE_DICT['yixin_hengrun']
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

    def manual_asset_import(self, channel, source_type, from_system_name, element, count, amount):
        item_no, x_item_no, x_rights, source_type, x_source_type, x_right, from_system = \
            self.get_asset_item_info(channel, source_type, from_system_name)
        element = self.get_four_element() if element == 1 else element
        ref_order_no = '{0}_noloan'.format(item_no)
        from_system = FROM_SYSTEM_DICT[from_system_name]
        self.asset_import(item_no, channel, element, count, amount, source_type,
                                                  from_system_name, from_system, ref_order_no)
        self.add_asset(item_no, 0)

    def add_asset(self, name, source_type):
        grant_asset = self.check_item_exist(name)
        if grant_asset is None:
            return '没有该资产'
        exist_asset = AutoAsset.query.filter(AutoAsset.asset_name == name, AutoAsset.asset_env == self.env).first()
        if exist_asset:
            return '该资产已经存在'
        asset = AutoAsset()
        asset.asset_create_at = self.get_date(fmt="%Y-%m-%d", is_str=True)
        asset.asset_channel = grant_asset.asset_loan_channel
        asset.asset_descript = ''
        asset.asset_name = name
        asset.asset_period = grant_asset.asset_period_count
        asset.asset_env = self.env
        asset.asset_type = source_type
        asset.asset_country = self.country
        asset.asset_source_type = 1
        asset.asset_days = int(grant_asset.asset_product_category)
        db.session.add(asset)
        db.session.flush()

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

    def capital_asset_success(self, capital_asset):
        Http.http_post(self.repay_capital_asset_import_url, capital_asset)
        resp = Http.http_post(self.biz_central.capital_asset_import_url, capital_asset)
        self.biz_central.run_central_task_by_task_id(resp['data'])


