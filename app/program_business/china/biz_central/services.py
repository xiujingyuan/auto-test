from sqlalchemy import desc

from app.program_business import BaseAuto
from app.common.http_util import Http
import json

from app.program_business.china.biz_central.Model import CentralTask, CentralSendMsg, Asset, AssetTran, \
    CapitalAsset, CapitalTransaction, WithholdHistory, WithholdResult, CapitalNotify, CapitalSettlementDetail


class ChinaBizCentralAuto(BaseAuto):

    def __init__(self, env, run_env, check_req=False, return_req=False):
        super(ChinaBizCentralAuto, self).__init__('china', 'biz-central', env, run_env, check_req, return_req)
        self.central_task_url = self.biz_host + "/job/runTaskById?id={0}"
        self.asset_import_url = self.biz_host + "/asset/import"
        self.capital_asset_import_url = self.biz_host + "/capital-asset/import"

    def asset_import(self, req_data):
        ret = Http.http_post(self.asset_import_url, req_data)
        if not ret['code'] == 0:
            raise ValueError("import asset error, {0}".format(ret['message']))
        central_task_id = ret['data']
        if central_task_id is not None:
            req = self.run_central_task_by_task_id(central_task_id)
            if not req['code'] == 0:
                raise ValueError("run asset import task error ,{0}".format(req['message']))
        return ret

    def get_task_msg(self, request_no, serial_no, id_num, item_no):
        task_order_no = tuple(request_no + serial_no + [id_num['card_acc_id_num_encrypt'], item_no])
        task_list = self.db_session.query(CentralTask).filter(
            CentralTask.task_order_no.in_(task_order_no)).order_by(desc(CentralTask.task_id)).all()
        msg_list = self.db_session.query(CentralSendMsg).filter(
            CentralSendMsg.sendmsg_order_no.in_(task_order_no)).order_by(desc(CentralSendMsg.sendmsg_id)).all()
        task_list = list(map(lambda x: x.to_spec_dict, task_list))
        msg_list = list(map(lambda x: x.to_spec_dict, msg_list))
        return dict(zip(('task', 'msg'), (task_list, msg_list)))

    def get_capital_info(self, item_no):
        capital_asset = self.db_session.query(CapitalAsset).filter(
            CapitalAsset.capital_asset_item_no == item_no).first()
        capital_tran_list = self.db_session.query(CapitalTransaction).filter(
            CapitalTransaction.capital_transaction_asset_item_no == item_no).all()
        capital_notify_list = self.db_session.query(CapitalNotify).filter(
            CapitalNotify.capital_notify_asset_item_no == item_no).order_by(desc(CapitalNotify.capital_notify_id)).all()
        capital_detail_list = self.db_session.query(CapitalSettlementDetail).filter(
            CapitalSettlementDetail.channel == capital_asset.capital_asset_channel)\
            .order_by(desc(CapitalSettlementDetail.id)).all()
        capital_tran_list = list(map(lambda x: x.to_spec_dict, capital_tran_list))
        capital_notify_list = list(map(lambda x: x.to_spec_dict, capital_notify_list))
        capital_detail_list = list(map(lambda x: x.to_spec_dict, capital_detail_list))
        return dict(zip(('capital_tran', 'capital_notify', 'capital_detail'),
                        (capital_tran_list, capital_notify_list, capital_detail_list)))

    def sync_withhold_to_history(self, item_no):
        withhold_results = self.db_session.query(WithholdResult).filter(
            WithholdResult.withhold_result_asset_item_no == item_no).all()
        withhold_histories = []
        for withhold_result in withhold_results:
            withhold_history = WithholdHistory()
            for key in withhold_result.__dict__:
                if not key.startswith('_') and hasattr(withhold_history, key):
                    setattr(withhold_history, key, getattr(withhold_result, key))
            withhold_history.withhold_history_sync_at = self.get_date(is_str=True)
            withhold_histories.append(withhold_history)
        self.db_session.add_all(withhold_histories)
        self.db_session.commit()

    def change_asset(self, item_no, item_no_x, item_no_rights, advance_day, advance_month):
        item_tuple = tuple([x for x in [item_no, item_no_x, item_no_rights] if x])
        asset_list = self.db_session.query(Asset).filter(Asset.asset_item_no.in_(item_tuple)).all()
        capital_asset = self.db_session.query(CapitalAsset).filter(
            CapitalAsset.capital_asset_item_no == item_no).first()
        asset_tran_list = self.db_session.query(AssetTran).filter(
            AssetTran.asset_tran_asset_item_no.in_(item_tuple)).all()
        capital_tran_list = self.db_session.query(CapitalTransaction).filter(
            CapitalTransaction.capital_transaction_asset_item_no == item_no).all()
        self.change_asset_due_at(asset_list, asset_tran_list, capital_asset, capital_tran_list, advance_day,
                                 advance_month)

    def update_central_task_next_run_at_forward_by_task_id(self, task_id):
        central_task = self.db_session.query(CentralTask).filter(CentralTask.task_id == task_id).first()
        if not central_task:
            raise ValueError("not found the central_task info with central_task'id: {0}".format(task_id))
        if central_task.task_status == 'close':
            if json.loads(central_task.task_response_data)['code'] == 0:
                print('task is run with success')
                return
            else:
                raise ValueError("task is run but not success, with response is :{0}".format(
                    central_task.task_response_data))
        central_task.task_next_run_at = self.get_date(minutes=1)
        self.db_session.add(central_task)
        self.db_session.commit()

    def run_central_task_by_task_id(self, task_id):
        self.update_central_task_next_run_at_forward_by_task_id(task_id)
        ret = Http.http_get(self.central_task_url.format(task_id))
        if not ret['code'] == 0:
            raise ValueError('the central task run error, {0}'.format(ret['message']))
        return ret

    def get_asset_info(self, item_no):
        asset = self.db_session.query(Asset).filter(Asset.asset_item_no == item_no).first()
        if not asset:
            raise ValueError("not found the asset info in biz")
        return asset

    @staticmethod
    def get_item_no(msg):
        msg_list = msg.sendmsg_order_no.replace('early_settlement', 'earlysettlement').split("_")
        if msg_list[0] not in ('normal', 'advance', 'overdue', 'compensate', 'earlysettlement', 'offline', 'buyback',
                               'chargeback'):
            item_no = "_".join(msg_list[0:-3]) if len(msg_list) > 4 else msg_list[0]
            msg_type = msg_list[-3]
        else:
            item_no = "_".join(msg_list[1:-2]) if len(msg_list) > 4 else msg_list[1]
            msg_type = msg_list[0]
        return item_no, msg_type, msg_list[-2], msg_list[-1]

    def create_push_dcs_task(self):
        central_send_msg_list = self.db_session.query(CentralSendMsg).filter(
            CentralSendMsg.sendmsg_type == 'CapitalTransactionClearing').all()
        old_data = {}
        max_msg_id = 0
        for index, msg in enumerate(central_send_msg_list):
            if index == 0:
                max_msg_id = msg.sendmsg_id
            item_no, msg_type, start_period, end_period = self.get_item_no(msg)
            old_data["_".join((item_no, msg_type.replace('early_settlement', 'earlysettlement'),
                               start_period, end_period))] = msg['sendmsg_content']
            task_id = self.add_re_push_dcs_task(item_no, start_period, end_period)
            if task_id is None:
                raise ValueError('task id is error!')
            self.run_central_task_by_task_id(task_id)
        all_new_msg = self.db_session.query(CentralSendMsg).filter(
            CentralSendMsg.sendmsg_type == 'CapitalTransactionClearing').all()
        for msg in all_new_msg:
            if msg.sendmsg_id < max_msg_id:
                continue
            item_no, msg_type, start_period, end_period = self.get_item_no(msg)
            msg_key = msg.sendmsg_order_no if msg.sendmsg_order_no in old_data \
                else "_".join((msg_type.replace('early_settlement', 'earlysettlement'), item_no,
                               start_period,
                               end_period))
            if msg_key in old_data:
                item_info = self.db_session.query(Asset).filter(Asset.asset_item_no == item_no).first()
                if item_info:
                    print(msg_key, item_info.asset_loan_channel,
                          self.compare_data(123, json.loads(old_data[msg.sendmsg_order_no]),
                                            json.loads(msg.sendmsg_content), [], 0))
                else:
                    print('not fount the item {0}'.format(item_no))
            else:
                print('not fount the order no {0}'.format(msg['sendmsg_order_no']))