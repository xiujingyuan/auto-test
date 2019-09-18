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
from flask import current_app
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
        current_app.logger.info("{0}, {1}, {2}, {3}, {4}".format(
            current_app.config["JENKINS_URL"],
            jenkins_job,
            env,
            current_app.config["USER_ID"],
            current_app.config["USER_PWD"]
        ))

        server = jenkins.Jenkins(current_app.config["JENKINS_URL"],
                                 username=current_app.config["USER_ID"],
                                 password=current_app.config["USER_PWD"])
        next_build_number = server.get_job_info(jenkins_job)['nextBuildNumber']
        current_app.logger.info("next_build_number is : {0}".format(next_build_number))
        build_number = server.build_job(jenkins_job,
                                        parameters=env)
        current_app.logger.info("build_number is : {0}".format(build_number))
        last_console_output = ""

        while True:
            try:
                build_info = server.get_build_info(jenkins_job, next_build_number)
                console_output = server.get_build_console_output(jenkins_job, next_build_number)
            except:
                pass
            else:
                console_output = console_output.strip("\r\n").strip("\n")
                current_app.logger.info(console_output)
                current_app.logger.info(last_console_output)
                if console_output:
                    if last_console_output:
                        console_output = console_output.replace(last_console_output, "")
                    if console_output and console_output not in last_console_output:
                        last_console_output += console_output
                        console_output = console_output.strip("\r\n").strip("\n")
                    self.update_state(state='PROGRESS',
                                      meta={'current': i,
                                            'total': total,
                                            'status': console_output,
                                            'build_num': next_build_number})
                    i += 1
                if not build_info["building"]:
                    break
                time.sleep(0.1)
        while True:
            console_output = server.get_build_console_output(jenkins_job, next_build_number)
            console_output_list = console_output.strip("\n").split("\n")
            if console_output_list[-1].startswith("Finished:"):
                if "failure" in console_output.lower():
                    result = "FAILURE"
                break
            time.sleep(1)
        self.update_state(state="SUCCESS",
                          meta={'current': total,
                                'total': total,
                                'result': result,
                                'status': "",
                                'build_num': next_build_number})
        time.sleep(1)
    except jenkins.JenkinsException:
        current_app.logger.error("jenkins的的参数错误！")
        self.update_state(state='FAILURE',
                          meta={'current': i,
                                'total': total,
                                'result': 'error',
                                'status': "jenkins任务构建失败",
                                'build_num': next_build_number})
    except Exception as e:
        current_app.logger.exception(e)
        self.update_state(state='FAILURE',
                          meta={'current': i,
                                'total': total,
                                'result': 'error',
                                'status': traceback.format_exc(),
                                'build_num': next_build_number})

