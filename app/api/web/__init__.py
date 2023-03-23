import importlib
import json
from copy import deepcopy

from flask import Blueprint, request, jsonify
from flask import current_app

from app import db
from app.common import RET
from app.model.Model import Menu, TestCase, BackendKeyValue, AutoAsset, CaseTask

api_web = Blueprint('api_web', __name__)


@api_web.route('/')
def hello_world():
    current_app.logger.info('hello web api!')
    return 'hello web api'


@api_web.route('/menu', methods=["GET"])
def get_menu():
    menu_list = Menu.query.filter(Menu.menu_parent_id == 0, Menu.menu_active == 1).order_by(Menu.menu_order).all()
    ret = deepcopy(RET)
    ret['data'] = get_all_menu(menu_list)
    return jsonify(ret)


@api_web.route('/backend_config', methods=["GET"])
def get_backend_key_value():
    key_value_list = BackendKeyValue.query.filter(BackendKeyValue.backend_is_active == 1,
                                                  BackendKeyValue.backend_group == 'backend').all()
    ret = deepcopy(RET)
    backend_config_dict = {'backend_config': {}}
    for item in key_value_list:
        print(item.backend_key)
        backend_config_dict['backend_config'][item.backend_key] = json.loads(item.backend_value)
    ret['data'] = backend_config_dict
    return jsonify(ret)


@api_web.route('/table', methods=["GET"])
def get_table():
    ret = deepcopy(RET)
    ret['data'] = {
        "list": [{
                "id": 1,
                "name": "张三",
                "money": 123,
                "address": "广东省东莞市长安镇",
                "state": "成功",
                "date": "2019-11-1",
                "thumb": "https://lin-xin.gitee.io/images/post/wms.png"
            },
            {
                "id": 2,
                "name": "李四",
                "money": 456,
                "address": "广东省广州市白云区",
                "state": "成功",
                "date": "2019-10-11",
                "thumb": "https://lin-xin.gitee.io/images/post/node3.png"
            },
            {
                "id": 3,
                "name": "王五",
                "money": 789,
                "address": "湖南省长沙市",
                "state": "失败",
                "date": "2019-11-11",
                "thumb": "https://lin-xin.gitee.io/images/post/parcel.png"
            },
            {
                "id": 4,
                "name": "赵六",
                "money": 1011,
                "address": "福建省厦门市鼓浪屿",
                "state": "成功",
                "date": "2019-10-20",
                "thumb": "https://lin-xin.gitee.io/images/post/notice.png"
            }
        ],
        "pageTotal": 4
    }
    return jsonify(ret)


@api_web.route('/cases/<string:country>/<string:program>', methods=["GET"])
def get_case(country, program):
    case_list = TestCase.query.filter(TestCase.test_cases_country == country,
                                      TestCase.test_cases_group == program).order_by(TestCase.test_cases_id).all()
    ret = deepcopy(RET)
    ret['data'] = {'case': list(map(lambda x: x.to_spec_dict, case_list))}
    return jsonify(ret)


@api_web.route('/auto_task', methods=["POST"])
def auto_task():
    ret = deepcopy(RET)
    req = request.json
    program = req.get('program', 'total')
    country = req.get('country', 'china')
    record = CaseTask.query.filter(CaseTask.case_task_country == country).all()
    if country != 'total':
        record = [x for x in record if x.case_task_program == program]
    ret['data'] = list(map(lambda x: x.to_spec_dict, record))
    return jsonify(ret)


@api_web.route('/remove_item/<string:item_no>', methods=["POST"])
def remove_item(item_no):
    ret = deepcopy(RET)
    db.session.query(AutoAsset).filter(AutoAsset.asset_name == item_no).delete()
    db.session.flush()
    return jsonify(ret)


@api_web.route('/run_single_case', methods=["POST"])
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


@api_web.route('/update_single_case', methods=["POST"])
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


def get_all_menu(menu_list):
    ret_menu = []
    for menu in menu_list:
        menu_dict = menu.to_spec_dict
        sub_menu = Menu.query.filter(Menu.menu_parent_id == menu.menu_id).all()
        if sub_menu:
            menu_dict['subs'] = get_all_menu(sub_menu)['menu']
        ret_menu.append(menu_dict)

    ret_menu = change_menu(ret_menu)

    return {'menu': ret_menu}


def change_menu(menu, include=['icon', 'index', 'title']):
    ret = []
    for item in menu:
        menu_dict = {}
        for key in item:
            if key in include:
                menu_dict[key] = item[key]
            elif key == 'subs':
                menu_dict[key] = change_menu(item[key])
        ret.append(menu_dict)
    return ret



