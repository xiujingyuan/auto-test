import time
from datetime import datetime
from sqlalchemy import desc, or_

from app.common.easy_mock_util import EasyMock
from app.common.log_util import LogUtil
from app.services import BaseService, wait_timeout, time_print
from app.common.http_util import Http
import json

from app.services.china.biz_central import biz_modify_return
from app.services.china.biz_central.Model import CentralTask, CentralSendMsg, Asset, AssetTran, \
    CapitalAsset, CapitalTransaction, WithholdHistory, WithholdResult, CapitalNotify, CapitalSettlementDetail, Holiday
from app.test_cases import CaseException


class ChinaBizCentralService(BaseService):

    def __init__(self, env, run_env, check_req=False, return_req=False):
        self.biz_host = "http://biz-central-{0}.k8s-ingress-nginx.kuainiujinke.com".format(env)
        super(ChinaBizCentralService, self).__init__('china', 'biz_central', env, run_env, check_req, return_req)
        self.central_task_url = self.biz_host + "/job/runTaskById?id={0}"
        self.central_msg_url = self.biz_host + "/job/sendMsgById?id={0}"
        self.asset_import_url = self.biz_host + "/asset/import"
        self.capital_asset_import_url = self.biz_host + "/capital-asset/import"
        self.central_task_date_url = self.biz_host + "/job/runTaskWithDate?id={0}&date={1}"
        self.refresh_holiday_url = self.biz_host + "/job/refreshholiday"
        self.run_job_by_date_url = self.biz_host + "/job/runWithDate?jobType={0}&param={1}&date={2}"
        self.gate_str = 'gate.client.serviceUrl'

    def get_capital_principal(self, item_no, period):
        capital_principal = self.db_session.query(CapitalTransaction.capital_transaction_asset_item_no == item_no,
                                                  CapitalTransaction.capital_transaction_period == period,
                                                  CapitalTransaction.capital_transaction_type == 'principal').first()
        return capital_principal

    def update_service_url(self, mock_name):
        config_name = 'biz-central-{0}.properties'.format(self.env)
        system_config = self.nacos.get_config(config_name, group='SYSTEM')['content']
        easy_mock = EasyMock(mock_name)
        mock_url = '{0}={1}'.format(self.gate_str, easy_mock.get_mock_base_url())
        system_config = system_config.replace(self.gate_str, "#{0}".format(self.gate_str))
        system_config += "\n{0}".format(mock_url)
        self.nacos.update_config(config_name, system_config, group='SYSTEM', types='properties')

    def get_kv(self, channel):
        return json.loads(self.nacos.get_config('{0}_config'.format(channel))['content'])

    @wait_timeout
    def get_capital_notify_info(self, item_no):
        capital_notify = self.db_session.query(CapitalNotify).filter(
            CapitalNotify.capital_notify_asset_item_no == item_no,
            CapitalNotify.capital_notify_status == 'open').all()
        return capital_notify

    @wait_timeout
    def get_capital_notify_info_by_id(self, capital_notify_id):
        capital_notify = self.db_session.query(CapitalNotify).filter(
            CapitalNotify.capital_notify_id == capital_notify_id).first()
        return capital_notify

    def get_system_url(self):
        system_config = self.nacos.get_config('biz-central-{0}.properties'.format(self.env), group='SYSTEM')
        for content in system_config['content'].split("\n"):
            if content.startswith(self.gate_str):
                service_url = content.strip().replace(self.gate_str, '')[1:]
                break
        return service_url

    def check_and_add_push_channel(self, channel):
        account_import_config = json.loads(self.nacos.get_config('account_import_config')['content'])
        if 'newProgramChannels' not in account_import_config:
            account_import_config['newProgramChannels'] = ['channel']
            self.nacos.update_config('account_import_config', account_import_config)
        elif channel not in account_import_config['newProgramChannels']:
            account_import_config['newProgramChannels'].append(channel)
            self.nacos.update_config('account_import_config', json.dumps(account_import_config))

    def set_capital_tran_status(self, item_no, period, operate_type='grant', status='finished', capital_notify=False):
        capital_tran_list = self.db_session.query(CapitalTransaction).filter(
            CapitalTransaction.capital_transaction_asset_item_no == item_no,
            CapitalTransaction.capital_transaction_period < period).all()
        for capital_tran in capital_tran_list:
            capital_tran.capital_transaction_operation_type = operate_type
            capital_tran.capital_transaction_status = status
            capital_tran.capital_transaction_actual_operate_at = capital_tran.capital_transaction_expect_finished_at
            capital_tran.capital_transaction_expect_operate_at = capital_tran.capital_transaction_expect_finished_at
            capital_tran.capital_transaction_user_repay_at = capital_tran.capital_transaction_expect_finished_at
            capital_tran.capital_transaction_withhold_result_channel = 'qsq'
            capital_tran.capital_transaction_repaid_amount = capital_tran.capital_transaction_amount
            capital_tran.capital_transaction_process_status = 'success'
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

    def modify_row_data(self, modify_id, modify_type, modify_data):
        obj = eval(modify_type.title().replace("_", ""))
        if modify_type == 'capital_settlement_detail':
            except_id = 'id'
        elif modify_type == 'central_task':
            except_id = 'task_id'
        else:
            except_id = '{0}_id'.format(modify_type)
        record = self.db_session.query(obj).filter(getattr(obj, except_id) == modify_id).first()
        for item_key, item_value in modify_data.items():
            if item_key == 'id':
                continue
            attr_name = item_key if modify_type in ('central_task', 'capital_settlement_detail') \
                else '_'.join((modify_type, item_key))
            setattr(record, attr_name, item_value)
        self.db_session.add(record)
        self.db_session.flush()
        self.db_session.commit()

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

    @time_print
    def run_xxl_job(self, job_type, run_date, param={}):
        get_param = self.xxljob.get_job_info(job_type)[0]['executorParam']
        param = json.dumps(json.loads(param)) if param else get_param
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

    def get_date_is_holiday(self, date_time):
        get_date = self.db_session.query(Holiday).filter(Holiday.holiday_date == date_time).first()
        if get_date:
            return get_date.holiday_status
        return None

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
        task_dict = self.get_task(task_order_no, item_no, max_create_at, channel)
        msg_dict = self.get_msg(item_no,  max_create_at)
        ret.update(task_dict)
        ret.update(msg_dict)
        return ret

    @biz_modify_return
    def get_task(self, task_order_no, item_no, channel=None, max_create_at=None):
        max_create_at = max_create_at if max_create_at is not None else self.get_date(is_str=True, days=-7)
        task_order_no = tuple(list(task_order_no) + [channel]) \
            if channel is not None else task_order_no
        task_list = self.db_session.query(CentralTask).filter(
            or_(CentralTask.task_order_no.in_(task_order_no),
                CentralTask.task_order_no.like('settle_detail_{0}%'.format(channel)),
                CentralTask.task_order_no.like('{0}%'.format(channel)),
                CentralTask.task_order_no.like('{0}%'.format(item_no))),
            CentralTask.task_update_at >= max_create_at)\
            .order_by(desc(CentralTask.task_id)).all()

        return task_list

    @biz_modify_return
    def get_msg(self, item_no, max_create_at=None):
        max_create_at = max_create_at if max_create_at is not None else self.get_date(is_str=True, days=-7)
        msg_list = self.db_session.query(CentralSendMsg). \
            filter(CentralSendMsg.sendmsg_order_no.like('{0}%'.format(item_no)),
                   CentralSendMsg.sendmsg_update_at >= max_create_at) \
            .order_by(desc(CentralSendMsg.sendmsg_id)).all()
        return msg_list

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
        due_at = self.get_date(days=-1)
        return self.add_capital_settlement_detail(item_no, period, due_at, principal, interest, 'compensate')

    def add_buyback(self, item_no, period):
        asset_tran = self.db_session.query(AssetTran).filter(AssetTran.asset_tran_asset_item_no == item_no,
                                                             AssetTran.asset_tran_period >= period).all()
        principal = sum([x.asset_tran_amount for x in (filter(
            lambda x: x.asset_tran_type == 'repayprincipal', asset_tran))])
        interest = list(filter(lambda x: x.asset_tran_type == 'repayinterest', asset_tran))[0].asset_tran_amount
        due_at = self.get_date(days=-1)
        return self.add_capital_settlement_detail(item_no, period, due_at, principal, interest, 'buyback')

    def remove_buyback(self, item_no, channel):
        self.db_session.query(CapitalSettlementDetail).filter(
            CapitalSettlementDetail.asset_item_no == item_no,
            CapitalSettlementDetail.channel == channel).delete()
        self.db_session.flush()
        self.db_session.commit()

    def add_capital_settlement_detail(self, item_no, period, due_at, principal, interest, settlement_type):
        asset = self.db_session.query(Asset).filter(Asset.asset_item_no == item_no).first()
        if not asset:
            raise ValueError('not fount the asset with item_no is :{0}'.format(asset))
        compensate = self.db_session.query(CapitalSettlementDetail).filter(
            CapitalSettlementDetail.asset_item_no == item_no).first()
        # if self.cal_days(due_at, self.get_date()) < 0:
        #     raise ValueError('not overdue with asset is :{0}, period is :{1}'.format(item_no, period))
        if not compensate:
            compensate = CapitalSettlementDetail()
            compensate.asset_item_no = item_no
        compensate.period = period

        compensate.channel = asset.asset_loan_channel
        compensate.asset_granted_principal_amount = asset.asset_granted_principal_amount_f
        compensate.repay_total_amount = principal + interest
        compensate.repay_principal = principal
        compensate.repay_interest = interest
        compensate.contract_start_date = asset.asset_actual_grant_at
        compensate.contract_end_date = asset.asset_due_at
        compensate.type = settlement_type
        compensate.capital_tran_process_status = 'open'
        compensate.repay_date = due_at

        self.db_session.add(compensate)
        self.db_session.commit()

    @biz_modify_return
    def get_capital(self, item_no):
        capital_asset = self.db_session.query(CapitalAsset).filter(
            CapitalAsset.capital_asset_item_no == item_no).first()
        return capital_asset

    @biz_modify_return
    def get_capital_tran(self, item_no):
        capital_tran_list = self.db_session.query(CapitalTransaction).filter(
            CapitalTransaction.capital_transaction_asset_item_no == item_no).all()
        return capital_tran_list

    def get_capital_tran_info(self, item_no, period_start, operation_type, status, fee_type):
        capital_tran = self.db_session.query(CapitalTransaction).filter(
            CapitalTransaction.capital_transaction_asset_item_no == item_no,
            CapitalTransaction.capital_transaction_operation_type == operation_type,
            CapitalTransaction.capital_transaction_status == status,
            CapitalTransaction.capital_transaction_period >= period_start,
            CapitalTransaction.capital_transaction_type.in_(fee_type)).all()
        return capital_tran

    @biz_modify_return
    def get_capital_notify(self, item_no):
        capital_notify_list = self.db_session.query(CapitalNotify).filter(
            CapitalNotify.capital_notify_asset_item_no == item_no)\
            .order_by(desc(CapitalNotify.capital_notify_id)).all()
        return capital_notify_list

    @biz_modify_return
    def get_capital_settlement_detail(self, channel):
        capital_detail_list = self.db_session.query(CapitalSettlementDetail).filter(
            CapitalSettlementDetail.channel == channel) \
            .order_by(desc(CapitalSettlementDetail.id)).all()
        return capital_detail_list

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

    @time_print
    def change_asset(self, item_no, item_no_x, item_no_rights, advance_day, advance_month):
        capital_asset = self.db_session.query(CapitalAsset).filter(
            CapitalAsset.capital_asset_item_no == item_no).first()
        capital_tran_list = self.db_session.query(CapitalTransaction).filter(
            CapitalTransaction.capital_transaction_asset_item_no == item_no).all()
        self.change_asset_due_at([], [], capital_asset, capital_tran_list, advance_day,
                                 advance_month, 30)

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
                LogUtil.log_info('task is run with success')
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

    @time_print
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

    @time_print
    def run_central_task_by_order_no(self, order_no, task_type, status='open', timeout=60):
        begin = datetime.now()
        while True:
            task = self.get_central_task_info(order_no, task_type, status=status)
            if task:
                break
            if (datetime.now() - begin).seconds >= timeout:
                raise CaseException('not found the task with order no is {0}, type is {1} in 60s'.format(order_no,
                                                                                                         task_type))
        return self.run_central_task_by_task_id(task.task_id)

    @wait_timeout
    def get_central_task_info(self, order_no, task_type, status='open'):
        task = self.db_session.query(CentralTask).filter(CentralTask.task_order_no == order_no,
                                                         CentralTask.task_type == task_type,
                                                         CentralTask.task_status == status).first()
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

    @time_print
    def run_central_msg_by_msg_id(self, msg_id):
        self.update_central_msg_next_run_at_forward_by_msg_id(msg_id)
        ret = Http.http_get(self.central_msg_url.format(msg_id))
        return ret

    @wait_timeout
    def run_central_msg_by_order_no(self, order_no, sendmsg_type, max_create_at=None):
        max_create_at = self.get_date(fmt='Y-%m-%d %H:00:00', is_str=True) if max_create_at is None else max_create_at
        msg = self.db_session.query(CentralSendMsg).filter(CentralSendMsg.sendmsg_order_no == order_no,
                                                           CentralSendMsg.sendmsg_status == 'open',
                                                           CentralSendMsg.sendmsg_update_at >= max_create_at,
                                                           CentralSendMsg.sendmsg_type == sendmsg_type).all()
        for item in msg:
            self.run_central_msg_by_msg_id(item.sendmsg_id)
        return msg

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
                    LogUtil.log_info(msg_key, item_info.asset_loan_channel,
                                     self.compare_data(123, json.loads(old_data[msg.sendmsg_order_no]),
                                                       json.loads(msg.sendmsg_content), [], 0))
                else:
                    LogUtil.log_info('not fount the item {0}'.format(item_no))
            else:
                LogUtil.log_info('not fount the order no {0}'.format(msg['sendmsg_order_no']))