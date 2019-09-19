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

from flask import jsonify, request,Response
from app.common.tools.CommonResult import CommonResult
from app.api.v1 import api_v1
from app.bussinse.CaseBiz import CaseBiz as CaseBussinse


@api_v1.route('/case/<int:caseid>', methods=['PUT', 'GET', 'DELETE'])
def get_case_data_bycaseid(caseid):
    cs = CaseBussinse()
    if request.method == "PUT":
        if cs.check_exists_bycaseid(caseid):
            basicInfo = request.json if "flag" in request.json else request.json['case']['basicInfo']
            result = cs.change_case(basicInfo, caseid)
    elif request.method == "GET":
        result = cs.get_bussinse_data(caseid)

    elif request.method == "DELETE":
        result = cs.delete_case_bycaseid(caseid)

    result = CommonResult.fill_result(result)
    #return jsonify(result)
    return Response(json.dumps(result), mimetype='application/json')


@api_v1.route('/case', methods=['POST'])
def add_case():
    """
    添加用例接口
    :return: 返回是否添加成功
    """
    cs = CaseBussinse()
    result = cs.add_case(request)
    if result == 0:
        return jsonify(CommonResult.fill_result(0, 0, "添加用例失败"))
    return jsonify(CommonResult.fill_result(result))


@api_v1.route('/case/check_group', methods=['POST'])
def check_group():
    """
    添加用例接口
    :return: 返回是否添加成功
    """
    cs = CaseBussinse()
    result, error_message = cs.check_group(request)
    return jsonify(CommonResult.fill_result(result, message=error_message))


@api_v1.route('/case/copy_all', methods=['POST'])
def copy_case_all():
    """
    批量复制用例
    :return: 返回复制是否成功
    """
    cs = CaseBussinse()
    result, error_message = cs.copy_all(request)
    return jsonify(CommonResult.fill_result(result, message=error_message))


@api_v1.route('/case/search', methods=['POST'])
def search_case():
    cs = CaseBussinse()
    result = cs.search_case(request)
    return jsonify(CommonResult.fill_result(result))


@api_v1.route('/summary/search', methods=['GET'])
def summary_case():
    cs = CaseBussinse()
    result = cs.get_summary_case()
    return jsonify(CommonResult.fill_result(result))


@api_v1.route('/copy/group', methods=['POST'])
def copy_group_case():
    """
    复制用例接口
    :return:返回是否复制成功
    """
    cs = CaseBussinse()
    result, error_message = cs.copy_group_case(request)
    return jsonify(CommonResult.fill_result(result, message=error_message))


@api_v1.route('/case/last_case', methods=['GET'])
def get_new_cases():
    result, error_message = CaseBussinse.get_new_cases()
    return jsonify(CommonResult.fill_result(result, message=error_message))


@api_v1.route('/case/all', methods=['GET'])
def get_all_cases():
    result, error_message = CaseBussinse.get_all_cases()
    return jsonify(CommonResult.fill_result(result, message=error_message))
