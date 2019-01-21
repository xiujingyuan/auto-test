# -*- coding: utf-8 -*-
# @Title: CommonResult
# @ProjectName gaea-api
# @Description: TODO
# @author fyi zhang
# @date 2019/1/6 16:00

class CommonResult(object):

    @staticmethod
    def fill_result(data,code=None,message=None):
        if message is None:
            message ="success"
        if code is None:
            code=0
        res = {
            "code":code,
            "msg" : message,
            "data":data,
        }
        return res

