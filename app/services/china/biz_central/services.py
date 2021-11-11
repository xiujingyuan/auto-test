import time

from sqlalchemy import desc, or_

from app.services import BaseService
from app.common.http_util import Http
import json

from app.services.china.biz_central.Model import CentralTask, CentralSendMsg, Asset, AssetTran, \
    CapitalAsset, CapitalTransaction, WithholdHistory, WithholdResult, CapitalNotify, CapitalSettlementDetail, Holiday
from app.test_cases import CaseException


class ChinaBizCentralService(BaseService):

    def __init__(self, env, run_env, check_req=False, return_req=False):
        super(ChinaBizCentralService, self).__init__('china', 'biz_central', env, run_env, check_req, return_req)
        self.central_task_url = self.biz_host + "/job/runTaskById?id={0}"
        self.central_msg_url = self.biz_host + "/job/sendMsgById?id={0}"
        self.asset_import_url = self.biz_host + "/asset/import"
        self.capital_asset_import_url = self.biz_host + "/capital-asset/import"
        self.central_task_date_url = self.biz_host + "/job/runTaskWithDate?id={0}&date={1}"
        self.refresh_holiday_url = self.biz_host + "/job/refreshholiday"
        self.run_job_by_date_url = self.biz_host + "/job/runWithDate?jobType={0}&param={1}&date={2}"

    def set_capital_tran_status(self, item_no, period, operate_type='grant', status='finished', capital_notify=False):
        capital_tran_list = self.db_session.query(CapitalTransaction).filter(
            CapitalTransaction.capital_transaction_asset_item_no == item_no,
            CapitalTransaction.capital_transaction_period < period).all()
        for capital_tran in capital_tran_list:
            capital_tran.capital_transaction_operation_type = operate_type
            capital_tran.capital_transaction_status = status
        if capital_notify and operate_type != 'grant' and period > 1:
            notify_list = []
            channel = capital_tran_list[0].capital_transaction_channel
            for index in range(1, period - 1):
                notify = CapitalNotify()
                notify.capital_notify_channel = channel
                notify.capital_notify_period_start = index
                notify.capital_notify_period_end = index
                notify.capital_notify_asset_item_no = item_no
                notify.capital_notify_plan_at = self.get_date()
                notify.capital_notify_push_serial = 'test_{0}'.format(self.get_date(fmt='%Y%m%d%H%M%S'))
                notify.capital_notify_to_system = channel
                notify.capital_notify_status = 'success'
                notify.capital_notify_type = operate_type
                notify_list.append(notify)
            self.db_session.add_all(notify_list)

        self.db_session.add_all(capital_tran_list)
        self.db_session.flush()
        self.db_session.commit()

    def run_capital_push(self, plan_at):
        self.run_xxl_job('capitalNotifyPushJob', plan_at)

    def run_compensate_push(self, plan_at):
        self.run_xxl_job('generateCompensateJob', plan_at)

    def run_guarantor_push(self, plan_at):
        self.run_xxl_job('guarantorPushJob', plan_at)

    def delete_row_data(self, del_id, del_type):
        obj = eval(del_type.title().replace("_", ""))
        except_id = 'id' if del_type == 'capital_settlement_detail' else '{0}_id'.format(del_type)
        self.db_session.query(obj).filter(getattr(obj, except_id) == del_id).delete()
        self.db_session.flush()
        self.db_session.commit()

    def add_central_task(self, task, is_run=True):
        new_task = CentralTask()
        for key, value in task.items():
            if key != 'task_id':
                setattr(new_task, key, value)
        new_task.task_next_run_at = self.get_date(is_str=True)
        new_task.task_status = 'open'
        self.db_session.add(new_task)
        self.db_session.flush()
        self.db_session.commit()
        if is_run:
            ret = self.run_central_task_by_task_id(new_task.task_id)
        return new_task.task_id

    def run_xxl_job(self, job_type, run_date):
        param = self.xxljob.get_job_info(job_type)[0]['executorParam']
        param = json.dumps(json.loads(param))
        url = self.run_job_by_date_url.format(job_type, param, run_date)
        return Http.http_get(url)

    def add_and_update_holiday(self, date_time, status):
        get_date = self.db_session.query(Holiday).filter(Holiday.holiday_date == date_time).first()
        if not get_date:
            get_date = Holiday()
            get_date.holiday_date = date_time
            get_date.holiday_status = status
        else:
            get_date.holiday_status = status
        self.db_session.add(get_date)
        self.db_session.commit()
        time.sleep(1)
        return Http.http_get(self.refresh_holiday_url)

    def asset_import(self, req_data):
        ret = Http.http_post(self.asset_import_url, req_data)
        central_task_id = ret['data']
        if central_task_id is not None:
            self.run_central_task_by_task_id(central_task_id)
        return ret

    def get_loan_asset_task(self, item_no):
        task_list = self.db_session.query(CentralTask).filter(
            CentralTask.task_order_no == item_no,
            CentralTask.task_type.in_(('AssetImport', 'CapitalAssetImport', 'AssetWithdrawSuccess')))\
            .order_by(CentralTask.task_id).all()
        return list(map(lambda x: x.to_dict, task_list))

    def get_task_msg(self, task_order_no, channel, item_no, max_create_at):
        ret = {}
        task_dict = self.get_task(task_order_no, max_create_at, channel)
        msg_dict = self.get_msg(item_no,  max_create_at)
        ret.update(task_dict)
        ret.update(msg_dict)
        return ret

    def get_task(self, task_order_no, channel=None, max_create_at=None):
        max_create_at = max_create_at if max_create_at is not None else self.get_date(is_str=True, days=-7)
        task_order_no = tuple(list(task_order_no) + [channel] + ['settle_detail_{0}_{1} 00:00:00'.format(channel, self.get_date(fmt='%Y-%m-%d', is_str=True))]) if channel is not None else task_order_no
        task_list = self.db_session.query(CentralTask).filter(CentralTask.task_order_no.in_(task_order_no),
                                                              CentralTask.task_create_at >= max_create_at)\
            .order_by(desc(CentralTask.task_id)).all()
        task_list = list(map(lambda x: x.to_spec_dict, task_list))
        return {'biz_task': task_list}

    def get_msg(self, item_no, max_create_at=None):
        max_create_at = max_create_at if max_create_at is not None else self.get_date(is_str=True, days=-7)
        msg_list = self.db_session.query(CentralSendMsg). \
            filter(CentralSendMsg.sendmsg_order_no.like('{0}%'.format(item_no)),
                   CentralSendMsg.sendmsg_create_at >= max_create_at) \
            .order_by(desc(CentralSendMsg.sendmsg_id)).all()
        msg_list = list(map(lambda x: x.to_spec_dict, msg_list))
        return {'biz_msg': msg_list}

    def get_capital_info(self, item_no, channel):
        ret = {}
        capital = self.get_capital(item_no)
        capital_tran = self.get_capital_tran(item_no)
        capital_notify = self.get_capital_notify(item_no)
        capital_detail = self.get_capital_detail(channel)
        ret.update(capital)
        ret.update(capital_tran)
        ret.update(capital_notify)
        ret.update(capital_detail)
        return ret

    def add_compensate(self, item_no, period):
        asset_tran = self.db_session.query(AssetTran).filter(AssetTran.asset_tran_asset_item_no == item_no,
                                                             AssetTran.asset_tran_period == period).all()
        principal = list(filter(lambda x: x.asset_tran_type == 'repayprincipal', asset_tran))[0].asset_tran_amount
        interest = list(filter(lambda x: x.asset_tran_type == 'repayinterest', asset_tran))[0].asset_tran_amount
        due_at = asset_tran[0].asset_tran_due_at
        return self.add_capital_settlement_detail(item_no, period, due_at, principal, interest, 'compensate')

    def add_buyback(self, item_no, period):
        asset_tran = self.db_session.query(AssetTran).filter(AssetTran.asset_tran_asset_item_no == item_no,
                                                             AssetTran.asset_tran_period >= period).all()
        principal = sum([x.asset_tran_amount for x in (filter(
            lambda x: x.asset_tran_type == 'repayprincipal', asset_tran))])
        interest = list(filter(lambda x: x.asset_tran_type == 'repayinterest', asset_tran))[0].asset_tran_amount
        due_at = asset_tran[0].asset_tran_due_at
        return self.add_capital_settlement_detail(item_no, period, due_at, principal, interest, 'buyback')

    def add_capital_settlement_detail(self, item_no, period, due_at, principal, interest, settlement_type):
        asset = self.db_session.query(Asset).filter(Asset.asset_item_no == item_no).first()
        if not asset:
            raise ValueError('not fount the asset with item_no is :{0}'.format(asset))
        compensate = self.db_session.query(CapitalSettlementDetail).filter(
            CapitalSettlementDetail.asset_item_no == item_no, CapitalSettlementDetail.period == period,
            CapitalSettlementDetail.capital_tran_process_status == 'ready').first()
        if not compensate:
            if self.cal_days(due_at, self.get_date()) < 0:
                raise ValueError('not overdue with asset is :{0}, period is :{1}'.format(item_no, period))

            compensate = CapitalSettlementDetail()
            compensate.asset_item_no = item_no
            compensate.period = period

            compensate.channel = asset.asset_loan_channel
            compensate.asset_granted_principal_amount = asset.asset_granted_principal_amount_f
            compensate.repay_total_amount = 1
            compensate.repay_principal = principal
            compensate.repay_interest = interest
            compensate.contract_start_date = asset.asset_actual_grant_at
            compensate.contract_end_date = asset.asset_due_at
            compensate.type = settlement_type
            compensate.capital_tran_process_status = 'open'
        compensate.repay_date = due_at
        self.db_session.add(compensate)
        self.db_session.commit()

    def get_capital(self, item_no):
        capital_asset = self.db_session.query(CapitalAsset).filter(
            CapitalAsset.capital_asset_item_no == item_no).first().to_spec_dict
        return {"biz_capital_asset": [capital_asset]}

    def get_capital_tran(self, item_no):
        capital_tran_list = self.db_session.query(CapitalTransaction).filter(
            CapitalTransaction.capital_transaction_asset_item_no == item_no).all()
        capital_tran_list = list(map(lambda x: x.to_spec_dict, capital_tran_list))
        return {"biz_capital_tran": capital_tran_list}

    def get_capital_notify(self, item_no, max_create_at):
        capital_notify_list = self.db_session.query(CapitalNotify).filter(
            CapitalNotify.capital_notify_asset_item_no == item_no,
            CapitalNotify.capital_notify_create_at >= max_create_at)\
            .order_by(desc(CapitalNotify.capital_notify_id)).all()
        capital_notify_list = list(map(lambda x: x.to_spec_dict, capital_notify_list))
        return {"biz_capital_notify": capital_notify_list}

    def get_capital_detail(self, channel):
        capital_detail_list = self.db_session.query(CapitalSettlementDetail).filter(
            CapitalSettlementDetail.channel == channel) \
            .order_by(desc(CapitalSettlementDetail.id)).all()
        capital_detail_list = list(map(lambda x: x.to_spec_dict, capital_detail_list))
        return {"biz_capital_settlement_detail": capital_detail_list}

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
        return 'success'

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

    def update_central_task_next_run_at_forward_by_task_id(self, task_id, re_run):
        central_task = self.db_session.query(CentralTask).filter(CentralTask.task_id == task_id).first()
        if not central_task:
            raise ValueError("not found the central_task info with central_task'id: {0}".format(task_id))
        if re_run:
            central_task.task_next_run_at = self.get_date(minutes=1)
            central_task.task_status = 'open'
            self.db_session.add(central_task)
            self.db_session.commit()
            return True
        if central_task.task_status == 'close':
            if json.loads(central_task.task_response_data)['code'] == 0:
                print('task is run with success')
                return None
            else:
                raise ValueError("task is run but not success, with response is :{0}".format(
                    central_task.task_response_data))
        elif central_task.task_status == 'open':
            return True
        return None

    def update_central_msg_next_run_at_forward_by_msg_id(self, msg_id):
        central_msg = self.db_session.query(CentralSendMsg).filter(CentralSendMsg.sendmsg_id == msg_id).first()
        if not central_msg:
            raise ValueError("not found the central_msg info with central_msg'id: {0}".format(msg_id))
        central_msg.sendmsg_next_run_at = self.get_date(minutes=1)
        central_msg.sendmsg_status = 'open'
        self.db_session.add(central_msg)
        self.db_session.commit()

    def run_central_task_by_task_id(self, task_id, run_date=None, re_run=False):
        task = self.update_central_task_next_run_at_forward_by_task_id(task_id, re_run)
        if task is None:
            return '运行中或已执行'
        run_date = self.get_date() if run_date is None else run_date
        url = self.central_task_url.format(task_id) \
            if run_date and (self.cal_days(run_date, self.get_date(is_str=True)) >= 0) \
            else self.central_task_date_url.format(task_id, run_date)
        ret = Http.http_get(url)
        return ret

    def run_task_by_order_no(self, order_no, task_type, status='open', excepts={'code': 0}):
        task_id = self.get_task_info(order_no, task_type, status=status)[0].task_id
        return self.run_task_by_id(task_id, excepts=excepts)

    def get_task_info(self, order_no, task_type, status='open'):
        task = self.db_session.query(CentralTask).filter(CentralTask.task_order_no == order_no,
                                                         CentralTask.task_type == task_type,
                                                         CentralTask.task_status == status).first()
        if not task:
            raise CaseException('not found the task!')
        return task

    def get_asset_info(self, item_no):
        while True:
            asset = self.db_session.query(Asset).filter(Asset.asset_item_no == item_no).first()
            if asset:
                break
            time.sleep(1)
        if asset is None:
            raise ValueError("not found the asset info in biz")
        return asset

    def run_central_msg_by_msg_id(self, msg_id):
        self.update_central_msg_next_run_at_forward_by_msg_id(msg_id)
        ret = Http.http_get(self.central_msg_url.format(msg_id))
        return ret

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