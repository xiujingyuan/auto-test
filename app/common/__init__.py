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
import importlib

from app.services.china.biz_central.service import ChinaBizCentralService
from app.services.china.repay.service import ChinaRepayService

RET = {
        "code": 0,
        "message": "执行成功",
        "data": []
    }


class EasyMockFactory(object):
    @classmethod
    def get_easy_mock(cls, country, program, project_name, check_req, return_req):
        meta_class = importlib.import_module('app.services.{0}.{1}.easy_mock'.format(country, program))
        return getattr(meta_class, country.title() + program.title().replace("_", "") + "EasyMock")(project_name,
                                                                                                    check_req,
                                                                                                    return_req)


class NacosFactory(object):

    @classmethod
    def get_nacos(cls, country, program, env):
        meta_class = importlib.import_module('app.services.{0}.{1}.nacos'.format(country, program))
        return getattr(meta_class, country.title() + program.title().replace("_", "") + "Nacos")(env)


class XxlJobFactory(object):

    @classmethod
    def get_xxljob(cls, country, program, env):
        meta_class = importlib.import_module('app.services.{0}.{1}.xxljob'.format(country, program))
        return getattr(meta_class, country.title() + program.title().replace("_", "") + "XxlJob")(env)


class AutoFactory(object):

    @classmethod
    def get_auto(cls, country, program, env, run_env):
        if country == 'china' and program == 'repay':
            return ChinaRepayService(env, run_env)


class RepayServiceFactory(object):
    @classmethod
    def get_repay(cls, country, env, environment, project_name):
        meta_class = importlib.import_module('app.services.{0}.repay.service'.format(country))
        return getattr(meta_class, country.title() + "RepayService")(env, environment, project_name)


class CleanServiceFactory(object):
    @classmethod
    def get_clean(cls, country, env, environment, project_name):
        meta_class = importlib.import_module('app.services.{0}.clean.service'.format(country))
        return getattr(meta_class, country.title() + "CleanService")(env, environment, project_name)


class BizCentralServiceFactory(object):
    @classmethod
    def get_biz_central(cls, country, env, environment, project_name):
        if country == 'china':
            return ChinaBizCentralService(env, environment, project_name)


class GrantServiceFactory(object):
    @classmethod
    def get_grant(cls, country, env, environment, project_name):
        meta_class = importlib.import_module('app.services.{0}.grant.service'.format(country))
        return getattr(meta_class, country.title() + "GrantService")(env, environment, project_name)
