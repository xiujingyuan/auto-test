
from copy import deepcopy
from app.common import RET
from flask import Blueprint, current_app, jsonify, request
from app.model.Model import CaseTask, TaskRelativeCase
import datetime
from app import db

api_test_case = Blueprint('api_test_case', __name__)


@api_test_case.route('/')
def hello_world():
    current_app.logger.info('hello test case api!')
    return 'hello test case api!'


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
    obj = eval('{0}{1}AutoTest'.format(case_group.title(), program.replace('_', '').title()))(env, environment)
    obj.run_cases(case_id, case_group, case_scene)
    return jsonify(ret)


@api_test_case.route('/case_task/create', methods=["POST"])
def case_task_create():
    ret = deepcopy(RET)
    req = request.json
    case_list = req.get('case_id')
    if isinstance(case_list, list):
        ret["code"] = 1
        ret["message"] = "case_list类型不正确，需要list，实际是：{0}".format(type(case_list))
        return ret

    country = req.get('country')
    program = req.get('program')
    user = req.pop('user')
    task_type = req.pop('task_type')
    case_name = req.pop('case_name', None)
    now = datetime.datetime.now()
    env = req.pop('env', None)
    environment = req.pop('environment', 'dev')
    case_task = CaseTask()
    case_task.case_task_country = country
    case_task.case_task_program = program
    case_task.case_task_execute_time = now
    case_task.case_task_name = case_name if case_name is not None else 'Case{0}'.format(now)
    case_task.case_task_creator = user
    case_task.case_task_type = task_type
    case_task.case_task_updater = user
    db.session.add(case_task)
    for case in case_list:
        case_rel = TaskRelativeCase()
        case_rel.task_relative_case_case_id = case
        case_rel.task_relative_case_task_id = case_task.case_task_id
        db.session.add(case_rel)
    db.session.flush()

    return jsonify(ret)
