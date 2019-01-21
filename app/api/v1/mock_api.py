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
from app.bussinse.MockBiz import MockBiz as MockBussinse


@api_v1.route('/mock/<int:case_id>', methods=['GET'])
def get_mock_bycaseid(case_id):
    mock = MockBussinse()
    result = mock.get_bussinse_data(case_id)
    return jsonify(CommonResult.fill_result(result))


@api_v1.route('/mock/<int:mock_id>', methods=['PUT'])
def change_mock(mock_id):
    mock = MockBussinse()
    if request.method =="PUT":
        if(mock.check_exists_bymockid(mock_id)):
            mockInfo = request.json
            result = mock.change_mock(mockInfo,mock_id)
    return jsonify(CommonResult.fill_result(result))

@api_v1.route('/mock' , methods=['POST'])
def add_mock():
    mock = MockBussinse()
    result = mock.add_mock(request)
    return jsonify(CommonResult.fill_result(result))


@api_v1.route('/init/<int:mock_id>' , methods=['DELETE'])
def delete_mock(mock_id):
    mock = MockBussinse()
    result = mock.delete_mock(mock_id)
    return jsonify(CommonResult.fill_result(result))