# -*- coding: utf-8 -*-
# @Time    : 公元19-03-08 下午5:04
# @Author  : 张廷利
# @Site    :
# @File    : jenkins_api.py
# @Software: IntelliJ IDEA
import traceback

import jenkins
import json

from flask import jsonify, request,current_app
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
        email = request.json['email']
        print(case_ids)
        for case in case_ids:
            if case_biz.check_execstatus_bycaseid(case)==False:
                return jsonify(CommonResult.fill_result(case,1,"case_id:{0} 执行状态不正确不能被执行".format(case)))
        exec_case_array = case_biz.get_exec_caseid(case_ids)
        exec_case_array_str = ','.join(str(case) for case in exec_case_array)
        server = jenkins.Jenkins(jenkins_url,user_id,user_pwd)
        print(server.get_all_jobs())
        next_build_number = server.get_job_info('Auto_Test_Api_Run_Case1')['nextBuildNumber']
        build_number = server.build_job('Auto_Test_Api_Run_Case1',parameters={"case_ids":exec_case_array_str,"email_address":email,"debug_model":"TestRunCase.py"})
        from time import sleep
        sleep(10)
        while True:
            build_info = server.get_build_info('Auto_Test_Api_Run_Case1', next_build_number)
            print(build_info["building"])
            console_output = server.get_build_console_output("Auto_Test_Api_Run_Case1", next_build_number)
            current_app.logger.info(console_output)
            if not build_info["building"]:
                break
        return jsonify(CommonResult.fill_result(build_number))
    except Exception as e:
        current_app.logger.exception(traceback.format_exc())
        return jsonify(CommonResult.fill_result(0,1,str(e)))


@api_v1.route("/run/case/<case_id>", methods=['GET'])
def run_case_bycaseid(case_id):
    try:
        case_biz = CaseBiz()
        jenkins_url = "https://jenkins-test.kuainiujinke.com/jenkins/"
        user_id = "zhangtingli"
        user_pwd = "123456"
        case_ids = []
        case_ids.append(case_id)
        email = request.args.get("email")
        if email is None or email=="":
            email = "zhangtingli@kuainiugroup.com"
        print(type(case_id))
        for case in case_ids:
            if case_biz.check_execstatus_bycaseid(case)==False:
                return jsonify(CommonResult.fill_result(case,1,"case_id:{0} 执行状态不正确不能被执行".format(case)))
        server = jenkins.Jenkins(jenkins_url,user_id,user_pwd)
        build_number = server.build_job("Auto_Test_Api_Run_Case1",parameters={"case_ids":int(case_id),"email_address":email,"debug_model":"testDebug.py"})
        console_output = server.get_build_console_output("Auto_Test_Api_Run_Case1", build_number[0])
        current_app.logger.info(console_output)
        return jsonify(CommonResult.fill_result(build_number))
    except Exception as e:
        current_app.logger.exception(e)
        return jsonify(CommonResult.fill_result(0,1,str(e)))



