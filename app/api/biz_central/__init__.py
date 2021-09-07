from copy import deepcopy

from flask import Blueprint, request, jsonify
from flask import current_app

from app.common import RET
from app.program_business.china.biz_central.services import ChinaBizCentralAuto

api_biz_central = Blueprint('api_biz_central', __name__)


class BizCentralFactory(object):
    @classmethod
    def get_biz_central(cls, country, env, environment):
        if country == 'china':
            return ChinaBizCentralAuto(env, environment)


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
    repay = BizCentralFactory.get_biz_central(country, env, environment)
    ret['data'] = getattr(repay, tool)(**req)
    return jsonify(ret)
