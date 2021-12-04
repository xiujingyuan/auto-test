import traceback
from copy import deepcopy

from flask import Blueprint, request, jsonify
from flask import current_app
from app.common import RET, RepayServiceFactory

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

    try:
        if tool == 'copy_asset':
            to_env = req.pop('to_env', None)
            if to_env is None:
                ret['code'] = 1
                ret['message'] = 'need from environment'
            else:
                from_repay = RepayServiceFactory.get_repay(country, env, environment)
                from_req = {'item_no': req.get('item_no')}
                req_param = getattr(from_repay, 'get_exist_asset_request')(**from_req)
                if not req_param['biz_task']:
                    raise ValueError('not found the asset_import or capital_import or withdraw_success msg!')
                req['asset_import'] = req_param['biz_task'][0]
                req['capital_import'] = req_param['biz_task'][1] if req_param['is_noloan'] else []
                req['capital_data'] = req_param['capital_data']
                req['withdraw_success'] = req_param['biz_task'][-1]
                req['grant_msg'] = req_param['grant_msg']
                for e in to_env:
                    repay = RepayServiceFactory.get_repay(country, e, environment)
                    ret['data'].append({e: getattr(repay, tool)(**req)})
        else:
            repay = RepayServiceFactory.get_repay(country, env, environment)
            ret['data'] = getattr(repay, tool)(**req)
    except Exception as e:
        ret['code'] = 1
        print(traceback.format_exc())
        ret['message'] = str(e)
    return jsonify(ret)
