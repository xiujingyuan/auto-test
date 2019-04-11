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
from app.bussinse.CommonBiz import CommonBiz
from app.bussinse.KeyvalueBiz import KeyvalueBiz



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

