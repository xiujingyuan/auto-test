# -*- coding: utf-8 -*-
# @Time    : 2019/5/27 10:01
# @Author  : 张廷利
# @Site    :
# @File    : report_api.py
# @Software: IntelliJ IDEA

from flask import jsonify, request
from app.common.tools.CommonResult import CommonResult

from app.api.v1 import api_v1
from app.bussinse.ReportBiz import ReportBiz


@api_v1.route('/report/write-report',methods=['POST'])
def report_writeport():
    report = ReportBiz()
    result = report.transfer_params(request)
    print(result)
    return jsonify(CommonResult.fill_result(result))


@api_v1.route('/report/search',methods=['POST'])
def search_report():
    report = ReportBiz()
    result = report.search_report(request)
    # print(result)
    return jsonify(CommonResult.fill_result(result))


@api_v1.route('/report/report-detail',methods=['POST'])
def search_report_detail():
    report = ReportBiz()
    result = report.get_report_detail(request)
    # print(result)
    return jsonify(CommonResult.fill_result(result))

@api_v1.route('/report/capturescreen',methods=['POST'])
def capture_screen():
    report = ReportBiz()
    request_json = request.json
    result = report.capture_screen_report(request_json['url'],request_json['path'])
    if result==0:
        report_dict = request_json['report']
        trans_dict = request_json['trans']
        report_result = report.write_report(report_dict,trans_dict)
    return jsonify(CommonResult.fill_result(report_result))
