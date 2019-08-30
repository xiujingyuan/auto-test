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
def run_build_task(self, build_task_id, jenkins_job, env):
    try:
        i = 0
        total = 100
        result = "SUCCESS"
        email = "zhangtingli@kuainiugroup.com"
        print(current_app.config["JENKINS_URL"],
              jenkins_job,
              env)
        server = jenkins.Jenkins(current_app.config["JENKINS_URL"],
                                 current_app.config["USER_ID"],
                                 current_app.config["USER_PWD"])
        next_build_number = server.get_job_info(jenkins_job)['nextBuildNumber']
        build_number = server.build_job(jenkins_job,
                                        parameters=env)
        last_console_output = ""

        while True:
            try:
                build_info = server.get_build_info(jenkins_job, next_build_number)
                console_output = server.get_build_console_output(jenkins_job, next_build_number)
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
        console_output_list = console_output.split("\n")
        if not console_output_list[-1].startswith("Finished:"):
            console_output = server.get_build_console_output(jenkins_job, next_build_number)
            console_output = console_output.replace(last_console_output, "")
        if "failure" in console_output.lower():
            result = "FAILURE"
        self.update_state(state="SUCCESS",
                          meta={'current': total,
                                'total': total,
                                'result': result,
                                'status': ""})
        time.sleep(1)
    except Exception as e:
        current_app.logger.exception(traceback.format_exc())
        self.update_state(state='FAILURE',
                          meta={'current': i,
                                'total': total,
                                'result': 'error',
                                'status': traceback.format_exc()})

