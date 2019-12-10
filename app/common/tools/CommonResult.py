# -*- coding: utf-8 -*-
# @Title: CommonResult
# @ProjectName gaea-api
# @Description: TODO
# @author fyi zhang
# @date 2019/1/6 16:00

from app.models.ErrorCode import ErrorCode


class CommonResult(object):
    @staticmethod
    def fill_result(data, code=None, message=None):
        if message is None:
            message = "success"
        if code is None:
            if isinstance(data,int) and data == ErrorCode.ERROR_CODE:
                code = 1
                message = "fail"
            else:
                code = 0

        res = {
            "code": code,
            "msg": message,
            "data": data,
        }
        return res

