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
from flask import jsonify, request, render_template, url_for
from app.tasks.case.case_task import run_special_case, run_case_by_case_id
from app.tasks import task_url
from app.tasks.test.test_task import long_task


@task_url.route("/tasks/status/<task_id>", methods=["GET"])
def task_status(task_id):
    task = long_task.AsyncResult(task_id)
    if task.state == 'PENDING':
        # job did not start yet
        response = {
            'state': task.state,
            'current': 0,
            'total': 1,
            'status': 'Pending...'
        }
    elif task.state != 'FAILURE':
        response = {
            'state': task.state,
            'current': task.info.get('current', 0),
            'total': task.info.get('total', 1),
            'status': task.info.get('status', '')
        }
        if 'result' in task.info:
            response['result'] = task.info['result']
    else:
        # something went wrong in the background job
        response = {
            'state': task.state,
            'current': 1,
            'total': 1,
            'status': str(task.info),  # this is the exception raised
        }
    return jsonify(response)


@task_url.route("/tasks/long_task", methods=["GET"])
def task_create():
    task = long_task.apply_async()
    return jsonify({"Location": '/tasks/status/{0}'.format(task.id)}), 202


@task_url.route("/tasks/case_task_status/status/<run_id>", methods=["GET"])
def case_task_status(run_id):
    task = run_case_by_case_id.AsyncResult(run_id)
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


@task_url.route("/tasks/case_task_create/<task_id>", methods=["GET"])
def case_task_create(task_id):
    task = run_case_by_case_id.apply_async(args=[task_id])
    return jsonify({"Location": '/tasks/case_task_status/status/{0}'.format(task.id), "code": 202})

