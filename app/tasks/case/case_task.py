#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
 @author: snow
 @software: PyCharm
 @time: 2019/07/10
 @file: case_task.py
 @site:
 @email:
"""

from app import celery
from app.bussinse.CaseBiz import CaseBiz
from flask import jsonify, request,current_app
from app.common.tools.CommonResult import CommonResult
import jenkins
import traceback
import time


@celery.task(bind=True)
def run_special_case(self):
    try:
        case_biz = CaseBiz()
        case_ids = request.json['case_ids']
        email = request.json['email']
        for case in case_ids:
            if not case_biz.check_execstatus_bycaseid(case):
                return jsonify(CommonResult.fill_result(case,1,"case_id:{0} 执行状态不正确不能被执行".format(case)))
        exec_case_array = case_biz.get_exec_caseid(case_ids)
        exec_case_array_str = ','.join(str(case) for case in exec_case_array)
        server = jenkins.Jenkins(current_app.config["JENKINS_URL"],
                                 current_app.config["USER_ID"],
                                 current_app.config["USER_PWD"])
        next_build_number = server.get_job_info('Auto_Test_Api_Run_Case1')['nextBuildNumber']
        build_number = server.build_job('Auto_Test_Api_Run_Case1',
                                        parameters={"case_ids": exec_case_array_str,
                                                    "email_address": email,
                                                    "debug_model": "TestRunCase.py"})
        last_console_output = ""
        while True:
            try:
                build_info = server.get_build_info('Auto_Test_Api_Run_Case1', next_build_number)
                console_output = server.get_build_console_output("Auto_Test_Api_Run_Case1", next_build_number)
            except:
                pass
            else:
                console_output = console_output.strip("\r\n").strip("\n")
                if console_output:
                    if last_console_output:
                        console_output = console_output.replace(last_console_output, "")
                    if console_output:
                        last_console_output += console_output
                        console_output = console_output.strip("\r\n").strip("\n")
                        print(console_output)
                if not build_info["building"]:
                    break
        return jsonify(CommonResult.fill_result(build_number))
    except Exception as e:
        current_app.logger.exception(traceback.format_exc())
        return jsonify(CommonResult.fill_result(0, 1, str(e)))


@celery.task(bind=True)
def run_case_by_case_id(self, case_id):
    try:
        case_ids = [case_id]
        email = "zhangtingli@kuainiugroup.com"
        exec_case_array_str = ','.join(str(case) for case in case_ids)
        server = jenkins.Jenkins(current_app.config["JENKINS_URL"],
                                 current_app.config["USER_ID"],
                                 current_app.config["USER_PWD"])
        next_build_number = server.get_job_info('Auto_Test_Api_Run_Case1')['nextBuildNumber']
        build_number = server.build_job("Auto_Test_Api_Run_Case1",
                                        parameters={"case_ids": exec_case_array_str,
                                                    "email_address": email,
                                                    "debug_model": "testDebug.py"})
        last_console_output = ""
        total = len(case_ids) * 10
        i = 0
        while True:
            try:
                build_info = server.get_build_info('Auto_Test_Api_Run_Case1', next_build_number)
                console_output = server.get_build_console_output("Auto_Test_Api_Run_Case1", next_build_number)
            except:
                pass
            else:
                console_output = console_output.strip("\r\n").strip("\n")
                if console_output:
                    if last_console_output:
                        console_output = console_output.replace(last_console_output, "")
                    if console_output and console_output not in last_console_output:
                        last_console_output += console_output
                        console_output = console_output.strip("\r\n").strip("\n")
                        print(console_output)
                    self.update_state(state='PROGRESS',
                                      meta={'current': i,
                                            'total': total,
                                            'status': console_output})
                    i += 1
                if not build_info["building"]:
                    break
                time.sleep(0.1)
        return self.update_state(state='PROGRESS',
                                 meta={'current': total,
                                       'total': total,
                                       'status': ""})
    except Exception as e:
        current_app.logger.exception(traceback.format_exc())
        return self.update_state(state='PROGRESS',
                                 meta={'current': i,
                                       'total': total,
                                       'status': traceback.format_exc()})

