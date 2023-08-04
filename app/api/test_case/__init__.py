import importlib
import json
from copy import deepcopy

from sqlalchemy import desc

from app.common import RET
from flask import Blueprint, current_app, jsonify, request
from app.model.Model import CaseTask, TaskRelativeCase, TestCase, BackendKeyValue
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

@api_test_case.route('/update_single_case', methods=["POST"])
def update_case():
    ret = deepcopy(RET)
    req = request.json
    case = req.get("case", None)
    if case is None:
        ret['message'] = 'need case, but not found'
        ret['code'] = 1
    find_case = TestCase.query.filter(TestCase.test_cases_id == case['id']).first()
    if find_case is None:
        ret['message'] = "not fount the case with case's {0}".format(case['id'])
        ret['code'] = 1
    for case_key, case_value in case.items():
        if case_key == 'id':
            continue
        setattr(find_case, 'test_cases_{0}'.format(case_key), case_value)
    db.session.add(find_case)
    db.session.flush()
    return jsonify(ret)


@api_test_case.route('/run_single_case', methods=["POST"])
def run_case():
    ret = deepcopy(RET)
    req = request.json
    case_id = req.get("case_id", None)
    environment = req.get("environment", 'dev')
    env = req.get("env", "1")
    if env is None:
        ret['message'] = 'need env, but not found'
        ret['code'] = 1
    if case_id is None:
        ret['message'] = 'need case, but not found'
        ret['code'] = 1
    find_case = TestCase.query.filter(TestCase.test_cases_id == case_id).first()
    if find_case is None:
        ret['message'] = "not fount the case with case's {0}".format(case_id)
        ret['code'] = 1
    channel = find_case.test_cases_channel
    mock_name = find_case.test_cases_mock_name
    program = find_case.test_cases_group.lower()
    obj_name = '{0}{1}AutoTest'.format(channel.replace('_', '').title(), program.title())
    meta_class = importlib.import_module('app.test_cases.china.{0}.{1}'.format(program, obj_name))
    obj = getattr(meta_class, obj_name)(env, environment, mock_name)
    obj.run_single_case(find_case)
    return jsonify(ret)


@api_test_case.route('/run_case_task', methods=["POST"])
def run_case_task():
    ret = deepcopy(RET)
    req = request.json
    case_task_id = req.get("case_task_id", None)
    environment = req.get("environment", 'dev')
    env = req.get("env", "1")
    if env is None:
        ret['message'] = 'need env, but not found'
        ret['code'] = 1
    if case_task_id is None:
        ret['message'] = 'need case, but not found'
        ret['code'] = 1
    case_list = TaskRelativeCase.query.filter(TaskRelativeCase.task_relative_case_task_id == case_task_id).all()
    for case in case_list:
        find_case = TestCase.query.filter(TestCase.test_cases_id == case.task_relative_case_case_id).first()
        if find_case is None:
            ret['message'] = "not fount the case with case's {0}".format(case.task_relative_case_case_id)
            ret['code'] = 1
        channel = find_case.test_cases_channel
        mock_name = find_case.test_cases_mock_name
        program = find_case.test_cases_group.lower()
        obj_name = '{0}{1}AutoTest'.format(channel.replace('_', '').title(), program.title())
        meta_class = importlib.import_module('app.test_cases.china.{0}.{1}'.format(program, obj_name))
        obj = getattr(meta_class, obj_name)(env, environment, mock_name)
        obj.run_single_case(find_case)
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


@api_test_case.route('/get_auto_task_case/<int:task_id>', methods=["POST"])
def get_auto_task_case(task_id):
    ret = deepcopy(RET)
    req = request.json
    pageParams = req.get('pageParams', {'page': 1, "limit": 13})
    case_list = TaskRelativeCase.query.filter(
        TaskRelativeCase.task_relative_case_task_id == task_id).all()
    case_list = tuple([x.task_relative_case_case_id for x in case_list])
    test_case = TestCase.query.filter(TestCase.test_cases_id.in_(case_list)).paginate(
            page=pageParams['page'],
            per_page=pageParams['limit'],
            error_out=True)
    ret["total"] = test_case.total
    ret["data"] = TestCase.to_spec_dicts(test_case.items) if test_case.items else []
    return ret


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
    ret["total"], ret["data"] = get_case_task(program, country, {'page': 1, 'limit': 15})
    return jsonify(ret)


@api_test_case.route('/auto_task', methods=["POST"])
def auto_task():
    ret = deepcopy(RET)
    req = request.json
    program = req.get('program', 'total')
    country = req.get('country', 'china')
    pageParams = req.get('pageParams', {'page': 1, 'limit': 15})
    ret["total"], ret["data"] = get_case_task(program, country, pageParams)
    return jsonify(ret)


def get_case_task(program, country, page_params):
    if program == 'total':
        auto_task_list = json.loads(BackendKeyValue.query.filter(
            BackendKeyValue.backend_key == 'auto_task_list').first().backend_value)
        program = [x['value'] for x in auto_task_list]
        program = tuple(filter(lambda x: x != 'log', program))
    else:
        program = tuple([program],)
    record = CaseTask.query.filter(CaseTask.case_task_country == country,
                                   CaseTask.case_task_program.in_(program)).order_by(
        desc(CaseTask.case_task_id)).paginate(
            page=page_params['page'],
            per_page=page_params['limit'],
            error_out=True)
    return record.total, TestCase.to_spec_dicts(record.items) if record.items else []

