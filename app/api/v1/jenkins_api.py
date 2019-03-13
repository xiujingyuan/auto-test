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
from app.bussinse.CaseBiz import CaseBiz


@api_v1.route("/run/case", methods=['POST'])
def run_special_case():
    try:
        case_biz = CaseBiz()
        jenkins_url = "https://jenkins-test.kuainiujinke.com/jenkins/"
        user_id = "zhangtingli"
        user_pwd = "123456"
        case_ids = request.json['case_ids']
        confirm_cases=[]
        email = request.json['email']
        print(case_ids)
        for case in case_ids:
            if case_biz.check_execstatus_bycaseid(case)==False:
                return jsonify(CommonResult.fill_result(case,1,"case_id:{0} 执行状态不正确不能被执行".format(case)))
        exec_case_array = case_biz.get_exec_caseid(case_ids)
        exec_case_array_str = ','.join(str(case) for case in exec_case_array)
        server = jenkins.Jenkins(jenkins_url,user_id,user_pwd)

        build_number = server.build_job("Auto_Test_Api_Run_Case",parameters={"case_ids":exec_case_array_str,"email_address":email})
        return jsonify(CommonResult.fill_result(build_number))
    except Exception as e:
        return jsonify(CommonResult.fill_result(build_number,1,"jenkins 构建失败"))




