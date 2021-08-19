from flask import Blueprint, request, jsonify
from flask import current_app

from app.common.db_util import DataBase
from app.program_business.china.biz_central.services import ChinaBizCentralAuto

api_data_base = Blueprint('api_data_base', __name__)


@api_data_base.route('/')
def hello_world():
    current_app.logger.info('hello data base api!')
    return 'hello data base api'


@api_data_base.route('/get_info', methods=['POST'])
def get_info():
    get_ret = {
        "code": 0,
        "msg": "获取成功"
    }
    req = request.json
    country = req.get('country', 'china')
    env = req.get("env", 1)
    run_dev = req.get("run_dev", 'dev')
    table = req.get('table', None)
    query_key = req.get('query_key', None)
    program = req.get('program', 'repay')
    db = DataBase(country, program, env, run_dev)
    get_ret['data'] = db.get_data(table, query_key)
    db.close_connects()
    return jsonify(get_ret)


@api_data_base.route('/test', methods=['POST'])
def tool_test():
    get_ret = {
        "code": 0,
        "msg": "执行成功"
    }
    biz_central = ChinaBizCentralAuto('2', 'dev')
    biz_central.create_push_dcs_task()
    return jsonify(get_ret)
