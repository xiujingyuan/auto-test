import traceback
from copy import deepcopy

from flask import Blueprint, request, jsonify
from flask import current_app

from app.common import RET
from app.program_business.china.repay.services import ChinaRepayAuto

api_repay = Blueprint('api_repay', __name__)


class RepayFactory(object):
    @classmethod
    def get_repay(cls, country, env, environment):
        if country == 'china':
            return ChinaRepayAuto(env, environment)


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
                from_repay = RepayFactory.get_repay(country, env, environment)
                from_req = {'item_no': req.get('item_no')}
                req_param = getattr(from_repay, 'get_exist_asset_request')(**from_req)
                if not req_param['biz_task']:
                    raise ValueError('not found the asset_import or capital_import or withdraw_success msg!')
                req['asset_import'] = req_param['biz_task'][0]
                req['capital_import'] = req_param['biz_task'][1]
                req['withdraw_success'] = req_param['biz_task'][2]
                req['grant_msg'] = req_param['grant_msg']
                for e in to_env:
                    repay = RepayFactory.get_repay(country, e, environment)
                    ret['data'].append({e: getattr(repay, tool)(**req)})
        else:
            repay = RepayFactory.get_repay(country, env, environment)
            ret['data'] = getattr(repay, tool)(**req)
    except Exception as e:
        ret['code'] = 1
        print(traceback.format_exc())
        ret['message'] = str(e)
    return jsonify(ret)
