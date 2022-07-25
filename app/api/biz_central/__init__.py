from copy import deepcopy
from flask import Blueprint, request, jsonify
from flask import current_app
from app.common import RET, BizCentralServiceFactory

api_biz_central = Blueprint('api_biz_central', __name__)


@api_biz_central.route('/')
def hello_world():
    current_app.logger.info('hello biz central api!')
    return 'hello biz central api'


@api_biz_central.route('/biz_central_tools/<string:tool>', methods=["POST"])
def biz_central_tools(tool):
    ret = deepcopy(RET)
    req = request.json
    country = req.pop('country', 'china')
    env = req.pop('env', None)
    environment = req.pop('environment', 'dev')
    central = BizCentralServiceFactory.get_biz_central(country, env, environment)
    ret['data'] = getattr(central, tool)(**req)
    return jsonify(ret)
