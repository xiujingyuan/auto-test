#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
 @author: snow
 @software: PyCharm  
 @time: 2018/12/18
 @file: __init__.py.py
 @site:
 @email:
"""
from app.program_business.china.biz_central.services import ChinaBizCentralAuto
from app.program_business.china.biz_central.xxljob import ChinaBizCentralXxlJob
from app.program_business.china.grant.services import ChinaGrantAuto
from app.program_business.china.repay.easy_mock import RepayEasyMock
from app.program_business.china.repay.nacos import ChinaRepayNacos
from app.program_business.china.repay.services import ChinaRepayAuto
from app.program_business.china.repay.xxljob import ChinaRepayXxlJob

RET = {
        "code": 0,
        "message": "执行成功",
        "data": []
    }


class EasyMockFactory(object):
    @classmethod
    def get_easy_mock(cls, country, program, check_req, return_req):
        if country == 'china' and program == 'repay':
            return RepayEasyMock(check_req, return_req)


class NacosFactory(object):

    @classmethod
    def get_nacos(cls, country, program, env):
        if country == 'china' and program == 'repay':
            return ChinaRepayNacos(env)


class XxlJobFactory(object):

    @classmethod
    def get_xxljob(cls, country, program, env):
        if country == 'china' and program == 'repay':
            return ChinaRepayXxlJob(env)
        if country == 'china' and program == 'biz-central':
            return ChinaBizCentralXxlJob(env)


class AutoFactory(object):

    @classmethod
    def get_auto(cls, country, program, env, run_env):
        if country == 'china' and program == 'repay':
            return ChinaRepayAuto(env, run_env)
