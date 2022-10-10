import traceback
from copy import deepcopy

from flask import Blueprint, request, jsonify
from app.common import RET, CleanServiceFactory
from app.common.log_util import LogUtil
api_clean = Blueprint('api_clean', __name__)


@api_clean.route('/clean_tools/<string:tool>', methods=["POST"])
def clean_tools(tool):
    ret = deepcopy(RET)
    req = request.json
    country = req.pop('country', 'china')
    req.pop('env')
    env = '7'
    environment = req.pop('environment', 'dev')
    period = req.pop("period", None)
    mock_name = req.pop("mock_name")
    req.pop('run_date', None)
    if period is not None:
        req['period'] = period
        if country != 'china':
            req['days'] = 0
            if isinstance(period, str) and "-" in period:
                req['period'] = period.split('-')[0]
                req['days'] = int(period.split('-')[1])
    try:
        repay = CleanServiceFactory.get_clean(country, env, environment, mock_name)
        if tool == "run_xxl_job":
            req.pop('item_no')
        if not hasattr(repay, tool):
            ret['message'] = '没有该工具{0}'.format(tool)
            ret['code'] = 1
            ret['data'] = []
        else:
            ret['data'] = getattr(repay, tool)(**req)
    except Exception as e:
        ret['code'] = 1
        LogUtil.log_info(traceback.format_exc())
        ret['message'] = str(e)
    return jsonify(ret)
