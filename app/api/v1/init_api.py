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
from app.bussinse.InitBiz import InitBiz as InitBussinse


@api_v1.route('/init/<int:case_id>', methods=['GET'])
def get_init_bycaseid(case_id):

    init = InitBussinse()
    result = init.get_bussinse_data(case_id)
    return jsonify(CommonResult.fill_result(result))


@api_v1.route('/init/id/<int:inid_id>', methods=['GET'])
def get_init_byinitid(inid_id):

    init = InitBussinse()
    result = init.get_bussinse_data_by_initid(inid_id)
    #return jsonify(CommonResult.fill_result(result))
    return Response(json.dumps(CommonResult.fill_result(result)),mimetype='application/json')


@api_v1.route('/init/<int:init_id>', methods=['PUT'])
def change_init(init_id):
    init = InitBussinse()
    if request.method =="PUT":
        if(init.check_exists_byinitid(init_id)):
            initInfo = request.json
            result = init.change_init(initInfo,init_id)
    return jsonify(CommonResult.fill_result(result))


@api_v1.route('/init', methods=['POST'])
def add_init():
    init = InitBussinse()
    result = init.add_init(request)
    return jsonify(CommonResult.fill_result(result))


@api_v1.route('/init/<int:init_id>', methods=['DELETE'])
def delete_init(init_id):
    init = InitBussinse()
    result = init.delete_init(init_id)
    return jsonify(CommonResult.fill_result(result))


@api_v1.route('/init_priority', methods=['PUT'])
def init_priority():
    init = InitBussinse()
    result = init.init_priority(request)
    return jsonify(CommonResult.fill_result(result))
