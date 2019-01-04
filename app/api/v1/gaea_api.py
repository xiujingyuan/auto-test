#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
 @author: snow
 @software: PyCharm
 @time: 2019/01/03
 @file: gaea_api.py
 @site:
 @email:
"""


from flask import jsonify, request

from app.api.v1 import api_v1


@api_v1.route('/', methods=['GET', 'POST'])
def index():
    return 'Hello World!'


@api_v1.route('/v1/', methods=['GET', 'POST'])
def v1_index():
    if request.method == "GET":
        data = {"code": 0,
                "method": request.method
                }
    elif request.method == "POST":
        data = {"code": 0,
                "method": request.method
                }
    return jsonify(data)

