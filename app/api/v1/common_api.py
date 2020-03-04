#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
 @author: snow
 @software: PyCharm
 @time: 2019/01/03
 @file: case_api.py
 @site:
 @email:
"""

import json

from flask import jsonify, request,current_app
from app.common.tools.CommonResult import CommonResult

from app.api.v1 import api_v1
from app.bussinse.CommonBiz import CommonBiz
from app.bussinse.KeyvalueBiz import KeyvalueBiz
from app.bussinse.TableSyncBiz import TableSyncBiz
from app.bussinse.ReportBiz import ReportBiz



@api_v1.route('/common/getdblist', methods=['GET'])
def get_variable_database_list():
    common = CommonBiz()
    result = common.get_variable_database_list()
    return jsonify(CommonResult.fill_result(result))


@api_v1.route('/common/getprevflag', methods=['GET'])
def get_prev_flag():
    common = CommonBiz()
    result = common.get_prev_flag()
    return jsonify(CommonResult.fill_result(result))


@api_v1.route('/common/sync/keyvalue',methods=["POST"])
def sync_keyvalue():
    common = KeyvalueBiz()
    result = common.sync_keyvalue(request)
    return jsonify(CommonResult.fill_result(result))


@api_v1.route('/common/tools',methods=["GET"])
def common_tools():
    common = CommonBiz()
    result =common.get_common_tools()
    return jsonify(CommonResult.fill_result(result))

@api_v1.route('/common/sync/tables',methods=["POST"])
def sync_tables():
    common = TableSyncBiz()
    result = common.sync_tables(request)
    return jsonify(CommonResult.fill_result(result))


@api_v1.route('/common/sendmail',methods=["POST"])
def send_mail():
    common = CommonBiz()
    result = common.sendMail(request)
    return jsonify(CommonResult.fill_result(result))


@api_v1.route('/common/capital-plan',methods=["POST"])
def capital_plan():
    common = CommonBiz()
    result = common.capitalPlan(request)
    return jsonify(CommonResult.fill_result(result))


@api_v1.route('/common/withdraw-success',methods=["POST"])
def withdraw_success():
    common = CommonBiz()
    result = common.grantWithdrawSuccess(request)
    return jsonify(CommonResult.fill_result(result))


@api_v1.route('/common/prev-flag',methods=['GET'])
def search_prev_flag():
    cs = CommonBiz()
    result = cs.get_prev_flag()
    return jsonify(CommonResult.fill_result(result))


@api_v1.route('/common/from-system',methods=['GET'])
def search_from_system():
    cs = CommonBiz()
    result = cs.get_from_system()
    return jsonify(CommonResult.fill_result(result))


@api_v1.route('/grant/withdraw-success',methods=["POST"])
def grant_withdraw_success():
    common = CommonBiz()
    result = common.grantWithdrawSuccess(request)
    return jsonify(CommonResult.fill_result(result))


@api_v1.route('/repay/withhold-success',methods=["POST"])
def repay_withhold_success():
    common = CommonBiz()
    result = common.repayWithholdSuccess(request)
    return jsonify(CommonResult.fill_result(result))

@api_v1.route('/quickly-repay',methods=["POST"])
def quickly_repay():
    common = CommonBiz()
    result = common.QuicklyRepay(request)
    return jsonify(CommonResult.fill_result(result))


@api_v1.route('/common/upload/file',methods=['POST'])
def upload_file():
    cmmon = CommonBiz()
    result = cmmon.upload_save_file(request)
    return jsonify(CommonResult.fill_result(result))


@api_v1.route('/common/set-capital-loan-condition',methods=['POST'])
def set_capital_loan_condition():
    common = CommonBiz()
    result = common.set_capital_loan_condition(request)
    return jsonify(CommonResult.fill_result(result))


@api_v1.route('/grant/auto_route',methods=["POST"])
def grant_auto_route_success():
    common = CommonBiz()
    result, msg = common.grant_auto_route_success(request)
    return jsonify(CommonResult.fill_result(result, message=msg))


@api_v1.route('/grant/success_four_elements',methods=["POST"])
def grant_four_elements_success():
    common = CommonBiz()
    result, msg = common.grant_four_elements_success(request)
    return jsonify(CommonResult.fill_result(result, message=msg))


@api_v1.route('/grant-global/withdraw-success',methods=["POST"])
def grant_global_withdraw_success():
    common = CommonBiz()
    result, msg = common.grant_global_withdraw_success(request)
    return jsonify(CommonResult.fill_result(result, message=msg))

@api_v1.route('/grant/account_test',methods=["POST"])
def grant_open_account_success():
    common = CommonBiz()
    result, msg = common.grant_open_account_success(request)
    return jsonify(CommonResult.fill_result(result,message=msg))
