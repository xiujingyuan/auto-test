from datetime import datetime

from app.program_business import BaseAuto
from app.common.http_util import Http
from app.program_business.china.biz_central.services import ChinaBizCentralAuto
from app.program_business.china.grant import GRANT_ASSET_IMPORT_URL, FROM_SYSTEM_DICT


class ChinaGrantAuto(BaseAuto):
    def __init__(self, env, run_env, check_req=False, return_req=False):
        super(ChinaGrantAuto, self).__init__('china', 'grant', env, run_env, check_req, return_req)
        self.host_url = "https://kong-api-test.kuainiujinke.com/gbiz{0}".format(env)
        self.biz_central = ChinaBizCentralAuto(env, run_env, check_req, return_req)
        self.asset_import_url = self.host_url + GRANT_ASSET_IMPORT_URL
        self.run_task_id_url = self.host_url + '/task/run?taskId={0}'
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
        asset_info['data']['asset']['grant_at'] = self.get_date()
        asset_info['data']['asset']['loan_channel'] = channel
        asset_info['data']['asset']['source_type'] = source_type
        asset_info['data']['asset']['from_app'] = from_system_name
        asset_info['data']['asset']['source_number'] = ref_order_no
        asset_info['data']['asset']['sub_order_type'] = sub_order_type

    @staticmethod
    def set_asset_repay_card(asset_info, element):
        asset_info['data']['repay_card']['username_encrypt'] = element['data']['user_name_encrypt']
        asset_info['data']['repay_card']['phone_encrypt'] = element['data']['phone_number_encrypt']
        asset_info['data']['repay_card']['individual_idnum_encrypt'] = element['data']['id_number_encrypt']
        asset_info['data']['repay_card']['account_num_encrypt'] = element['data']['bank_code_encrypt']

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
        keys = {"router_load_record_key": item_no + channel,
                "router_load_record_rule_code": channel + "_" + str(count) + "month",
                "router_load_record_principal_amount": amount * 100,
                "router_load_record_status": "routed",
                "router_load_record_channel": channel,
                "router_load_record_sub_type": "multiple",
                "router_load_record_period_count": count,
                "router_load_record_period_type": "month",
                "router_load_record_period_days": "0",
                "router_load_record_sub_order_type": sub_order_type,
                "router_load_record_route_day": self.get_date(fmt="%Y-%m-%d"),
                "router_load_record_idnum": element['data']['id_number_encrypt'],
                "router_load_record_from_system": asset_info['from_system'],
                }
        self.db.insert_router_load_record(**keys)

    def asset_import(self, channel, element, count, amount, from_system_name='香蕉', source_type='', item_no='',
                     borrower_extend_district=None, sub_order_type='', route_uuid=None, insert_router_record=True):
        item_no = item_no if item_no else self.create_item_no()
        from_system, ref_order_no, source_type = self.get_from_system_and_ref(item_no, from_system_name, source_type)
        asset_info = self.db.get_asset_import_info()
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
            self.insert_router_record(item_no, channel, amount, count,sub_order_type ,element, asset_info)

        header = {"Content-Type": "application/json"}
        resp = Http.http_post(self.asset_import_url, asset_info, header)
        if resp['code'] == 0:
            asset_info = self.db.get_asset_import_data_by_item_no(item_no)
        else:
            raise ValueError('资产导入失败', resp.text)

        return item_no, asset_info

    def loan_success(self, item_no):
        self.db.run_task_by_order_no(item_no, "AssetImport")
        req = self.db.get_msg_return_req(item_no, "AssetImportSync")
        req_data = json.loads(req)['body']
        self.biz_central.asset_import(req_data)