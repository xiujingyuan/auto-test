#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
 @author: snow
 @software: PyCharm
 @time: 2019/08/14
 @file: tool_api.py
 @site:
 @email:
"""
import json
from flask import Response, current_app, jsonify

from app.api.v1 import api_v1
from app.bussinse.EncryBiz import EncryBiz
from app.bussinse.FourElement import FourElement
from app.common.tools.CommonResult import CommonResult


@api_v1.route('/fourelement', methods=['GET'])
def get_fourelement():
    cs = FourElement()
    result = cs.get()
    encry_biz = EncryBiz()
    try:
        request_dict = result["data"]
        send_data = {
            "card_number": request_dict["bank_code"],
            "idnum": request_dict["id_number"],
            "mobile": request_dict["phone_number"],
            "name": request_dict["user_name"]
            }
        encry_data_list = {}
        for key, value in send_data.items():
            data = encry_biz.generate_data(key, value)
            encry_data = encry_biz.reuqest_encrp(data)
            # result[key] = value
            # encry_key = key + '_encry'
            encry_data_list[key] = encry_data
        result["data"]["bank_code_encrypt"] = encry_data_list["card_number"]
        result["data"]["id_number_encrypt"] = encry_data_list["idnum"]
        result["data"]["phone_number_encrypt"] = encry_data_list["mobile"]
        result["data"]["user_name_encrypt"] = encry_data_list["name"]
    except Exception as e:
        current_app.logger.exception(e)
        error = "{0}:{1} get error. {2}".format(key, value, encry_data)
        return jsonify(CommonResult.fill_result(error))
    return Response(json.dumps(result), mimetype='application/json')
