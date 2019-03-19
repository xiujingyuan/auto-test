# -*- coding: utf-8 -*-
# @Time    : 公元19-03-19 下午5:37
# @Author  : 张廷利
# @Site    : 
# @File    : encry_api.py
# @Software: IntelliJ IDEA

import requests
from app.bussinse.EncryBiz import EncryBiz
from app.api.v1 import api_v1
from flask import jsonify, request
from app.common.tools.CommonResult import CommonResult

@api_v1.route('/encry-data', methods=['POST'])
def encry_data():
    result = EncryBiz().encry_data(request)
    return jsonify(CommonResult.fill_result(result))


@api_v1.route('/decrypt-data', methods=['POST'])
def deencry_data():
    result = EncryBiz().de_encry_data(request)
    return jsonify(CommonResult.fill_result(result))