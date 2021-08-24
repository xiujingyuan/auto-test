from flask import Blueprint, request, jsonify
from flask import current_app
from app.common import XxlJobFactory

api_xxljob = Blueprint('api_xxljob', __name__)


@api_xxljob.route('/')
def hello_world():
    current_app.logger.info('hello xxl job api!')
    return 'hello xxl job api'


@api_xxljob.route('/exec_xxljob', methods=['POST'])
def exec_xxljob():
    get_ret = {
        "code": 0,
        "msg": "执行xxljob成功"
    }
    req = request.json
    country = req.get('country', 'china')
    env = req.get("env", 1)
    program = req.get('program', 'repay')
    haddler_name = req.get('haddler_name')
    xxljob = XxlJobFactory.get_xxljob(country, program, env)
    get_ret['data'] = xxljob.trigger_job(haddler_name)
    return jsonify(get_ret)
