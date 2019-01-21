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

from flask import jsonify, request
from app.common.tools.CommonResult import CommonResult

from app.api.v1 import api_v1
from app.bussinse.PrevBiz import PrevBiz as PrevBussinse

@api_v1.route('/prev/<int:case_id>', methods=['GET'])
def get_prev_bycaseid(case_id):
    prev = PrevBussinse()
    result = prev.get_bussinse_data(case_id)
    return jsonify(CommonResult.fill_result(result))


@api_v1.route('/prev/<int:prev_id>', methods=['PUT'])
def change_prev(prev_id):
    prev = PrevBussinse()
    if request.method =="PUT":
        if(prev.check_exists_byprevid(prev_id)):
            prevInfo = request.json
            result = prev.change_prev(prevInfo,prev_id)
    return jsonify(CommonResult.fill_result(result))

@api_v1.route('/prev' , methods=['POST'])
def add_prev():
    prev = PrevBussinse()
    result = prev.add_prev(request)
    return jsonify(CommonResult.fill_result(result))


@api_v1.route('/init/<int:prev_id>' , methods=['DELETE'])
def delete_prev(prev_id):
    prev = PrevBussinse()
    result = prev.delete_prev(prev_id)
    return jsonify(CommonResult.fill_result(result))