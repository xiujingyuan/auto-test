from app.common.assert_util import Assert
from app.program_business import BaseAuto
from app.common.http_util import Http
import json

from app.program_business.china.biz_central.Model import CentralTask, CentralSendMsg, Asset, AssetTran, \
    CapitalAsset, CapitalTransaction


class ChinaBizCentralAuto(BaseAuto):

    def __init__(self, env, run_env, check_req=False, return_req=False):
        super(ChinaBizCentralAuto, self).__init__('china', 'biz-central', env, run_env, check_req, return_req)
        self.host_url = "http://biz-central-{0}.k8s-ingress-nginx.kuainiujinke.com".format(env)
        self.host_url = "http://biz-central-{0}.k8s-ingress-nginx.kuainiujinke.com".format(env)
        self.central_task_url = self.host_url + "/job/runTaskById?id={0}"
        self.asset_import_url = self.host_url + "/asset/import"

    def asset_import(self, req_data):
        ret = Http.http_post(self.asset_import_url, req_data)
        return ret

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
            raise ValueError("not found the central_task info with central_task'id {0}".format(central_task))
        central_task.task_next_run_at = self.get_date(minutes=1)
        self.db_session.add(central_task)
        self.db_session.commit()

    def run_central_task_by_task_id(self, task_id, excepts={'code': 0}):
        self.update_central_task_next_run_at_forward_by_task_id(task_id)
        resp = Http.http_get(self.central_task_url.format(task_id))
        if excepts:
            Assert.assert_match_json(excepts, resp[0], "task运行结果校验不通过，task_id:{0}, return:{1}".format(task_id,
                                                                                                     resp))

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