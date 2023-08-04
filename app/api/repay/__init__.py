import json
import traceback
from copy import deepcopy

from flask import Blueprint, request, jsonify
from flask import current_app
from app.common import RET, RepayServiceFactory
from app.common.log_util import LogUtil

api_repay = Blueprint('api_repay', __name__)


@api_repay.route('/')
def hello_world():
    current_app.logger.info('hello repay api!')
    return 'hello repay api'


@api_repay.route('/repay_tools/<string:tool>', methods=["POST"])
def repay_tools(tool):
    ret = deepcopy(RET)
    req = request.json
    country = req.pop('country', 'china')
    env = req.pop('env', None)
    environment = req.pop('environment', 'dev')
    mock_name = req.pop('mock_name', None)
    period = req.pop("period", None)

    op_type = req.get('op_type', None)
    if op_type != 'get_trace_info':
        loading_key = req.pop('loading_key', None)

    if period is not None:
        req['period'] = period
        if country != 'china':
            if isinstance(period, str) and "-" in period:
                req['period'] = period.split('-')[0]
                req['days'] = int(period.split('-')[1])
            else:
                req['days'] = 0
    if tool == 'copy_asset':
        to_env = req.pop('to_env', None)
        if to_env is None:
            ret['code'] = 1
            ret['message'] = 'need from environment'
        else:
            from_repay = RepayServiceFactory.get_repay(country, env, environment, mock_name)
            from_req = {'item_no': req.get('item_no')}
            req_param = getattr(from_repay, 'get_exist_asset_request')(**from_req)
            if not req_param['biz_task']:
                grant_msg = getattr(from_repay, 'get_only_grant_msg')(**from_req)
                if len(grant_msg) == 3:
                    tool = 'copy_by_grant_msg'
                    req = {'grant_msg': grant_msg}
                    for e in to_env:
                        repay = RepayServiceFactory.get_repay(country, e, environment, mock_name)
                        ret['data'].append({e: getattr(repay, tool)(**req)})
                raise ValueError('not found the asset_import or capital_import or withdraw_success msg!')
            else:
                req['asset_import'] = req_param['biz_task'][0]
                req['grant_msg'] = req_param['grant_msg']
                req['capital_import'] = req_param['biz_task'][1] if req_param['is_noloan'] else []
                req['capital_data'] = req_param['capital_data']
                req['withdraw_success'] = req_param['biz_task'][-1]
                req['grant_sync_task'] = req_param['grant_sync_task']
                for e in to_env:
                    repay = RepayServiceFactory.get_repay(country, e, environment, mock_name)
                    ret['data'].append({e: getattr(repay, tool)(**req)})
    elif tool == 'sync_kv_value':
        data = req.pop('data')
        value = req.pop('value')
        name = req.pop('name')
        channel = req.pop('channel')
        if value == 'gateway':
            ret['message'] = 'gateway配置不需要迁移'
            ret['code'] = 1
            ret['data'] = []
            return jsonify(ret)
        kv_value = req.pop('kv_value')
        kv_value = json.dumps(kv_value, ensure_ascii=False) if isinstance(kv_value, dict) else kv_value
        req['content'] = kv_value
        for item in ['1', '2', '3', '4', '9']:
            if item != env:
                repay = RepayServiceFactory.get_repay(country, item, environment, mock_name)
                if data == value:
                    name = name.format(channel)
                if value.endswith('system'):
                    name = name + '.properties'
                req['config_name'] = name
                repay.nacos.update_config(**req)
    else:
        repay = RepayServiceFactory.get_repay(country, env, environment, mock_name)
        if tool == "run_xxl_job":
            item_no = req.pop('item_no')
        if not hasattr(repay, tool):
            ret['message'] = '没有该工具{0}'.format(tool)
            ret['code'] = 1
            ret['data'] = []
        else:
            ret['data'] = getattr(repay, tool)(**req)

    return jsonify(ret)
