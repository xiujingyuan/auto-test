from flask import Blueprint, request, jsonify
from flask import current_app
from app.program_business.china.repay import ChinaRepayXxlJob
from app.program_business.china.biz_central import ChinaBizCentralXxlJob

api_xxljob = Blueprint('api_xxljob', __name__)


class XxlJobFactory(object):

    @classmethod
    def get_xxljob(cls, country, program, env):
        if country == 'china' and program == 'repay':
            return ChinaRepayXxlJob(env)
        if country == 'china' and program == 'biz-central':
            return ChinaBizCentralXxlJob(env)


@api_xxljob.route('/')
def hello_world():
    current_app.logger.info('hello xxl job api!')
    return 'hello xxl job api'


@api_xxljob.route('/exec_xxljob', methods=['POST'])
def exec_xxljob():
    get_ret = {
        "code": 0,
        "msg": "更新成功"
    }
    req = request.json
    country = req.get('country', 'china')
    env = req.get("env", 1)
    program = req.get('program', 'repay')
    haddler_name = req.get('haddler_name')
    xxljob = XxlJobFactory.get_xxljob(country, program, env)
    get_ret['data'] = xxljob.trigger_job(haddler_name)
    return jsonify(get_ret)
