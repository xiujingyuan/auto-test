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
from app.services.china.biz_central.nacos import ChinaBizCentralNacos
from app.services.china.biz_central.services import ChinaBizCentralService
from app.services.china.biz_central.xxljob import ChinaBizCentralXxlJob
from app.services.china.repay.easy_mock import RepayEasyMock
from app.services.china.repay.nacos import ChinaRepayNacos
from app.services.china.repay.services import ChinaRepayService
from app.services.china.repay.xxljob import ChinaRepayXxlJob
from app.services.india.repay.service import IndiaRepayService
from app.services.india.repay.xxljob import IndiaRepayXxlJob

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
        elif country == 'china' and program == 'biz_central':
            return RepayEasyMock(check_req, return_req)


class NacosFactory(object):

    @classmethod
    def get_nacos(cls, country, program, env):
        if country == 'china' and program == 'repay':
            return ChinaRepayNacos(env)
        elif country == 'china' and program == 'biz_central':
            return ChinaBizCentralNacos(env)


class XxlJobFactory(object):

    @classmethod
    def get_xxljob(cls, country, program, env):
        if country == 'china' and program == 'repay':
            return ChinaRepayXxlJob(env)
        elif country == 'china' and program == 'biz_central':
            return ChinaBizCentralXxlJob(env)
        elif country == 'india' and program == 'repay':
            return IndiaRepayXxlJob(env)


class AutoFactory(object):

    @classmethod
    def get_auto(cls, country, program, env, run_env):
        if country == 'china' and program == 'repay':
            return ChinaRepayService(env, run_env)


class RepayServiceFactory(object):
    @classmethod
    def get_repay(cls, country, env, environment):
        if country == 'china':
            return ChinaRepayService(env, environment)
        elif country == 'india':
            return IndiaRepayService(env, environment)


class BizCentralServiceFactory(object):
    @classmethod
    def get_biz_central(cls, country, env, environment):
        if country == 'china':
            return ChinaBizCentralService(env, environment)
