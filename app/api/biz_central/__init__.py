from copy import deepcopy
from flask import Blueprint, request, jsonify
from flask import current_app
from app.common import RET, BizCentralServiceFactory, RepayServiceFactory

api_biz_central = Blueprint('api_biz_central', __name__)


@api_biz_central.route('/')
def hello_world():
    current_app.logger.info('hello biz central api!')
    return 'hello biz central api'


@api_biz_central.route('/biz_central_tools/<string:tool>', methods=["POST"])
def biz_central_tools(tool):
    ret = deepcopy(RET)
    req = request.json
    country = req.pop('country', 'china')
    env = req.pop('env', None)
    environment = req.pop('environment', 'dev')
    item_no = req.pop('item_no') if tool == 'run_xxl_job' else req.get('item_no')
    repay = RepayServiceFactory.get_repay(country, env, environment)
    max_create_at = repay.get_date(is_str=True, days=-3)
    asset = repay.get_asset(item_no)
    request_no_tuple, serial_no_tuple, id_num_encrypt_tuple, item_no_tuple, withhold_order = \
            repay.get_withhold_key_info(item_no, max_create_at=max_create_at)
    central = BizCentralServiceFactory.get_biz_central(country, env, environment)
    central.get_withhold_key_info = [request_no_tuple, serial_no_tuple, id_num_encrypt_tuple, item_no_tuple,
                                     withhold_order]
    central.asset = asset
    ret['data'] = getattr(central, tool)(**req)
    return jsonify(ret)
