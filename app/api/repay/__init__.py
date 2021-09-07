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
    # try:
    repay = RepayFactory.get_repay(country, env, environment)
    ret['data'] = getattr(repay, tool)(**req)
    # except Exception as e:
    #     ret['code'] = 1
    #     ret['message'] = str(e)
    return jsonify(ret)
