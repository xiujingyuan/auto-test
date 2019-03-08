# -*- coding: utf-8 -*-
# @Time    : 公元19-03-08 下午5:04
# @Author  : 张廷利
# @Site    : 
# @File    : jenkins_api.py
# @Software: IntelliJ IDEA

import jenkins
import json

from flask import jsonify, request
from app.common.tools.CommonResult import CommonResult
from app.api.v1 import api_v1
from app.models.CaseModel import Case
from app.bussinse.CaseBiz import CaseBiz as CaseBussinse


@api_v1.route("/run/case", methods=['POST'])
def run_special_case():
    jenkins_url = "https://jenkins-test.kuainiujinke.com/jenkins/"
    user_id = "zhangtingli"
    user_pwd = "123456"
    case_ids = request.json['case_ids']
    email = request.json['email']
    print(type(request.json))
    print(request.json['case_ids'])
    server = jenkins.Jenkins(jenkins_url,user_id,user_pwd)
    build_number = server.build_job("Auto_Test_Api_Run_Case",parameters={"case_ids":case_ids,"email_address":email})
    return jsonify(CommonResult.fill_result(build_number))



