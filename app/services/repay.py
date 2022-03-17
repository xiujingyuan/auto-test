import copy

from sqlalchemy import desc

from app.common.http_util import Http
from app.model.Model import AutoAsset
from app.services import BaseService, Asset, Task, AssetExtend, time_print, CapitalAsset, AssetTran, CapitalTransaction


class RepayBaseService(BaseService):
    def __init__(self, country, env, run_env, check_req, return_req):
        super(RepayBaseService, self).__init__(country, 'repay', env, run_env, check_req, return_req)
        self.decrease_url = self.repay_host + "/asset/bill/decrease"
        self.offline_recharge_url = self.repay_host + "/account/recharge-encrypt"
        self.offline_repay_url = self.repay_host + "/asset/repayPeriod"
        self.active_repay_url = self.repay_host + "/paydayloan/repay/combo-active-encrypt"
        self.fox_repay_url = self.repay_host + "/fox/manual-withhold-encrypt"
        self.refresh_url = self.repay_host + "/asset/refreshLateFee"
        self.send_msg_url = self.repay_host + "/paydayloan/repay/bindSms"
        self.pay_svr_callback_url = self.repay_host + "/paysvr/callback"
        self.reverse_url = self.repay_host + "/asset/repayReverse"
        self.withdraw_success_url = self.repay_host + "/sync/asset-withdraw-success"
        self.run_task_id_url = self.repay_host + '/task/run?taskId={0}'
        self.run_msg_id_url = self.repay_host + '/msg/run?msgId={0}'
        self.run_task_order_url = self.repay_host + '/task/run?orderNo={0}'
        self.bc_query_asset_url = self.repay_host + '/paydayloan/projectRepayQuery'

    def get_auto_asset(self, channel, period, days=0):
        asset_list = AutoAsset.query.filter(AutoAsset.asset_period == period,
                                            AutoAsset.asset_channel == channel,
                                            AutoAsset.asset_days == days,
                                            AutoAsset.asset_env == self.env,
                                            AutoAsset.asset_create_at >= self.get_date(is_str=True, days=-7)) \
            .order_by(desc(AutoAsset.asset_id)).all()
        asset_list = list(map(lambda x: x.to_spec_dict, asset_list))
        ret = {'assets': asset_list}
        if asset_list:
            ret_info = self.get_asset_info(asset_list[0]['name'])
            ret.update(ret_info)
        return ret

    def add_asset(self, name, source_type):
        grant_asset = self.grant.check_item_exist(name)
        repay_asset = self.check_item_exist(name)
        if grant_asset is None and repay_asset is None:
            return '没有该资产'
        exist_asset = AutoAsset.query.filter(AutoAsset.asset_name == name, AutoAsset.asset_env == self.env).first()
        if exist_asset:
            return '该资产已经存在'
        asset = AutoAsset()
        asset.asset_create_at = self.get_date(fmt="%Y-%m-%d", is_str=True)
        asset.asset_channel = repay_asset.asset_loan_channel if repay_asset is not None else\
            grant_asset.asset_loan_channel
        asset.asset_descript = ''
        asset.asset_name = name
        asset.asset_period = repay_asset.asset_period_count if repay_asset is not None else \
            grant_asset.asset_loan_channel
        asset.asset_env = self.env
        asset.asset_type = source_type
        asset.asset_source_type = 1
        asset.asset_days = int(repay_asset.asset_product_category)
        db.session.add(asset)
        db.session.flush()
        return self.get_auto_asset(repay_asset.asset_loan_channel, repay_asset.asset_period_count,
                                   days=int(repay_asset.asset_product_category))

    def refresh_late_fee(self, item_no):
        if not item_no:
            return
        request_data = {
            "from_system": "Biz",
            "type": "RbizRefreshLateInterest",
            "key": self.__create_req_key__(item_no, prefix='Refresh'),
            "data": {
                "asset_item_no": item_no
            }
        }
        asset = self.db_session.query(Asset).filter(Asset.asset_item_no == item_no).first()
        if not asset:
            raise ValueError("not found the asset, check env!")
        resp = Http.http_post(self.refresh_url, request_data)
        asset_x = self.get_no_loan(item_no)
        if asset_x:
            request_x_data = copy.deepcopy(request_data)
            request_x_data['key'] = self.__create_req_key__(asset_x, prefix='Refresh')
            request_x_data['data']['asset_item_no'] = asset_x
            resp_x = Http.http_post(self.refresh_url, request_x_data)
            self.run_task_by_type_and_order_no('AssetAccountChangeNotify', asset_x)
            self.run_msg_by_order_no(asset_x, 'AssetChangeNotifyMQ')
            self.run_msg_by_order_no(asset_x, 'assetFoxSync')
        self.run_task_by_type_and_order_no('AssetAccountChangeNotify', item_no)
        self.run_msg_by_order_no(item_no, 'AssetChangeNotifyMQ')
        self.run_msg_by_order_no(item_no, 'assetFoxSync')
        return [request_data, request_x_data] if asset_x else [request_data], self.refresh_url, [resp, resp_x] \
            if asset_x else [resp]

    def run_task_by_type_and_order_no(self, task_type, order_no):
        task_list = self.db_session.query(Task).filter(Task.task_type == task_type,
                                                       Task.task_order_no == order_no,
                                                       Task.task_status == 'open').all()
        for task in task_list:
            self.run_task_by_id(task.task_id)

    @time_print
    def sync_plan_to_bc(self, item_no):
        now = self.get_date(is_str=True, fmt='%Y-%m-%d')
        self.run_xxl_job('syncAssetToBiz', param={'assetItemNo': [item_no]})
        self.run_msg_by_order_no(item_no, 'asset_change_fix_status')
        self.biz_central.run_central_msg_by_order_no(item_no, 'AssetChangeNotify', max_create_at=now)

    def get_no_loan(self, item_no):
        item_no_x = ''
        asset_extend = self.db_session.query(AssetExtend).filter(
            AssetExtend.asset_extend_asset_item_no == item_no,
            AssetExtend.asset_extend_type == 'ref_order_no'
        ).first()
        if asset_extend:
            ref_order_type = self.db_session.query(AssetExtend).filter(
                AssetExtend.asset_extend_asset_item_no == item_no,
                AssetExtend.asset_extend_type == 'ref_order_type'
            ).first()
            item_no_x = asset_extend.asset_extend_val if ref_order_type and \
                                                         ref_order_type.asset_extend_val != 'lieyin' else ''
        return item_no_x

    @time_print
    def change_asset(self, item_no, item_no_rights, advance_day, advance_month, interval_day=30):
        item_no_tuple = tuple(item_no.split(',')) if ',' in item_no else (item_no,)
        for index, item in enumerate(item_no_tuple):

            item_no_x = self.get_no_loan(item)
            item_tuple = tuple([x for x in [item, item_no_x, item_no_rights] if x])
            asset_list = self.db_session.query(Asset).filter(Asset.asset_item_no.in_(item_tuple)).all()
            if not asset_list:
                raise ValueError('not found the asset, check the env!')
            asset_tran_list = self.db_session.query(AssetTran).filter(
                AssetTran.asset_tran_asset_item_no.in_(item_tuple),
                AssetTran.asset_tran_type).order_by(AssetTran.asset_tran_period).all()

            capital_asset = self.db_session.query(CapitalAsset).filter(
                CapitalAsset.capital_asset_item_no == item).first()
            capital_tran_list = self.db_session.query(CapitalTransaction).filter(
                CapitalTransaction.capital_transaction_item_no == item).all()
            self.change_asset_due_at(asset_list, asset_tran_list, capital_asset, capital_tran_list, advance_day,
                                     advance_month, interval_day)
            if self.country == 'china':
                self.biz_central.change_asset(item, item_no_x, item_no_rights, advance_day, advance_month)
        self.refresh_late_fee(item_no)
        self.refresh_late_fee(item_no_rights)
        self.sync_plan_to_bc(item_no)
        return "修改完成"


class OverseaRepayService(RepayBaseService):
        def __init__(self, country, env, run_env, check_req=False, return_req=False):
            super(OverseaRepayService, self).__init__(country, env, run_env, check_req, return_req)
            self.encrypt_url = 'http://47.101.30.198:8081/encrypt/'

        def get_four_element(self):
            four_element = super(OverseaRepayService, self).get_four_element()
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

        def auto_loan(self, channel, count, day, amount, source_type, from_system='香蕉', from_app=''):
            element = self.get_four_element_global(id_num_begin='110')
            item_no, asset_info = self.grant.asset_import(channel, count, day, "day", amount, from_system, from_app,
                                                          source_type, element, "")
            self.grant.loan_to_success(item_no)
            x_item_no, asset_info_noloan = self.grant.asset_import_noloan(asset_info)
            # 判断是否有小单
            if x_item_no:
                self.noloan_to_success(x_item_no)
            self.add_asset(item_no, 0)
            return item_no, x_item_no

        @time_print
        def sync_plan_to_bc(self, item_no):
            self.run_xxl_job('manualSyncAsset', param={"assetItemNo": [item_no]})
            self.run_task_by_order_no(item_no, 'AssetAccountChangeNotify')
            self.run_msg_by_order_no(item_no, 'AssetChangeNotifyMQ')