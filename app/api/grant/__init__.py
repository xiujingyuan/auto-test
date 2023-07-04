import traceback
from copy import deepcopy

from flask import Blueprint, request, jsonify
from flask import current_app
from app.common import RET, GrantServiceFactory
from app.common.log_util import LogUtil

api_grant = Blueprint('api_grant', __name__)


@api_grant.route('/')
def hello_world():
    current_app.logger.info('hello grant api!')
    return 'hello grant api'


@api_grant.route('/grant_tools/<string:tool>', methods=["POST"])
def grant_tools(tool):
    ret = deepcopy(RET)
    req = request.json
    country = req.pop('country', 'china')
    env = req.pop('env', None)
    environment = req.pop('environment', 'dev')
    mock_name = req.pop('mock_name', 'gbiz_auto_test')
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
    try:
        grant = GrantServiceFactory.get_grant(country, env, environment, mock_name)
        if not hasattr(grant, tool):
            ret['message'] = '没有该工具{0}'.format(tool)
            ret['code'] = 1
            ret['data'] = []
        else:
            ret['data'] = getattr(grant, tool)(**req)
    except Exception as e:
        ret['code'] = 1
        LogUtil.log_info(traceback.format_exc())
        ret['message'] = str(e)
    return jsonify(ret)
