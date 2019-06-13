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

from flask import jsonify, request,current_app,Response
from app.common.tools.CommonResult import CommonResult

from app.api.v1 import api_v1
from app.bussinse.HistoryBiz import HistoryBiz



@api_v1.route('/history/search',methods=['POST'])
def search_history():
    cs = HistoryBiz()
    #current_app.logger.info("history begin")
    result = cs.search_history(request)
    #return jsonify(CommonResult.fill_result(result))

    return Response(json.dumps(CommonResult.fill_result(result)),mimetype='application/json')


@api_v1.route('/history/last_update', methods=['GET'])
def last_update_history():
    """
    获取最新执行的报告，前八
    :return:
    """
    result = HistoryBiz.last_update_history()
    return Response(json.dumps(CommonResult.fill_result(result)), mimetype='application/json')
