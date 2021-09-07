import traceback
from copy import deepcopy

from flask import Blueprint, request, jsonify
from flask import current_app

from app.common import NacosFactory, RET

api_nacos = Blueprint('api_nacos', __name__)


@api_nacos.route('/')
def hello_world():
    current_app.logger.info('hello nacos api!')
    return 'hello nacos api'


@api_nacos.route('/update_config', methods=['POST'])
def update_nacos_config():
    update_ret = deepcopy(RET)
    req = request.json
    country = req.get('country', 'china')
    env = req.get("env", 1)
    program = req.get('program', 'repay')
    config_key = req.get('config_key')
    nacos = NacosFactory.get_nacos(country, program, env)
    nacos.update_nacos_config(config_key)
    return jsonify(update_ret)


@api_nacos.route('/get_config', methods=['POST'])
def get_nacos_config():
    get_ret = deepcopy(RET)
    req = request.json
    country = req.get('country', 'china')
    env = req.get("env", 1)
    program = req.get('program', 'repay')
    config_name = req.get('config_name')
    group = req.get('group', 'KV')
    nacos = NacosFactory.get_nacos(country, program, env)
    get_ret['data'] = nacos.get_config_content(config_name, group)
    return jsonify(get_ret)
