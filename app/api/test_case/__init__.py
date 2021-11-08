from copy import deepcopy
from app.common import RET
from flask import Blueprint, current_app, jsonify, request

api_test_case = Blueprint('api_test_case', __name__)


@api_test_case.route('/')
def hello_world():
    current_app.logger.info('hello test case api!')
    return 'hello test case api!'


@api_test_case.route('/cases', methods=["POST"])
def get_cases():
    ret = deepcopy(RET)
    req = request.json
    return jsonify(ret)


@api_test_case.route('/cases', methods=["POST"])
def run_cases():
    ret = deepcopy(RET)
    req = request.json
    case_id = req.get('case_id')
    case_group = req.get('case_group')
    case_scene = req.get('case_scene')
    program = req.get('program')
    env = req.pop('env', None)
    environment = req.pop('environment', 'dev')
    obj = eval('{0}{1}AutoTest'.format(case_group.title(), program.title()))(env, environment)
    obj.run_cases(case_id, case_group, case_scene)
    return jsonify(ret)
