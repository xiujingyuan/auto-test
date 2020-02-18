#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
 @author: snow
 @software: PyCharm
 @time: 2018/12/18
 @file: config.py
 @site:
 @email:
"""
from environment.common.config import Config


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:Coh8Beyiusa7@127.0.0.1:3317/gaea_framework_test?charset=utf8'
    SENTRY_DSN = "https://c825ef551d3045029ceb90799f894286:5e5ed9ee34754bbebb1494cc79679e25@sentry.kuainiujinke.com/230"

    # celery 配置
    BROKER_URL = "redis://:123456@localhost:6379/6"
    CELERY_RESULT_BACKEND = "redis://:123456@localhost:6379/7"

    # Jenkins run case 配置
    JENKINS_RUN_JOB = "Auto_Test_Api_Run_Case_Debug"
