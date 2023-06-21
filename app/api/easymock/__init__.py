import json
from copy import deepcopy

from flask import Blueprint, request, jsonify
from flask import current_app

from app.common import EasyMockFactory, RET
from app.common.easy_mock_util import EasyMock

api_easy_mock = Blueprint('api_easy_mock', __name__)


@api_easy_mock.route('/')
def hello_world():
    current_app.logger.info('hello easy mock api!')
    return 'hello easy mock api'


@api_easy_mock.route('/change', methods=['POST'])
def easy_mock_change():
    get_ret = deepcopy(RET)
    req = request.json
    country = req.get('country', 'china')
    check_req = req.get("check_req", False)
    return_req = req.get("return_req", False)
    project_name = req.get("project_name", None)
    program = req.get('program', 'repay')
    params = req.get('params', None)
    url = req.get('url', None)
    if url is None or params is None or project_name is None:
        get_ret['code'] = 1
        get_ret['message'] = 'params或url没有传递'
    else:
        easy_mock = EasyMockFactory.get_easy_mock(country, program, project_name, check_req, return_req)
        easy_mock.update(url, params)
    return jsonify(get_ret)


@api_easy_mock.route('/modify_mock', methods=['POST'])
def modify_mock():
    get_ret = deepcopy(RET)
    req = request.json
    url = req.get('url', None)
    value = req.get("value", None)
    mock_name = url.split("/")[3]
    easy_mock = EasyMock(mock_name)
    easy_mock.update_by_value(url.split(mock_name)[-1], value)
    return get_ret


@api_easy_mock.route('/<string:operate>', methods=['POST'])
def change_easymock(operate):
    get_ret = deepcopy(RET)
    req = request.json
    check_req = req.pop("check_req", False)
    return_req = req.pop("return_req", False)
    country = req.pop('country', 'china')
    program = req.pop('program', 'repay')
    # try:
    easy_mock = EasyMockFactory.get_easy_mock(country, program, check_req, return_req)
    get_ret['data'] = getattr(easy_mock, operate)(**req)
    # except Exception as e:
    #     get_ret['code'] = 1
    #     get_ret['message'] = str(e)
    return jsonify(get_ret)
