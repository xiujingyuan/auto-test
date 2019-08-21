#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
 @author: snow
 @software: PyCharm
 @time: 2019/07/09
 @file: task_view.py
 @site:
 @email:
"""

from flask import jsonify, request
from app.tasks.build_task.build_task import run_build_task
from app.tasks import task_url


@task_url.route("/tasks/build_task_status/status/<run_id>", methods=["GET"])
def build_task_status(run_id):
    task = run_build_task.AsyncResult(run_id)
    if task.state == 'PENDING':
        # job did not start yet
        response = {
            'state': task.state,
            'current': 0,
            'total': 1,
            'status': 'Pending...',
            'message': ''
        }
    elif task.state != 'FAILURE':
        response = {
            'state': task.state,
            'current': task.info.get('current', 0) if task.info is not None else 1,
            'total': task.info.get('total', 1) if task.info is not None else 1,
            'status': task.info.get('status', '') if task.info is not None else "",
            'message': task.info.get('message', '') if task.info is not None else ""
        }
        if task is not None and task.info is not None and 'result' in task.info:
            response['result'] = task.info['result']
        else:
            response['result'] = "error"
    else:
        # something went wrong in the background job
        response = {
            'state': task.state,
            'current': 1,
            'total': 1,
            'status': str(task.info),  # this is the exception raised
            'message': str(task.info)
        }
    return jsonify(response)


@task_url.route("/tasks/build_task_create/<build_task_id>", methods=["POST"])
def build_task_create(build_task_id):
    req_data = request.json
    if "job_name" not in req_data:
        return jsonify({"Location": 'job_name need', "code": 606})
    elif "env" not in req_data:
        return jsonify({"Location": 'env need', "code": 606})
    task = run_build_task.apply_async(args=[build_task_id, req_data["job_name"], req_data["env"]])
    return jsonify({"Location": '/tasks/build_task_status/status/{0}'.format(task.id), "code": 202})

