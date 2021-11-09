from copy import deepcopy

from flask import Blueprint, request, jsonify
from flask import current_app

from app import db
from app.common import RET
from app.model.Model import Menu, TestCase

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
            menu_dict['subs'] = get_all_menu(sub_menu)
        ret_menu.append(menu_dict)
    return {'menu': ret_menu}



