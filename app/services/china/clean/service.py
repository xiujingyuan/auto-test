import importlib
import time
from datetime import datetime
from sqlalchemy import desc, or_

from app.common.easy_mock_util import EasyMock
from app.common.log_util import LogUtil
from app.services import BaseService, wait_timeout, time_print
from app.common.http_util import Http
import json

from app.services.china import get_trace
from app.services.china.biz_central import biz_modify_return
from app.services.china.biz_central.Model import CentralTask, CentralSendMsg, Asset, AssetTran, \
    CapitalAsset, CapitalTransaction, WithholdHistory, WithholdResult, CapitalNotify, CapitalSettlementDetail, Holiday
from app.services.china.clean.Model import CleanTask, CleanClearingTrans , CleanCapitalSettlementPending
from app.test_cases import CaseException


class ChinaCleanService(BaseService):

    def __init__(self, env, run_env, mock_name, check_req=False, return_req=False):
        self.clean_host = "https://biz-gateway-proxy.k8s-ingress-nginx.kuainiujinke.com/dcs1"
        super(ChinaCleanService, self).__init__('china', 'clean', env, run_env, mock_name, check_req, return_req)
        self.task_url = self.clean_host + "/job/runTaskByOrderNo?orderNo={0}"
        self.asset = None

    def get_clean_info(self, item_no):
        ret = {}
        ret.update(self.get_clean_task(item_no))
        ret.update(self.get_clean_clearing_trans(item_no))
        ret.update(self.get_clean_capital_settlement_pending(item_no))

        # ret.update(self.get_table_info('clean_task', 'task_order_no', item_no))
        # ret.update(self.get_table_info('clean_clearing_trans', 'item_no', item_no))
        # ret.update(self.get_table_info('clean_capital_settlement_pending', 'asset_item_no', item_no))
        return ret

    def get_table_info(self, table_name, table_key, item_no):
        meta_class = importlib.import_module('app.services.china.clean.Model')
        table_modal = getattr(meta_class, table_name.title())
        table_info = self.db_session.query(table_modal).filter(getattr(table_modal, table_key) == item_no).all()
        return {table_name: list(map(lambda x: x.to_dict, table_info))}

    def get_clean_task(self, item_no):
        clean_task = self.db_session.query(CleanTask).filter(CleanTask.task_order_no == item_no).all()
        return {'clean_task': list(map(lambda x: x.to_dict, clean_task))}

    def get_clean_clearing_trans(self, item_no):
        clean_clearing_tran = self.db_session.query(CleanClearingTrans).filter(
            CleanClearingTrans.item_no == item_no).all()
        return {'clean_clearing_trans': list(map(lambda x: x.to_dict, clean_clearing_tran))}

    def get_clean_capital_settlement_pending(self, item_no):
        clean_clearing_settlement_pending = self.db_session.query(CleanCapitalSettlementPending).filter(
            CleanCapitalSettlementPending.asset_item_no == item_no).all()
        return {'clean_capital_settlement_pending': list(map(lambda x: x.to_dict, clean_clearing_settlement_pending))}

    @get_trace
    def operate_action(self, item_no, extend, op_type, table_name, loading_key, creator):
        loading_key_first = loading_key.split("_")[0]
        extend_name = '{0}_create_at'.format(loading_key_first)
        max_create_at = extend[extend_name] if extend_name in extend else None
        real_req = {}
        if op_type == 'run_clean_task_by_task_order_no':
            real_req['order_no'] = item_no
        if op_type == "del_row_data":
            real_req['del_id'] = extend['id']
            real_req['item_no'] = item_no
            real_req['refresh_type'] = table_name
            real_req['max_create_at'] = max_create_at
        ret = getattr(self, op_type)(**real_req)
        if max_create_at is not None:
            return self.info_refresh(item_no, max_create_at, refresh_type=table_name)
        return ret

    @time_print
    def info_refresh(self, item_no, max_create_at=None, refresh_type=None):
        req_name = 'get_{0}'.format(refresh_type)
        ret = getattr(self, req_name)(item_no)
        return ret

    def modify_row_data(self, item_no, modify_id, modify_type, modify_data, max_create_at=None):
        obj = eval(modify_type.title().replace("_", ""))
        except_id = 'task_id' if modify_type == 'clean_task' else 'id'
        record = self.db_session.query(obj).filter(getattr(obj, except_id) == modify_id).first()
        for item_key, item_value in modify_data.items():
            if item_key == except_id:
                continue
            setattr(record, item_key, item_value)
        self.db_session.add(record)
        self.db_session.flush()
        self.db_session.commit()
        return self.info_refresh(item_no, max_create_at=max_create_at, refresh_type=modify_type)

    def delete_row_data(self, del_id, del_type):
        obj = eval(del_type.title().replace("_", ""))
        except_id = 'task_id' if del_type == 'clean_task' else 'id'
        self.db_session.query(obj).filter(getattr(obj, except_id) == del_id).delete()
        self.db_session.flush()
        self.db_session.commit()

    @time_print
    def run_xxl_job(self, job_type, run_date, param={}):
        get_param = self.xxljob.get_job_info(job_type)[0]['executorParam']
        param = json.dumps(json.loads(param)) if param else get_param
        url = self.run_job_by_date_url.format(job_type, param, run_date)
        return Http.http_get(url)

    def update_clean_task_next_run_at_forward_by_order_no(self, order_no):
        clean_task = self.db_session.query(CleanTask).filter(CleanTask.task_order_no == order_no).all()
        if not clean_task:
            raise ValueError("not found the clean_task info with clean_task'id: {0}".format(order_no))
        for task in clean_task:
            task.task_next_run_at = self.get_date(minutes=1)
            self.db_session.add(task)
        self.db_session.commit()

    @time_print
    def run_clean_task_by_task_order_no(self, order_no, status='open', timeout=1):
        self.update_clean_task_next_run_at_forward_by_order_no(order_no)
        url = self.task_url.format(order_no)
        ret = Http.http_get(url)
        return ret
