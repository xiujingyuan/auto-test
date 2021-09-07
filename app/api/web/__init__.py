from copy import deepcopy

from flask import Blueprint, request, jsonify
from flask import current_app

from app.common import RET
from app.model.MenuDb import Menu

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


def get_all_menu(menu_list):
    ret_menu = []
    for menu in menu_list:
        menu_dict = menu.to_spec_dict
        sub_menu = Menu.query.filter(Menu.menu_parent_id == menu.menu_id).all()
        if sub_menu:
            menu_dict['subs'] = get_all_menu(sub_menu)
        ret_menu.append(menu_dict)
    return ret_menu



