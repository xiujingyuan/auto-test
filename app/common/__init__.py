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
from app.program_business.china.biz_central import ChinaBizCentralXxlJob, ChinaBizDb
from app.program_business.china.repay import RepayEasyMock, ChinaRepayXxlJob, ChinaRepayNacos, ChinaRepayDb


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


class DbFactory(object):

    @classmethod
    def get_db(cls, country, program, env, run_env):
        if country == 'china' and program == 'repay':
            return ChinaRepayDb(env, run_env)
        elif country == 'china' and program == 'biz-central':
            return ChinaBizDb(env, run_env)


class XxlJobFactory(object):

    @classmethod
    def get_xxljob(cls, country, program, env):
        if country == 'china' and program == 'repay':
            return ChinaRepayXxlJob(env)
        if country == 'china' and program == 'biz-central':
            return ChinaBizCentralXxlJob(env)
