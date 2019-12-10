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
from app.bussinse.ParamsBiz import ParamsBiz

@api_v1.route('/params/<int:params_id>', methods=['GET'])
def get_params_byid(params_id):
    params = ParamsBiz()
    result = params.get_params_byid(params_id)
    #return jsonify(CommonResult.fill_result(result))
    return Response(json.dumps(CommonResult.fill_result(result)),mimetype='application/json')


@api_v1.route('/params/<int:params_id>', methods=['PUT'])
def change_params(params_id):
    params = ParamsBiz()
    if request.method =="PUT":
        paramsInfo = request.json
        result = params.change_params(paramsInfo,params_id)
    return jsonify(CommonResult.fill_result(result))


@api_v1.route('/params', methods=['POST'])
def add_params():
    params = ParamsBiz()
    result = params.add_params(request)
    return jsonify(CommonResult.fill_result(result))


@api_v1.route('/params/search', methods=['POST'])
def search_params():
    params = ParamsBiz()
    result = params.search_params(request)
    return jsonify(CommonResult.fill_result(result))


@api_v1.route('/params/<string:params_name>/<string:params_value>/<string:user>', methods=['POST'])
def change_params_value(params_name, params_value, user):
    params = ParamsBiz()
    result = params.change_params_value(params_name, params_value, user)
    return jsonify(CommonResult.fill_result(result))
