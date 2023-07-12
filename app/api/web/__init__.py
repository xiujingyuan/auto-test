import importlib
import json
from copy import deepcopy

from flask import Blueprint, request, jsonify
from flask import current_app

from app import db
from app.common import RET
from app.common.http_util import Http
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


@api_web.route('/save_desc', methods=["POST"])
def save_desc():
    ret = deepcopy(RET)
    req = request.json
    channel = req.get('channel', None)
    desc = req.get('desc', None)
    desc_recorde = BackendKeyValue.query.filter(BackendKeyValue.backend_key == 'capital_connection_measure').first()
    backend_value = json.loads(desc_recorde.backend_value)
    if channel not in backend_value:
        backend_value[channel] = ''
    backend_value[channel] = desc
    desc_recorde.backend_value = json.dumps(backend_value, ensure_ascii=False)
    db.session.add(desc_recorde)
    db.session.flush()
    return jsonify(ret)


@api_web.route('/save_interface_doc', methods=["POST"])
def save_interface_doc():
    ret = deepcopy(RET)
    req = request.json
    channel = req.get('channel', None)
    label = req.get('label', None)
    url = req.get('url', '')
    rep = req.get('rep', {})
    interface_req = req.get('req', {})
    if channel is None:
        ret['code'] = 1
        return jsonify(ret)
    recorde = BackendKeyValue.query.filter(BackendKeyValue.backend_key == 'interfaceDoc').first()
    backend_value = json.loads(recorde.backend_value)
    if channel not in backend_value:
        backend_value[channel] = []

    if label is not None:
        if label in [x['label'] for x in backend_value[channel]]:
            for item in backend_value[channel]:
                if item['label'] == label:
                    item['url'] = url
                    item['request'] = interface_req
                    item['response'] = rep
                    break
        else:
            backend_value[channel].append({'url': url, 'request': interface_req, 'response': rep,
                                           'label': label})

    recorde.backend_value = json.dumps(backend_value, ensure_ascii=False)
    db.session.add(recorde)
    db.session.flush()
    return jsonify(ret)


@api_web.route('/download_file', methods=['POST'])
def download_file():
    req = request.json
    channel = req.get('channel', None)
    file_dir = req.get('dir', None)
    file_name = req.get('name', None)
    task_result = req.get('task_result', None)
    try:
        task_result = '_'.join(tuple(json.loads(task_result)['data']['pushSerialNo'].split("_")[:-2])) if \
            task_result is not None else task_result
    except Exception as e:
        print(e)
        task_result = None
    channel = channel if task_result is None else task_result
    url = 'https://biz-gateway-proxy.k8s-ingress-nginx.kuainiujinke.com/biz-filegate/ftp/download/' + channel
    req = {
        "from_system": "biz_central",
        "key": "81e99217-ebc0-4d03-b604-bc2b11daddfc",
        "type": "FtpFileDownload",
        "data": {
            "dir": file_dir,
            "name": file_name,
            "resFormat": "bytes"
        }
    }
    ret = Http.http_post(url, req)
    return ret


@api_web.route('/del_interface_doc', methods=["POST"])
def del_interface_doc():
    ret = deepcopy(RET)
    req = request.json
    channel = req.get('channel', None)
    label = req.get('label', None)
    if channel is None:
        ret['code'] = 1
        return jsonify(ret)
    recorde = BackendKeyValue.query.filter(BackendKeyValue.backend_key == 'interfaceDoc').first()
    backend_value = json.loads(recorde.backend_value)
    if channel not in backend_value:
        return

    if label is not None:
        if label in [x['label'] for x in backend_value[channel]]:
            new_value = []
            for item in backend_value[channel]:
                if item['label'] != label:
                    new_value.append(item)
            backend_value[channel] = new_value
    recorde.backend_value = json.dumps(backend_value, ensure_ascii=False)
    db.session.add(recorde)
    db.session.flush()
    return jsonify(ret)


@api_web.route('/add_capital', methods=["POST"])
def add_capital():
    ret = deepcopy(RET)
    req = request.json
    channel = req.get('channel', '')
    label = req.get('label', '')
    country = req.get('country', 'china')
    if channel == '' or label == '':
        ret['code'] = 1
        ret['message'] = "channel or label's value is error!"
        return jsonify(ret)
    channels = BackendKeyValue.query.filter(BackendKeyValue.backend_key == 'channels').first()
    channel_info = json.loads(channels.backend_value)
    periods = BackendKeyValue.query.filter(BackendKeyValue.backend_key == 'periods').first()
    period_info = json.loads(periods.backend_value)
    if channel not in [x['value'] for x in channel_info[country]]:
        channel_info[country].insert(0, {
            "label": label,
            "value": channel
        })
        channels.backend_value = json.dumps(channel_info, ensure_ascii=False)
        db.session.add(channels)
    if channel not in json.loads(periods.backend_value):
        period_info[channel] = [{"value": 12, "label": "12期"}]
        periods.backend_value = json.dumps(period_info, ensure_ascii=False)
        db.session.add(periods)
    db.session.flush()

    return get_backend_key_value()


@api_web.route('/backend_config', methods=["GET"])
def get_backend_key_value():
    key_value_list = BackendKeyValue.query.filter(BackendKeyValue.backend_is_active == 1,
                                                  BackendKeyValue.backend_group == 'backend').all()
    ret = deepcopy(RET)
    backend_config_dict = {'backend_config': {}}
    for item in key_value_list:
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


@api_web.route('/remove_item/', methods=["POST"])
def remove_item():
    req = request.json
    item_no = req.get('item_no', '')
    item_type = req.get('item_type', '0')
    env = req.get('env', '1')
    ret = deepcopy(RET)
    db.session.query(AutoAsset).filter(AutoAsset.asset_name == item_no,
                                       AutoAsset.asset_type == item_type,
                                       AutoAsset.asset_env == env).delete()
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



