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
from app.models.CaseModel import Case
from app.bussinse.CaseBiz import CaseBiz as CaseBussinse

@api_v1.route('/case/<int:caseid>', methods=['PUT','GET'])
def get_case_data_bycaseid(caseid):
    cs = CaseBussinse()
    if request.method =="PUT":
        if(Case.check_exists_bycaseid(caseid)):
            basicInfo = request.json['basicInfo']
            result = cs.change_case(basicInfo,caseid)
    else:
        result = cs.get_bussinse_data(caseid)
    return jsonify(CommonResult.fill_result(result))



@api_v1.route('/case' , methods=['POST'])
def add_case():

    cs = CaseBussinse()
    result = cs.add_case(request)
    if result ==0:
        return jsonify(CommonResult.fill_result(0,0,"添加用例失败"))
    return jsonify(CommonResult.fill_result(result))


@api_v1.route('/case/search',methods=['POST'])
def search_case():
    cs = CaseBussinse()
    result = cs.search_case(request)
    return jsonify(CommonResult.fill_result(result))


