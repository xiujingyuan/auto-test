import traceback

from flask import Blueprint, request
from flask import current_app
from app.program_business.china.repay import ChinaRepayNacos

api_nacos = Blueprint('api_nacos', __name__)


class NacosFactory(object):

    @classmethod
    def get_nacos(cls, country, program, env):
        if country == 'china' and program == 'repay':
            return ChinaRepayNacos(env)


@api_nacos.route('/')
def hello_world():
    current_app.logger.info('hello nacos api!')
    return 'hello nacos api'


@api_nacos.route('/update_config', methods=['POST'])
def update_nacos_config():
    ret = {
        "code": 0,
        "msg": "更新成功"
    }
    req = request.json
    country = req.get('country', 'china')
    env = req.get("env", 1)
    program = req.get('program', 'repay')
    config_key = req.get('config_key')
    nacos = NacosFactory.get_nacos(country, program, env)
    nacos.update_nacos_config(config_key)
    return ret
