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
        email = "zhangtingli@kuainiugroup.com"
        print(current_app.config["JENKINS_URL"],
              current_app.config["USER_ID"],
              current_app.config["USER_PWD"],
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

