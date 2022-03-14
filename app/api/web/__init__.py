import json
from copy import deepcopy

from flask import Blueprint, request, jsonify
from flask import current_app

from app import db
from app.common import RET
from app.model.Model import Menu, TestCase
from app.test_cases.china.biz_central.QinnongPushAutoTest import QinnongCentralAutoTest


api_web = Blueprint('api_web', __name__)


@api_web.route('/')
def hello_world():
    current_app.logger.info('hello web api!')
    return 'hello web api'


@api_web.route('/menu', methods=["GET"])
def get_menu():
    menu_list = Menu.query.filter(Menu.menu_parent_id == 0).order_by(Menu.menu_order).all()
    ret = deepcopy(RET)
    ret['data'] = get_all_menu(menu_list)
    print(json.dumps(ret['data'], ensure_ascii=False))
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


@api_web.route('/cases', methods=["GET"])
def get_case():
    case_list = TestCase.query.filter(TestCase.test_cases_channel == 'qinnong').order_by(TestCase.test_cases_id).all()
    ret = deepcopy(RET)
    ret['data'] = {'case': list(map(lambda x: x.to_spec_dict, case_list))}
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
    program = find_case.test_cases_group.lower()
    obj = eval('{0}{1}AutoTest'.format(channel.title(), program.title()))(env, environment)
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



