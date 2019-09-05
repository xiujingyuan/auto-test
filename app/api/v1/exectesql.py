# -*- coding: utf-8 -*-
# @Time    : 公元19-08-30 下午4:27
# @Author  : piay
# @Site    :
# @File    : executesql.py
# @Software: IntelliJ IDEA

import requests
from app.api.v1 import api_v1
from flask import jsonify, request
from app.common.tools.CommonResult import CommonResult
from app.bussinse.executesql import Executesql


@api_v1.route("/execute-sql",method=["POST"])
def execute_sql():
    execute=Executesql()
    result = execute.executesql(request)
    return jsonify(CommonResult.fill_result(result))