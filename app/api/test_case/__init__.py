
from copy import deepcopy
from app.common import RET
from flask import Blueprint, current_app, jsonify, request
from app.model.Model import CaseTask, TaskRelativeCase, TestCase
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


@api_test_case.route('/get_cases', methods=["POST"])
def get_case():
    ret = deepcopy(RET)
    req = request.json
    country = req.get('country', 'china')
    program = req.get('program')
    case_list = TestCase.query.filter(TestCase.test_cases_country == country,
                                      TestCase.test_cases_group == program).order_by(TestCase.test_cases_id).all()
    ret['data'] = {'case': list(map(lambda x: x.to_spec_dict, case_list))}
    return jsonify(ret)


@api_test_case.route('/filter_cases', methods=["POST"])
def filter_cases():
    ret = deepcopy(RET)
    req = request.json
    priority = req.get('priority')
    program = req.get('program')
    scene = req.get('scene')
    pageParams = req.get('pageParams')
    channel = req.get('channel')
    query_cases = TestCase.query.filter(TestCase.test_cases_group == program,
                                        TestCase.test_cases_scene.in_(tuple(scene)),
                                        TestCase.test_cases_channel == channel,
                                        TestCase.test_cases_priority.in_(tuple(priority))).paginate(
            page=pageParams['page'],
            per_page=pageParams['limit'],
            error_out=True)
    ret["total"] = query_cases.total
    ret["data"] = TestCase.to_spec_dicts(query_cases.items) if query_cases.items else []
    return jsonify(ret)


@api_test_case.route('/case_task_create', methods=["POST"])
def case_task_create():
    ret = deepcopy(RET)
    req = request.json
    case_list = req.get('case_id')
    if not isinstance(case_list, list):
        ret["code"] = 1
        ret["message"] = "case_list类型不正确，需要list，实际是：{0}".format(type(case_list))
        return ret

    country = req.get('country', 'china')
    program = req.get('program')
    user = req.pop('user')
    task_type = req.pop('task_type')
    case_name = req.pop('case_name', None)
    execute_time = req.pop('execute_time', None)
    now = datetime.datetime.now()
    env = req.pop('env', None)
    environment = req.pop('environment', 'dev')
    case_task = CaseTask()
    case_task.case_task_country = country
    case_task.case_task_program = program
    case_task.case_task_execute_time = now if task_type == 0 else execute_time
    case_task.case_task_name = case_name if case_name is not None else 'Case{0}'.format(now)
    case_task.case_task_creator = user
    case_task.case_task_type = task_type
    case_task.case_task_run_env = env
    case_task.case_task_updater = user
    db.session.add(case_task)
    db.session.flush()
    for case in case_list:
        case_rel = TaskRelativeCase()
        case_rel.task_relative_case_case_id = case
        case_rel.task_relative_case_task_id = case_task.case_task_id
        db.session.add(case_rel)
    db.session.flush()

    return jsonify(ret)
