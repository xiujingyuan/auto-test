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


class TestingConfig(Config):
    # TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:Coh8Beyiusa7@10.1.0.15:3306/gaea_framework?charset=utf8'
    WTF_CSRF_ENABLED = False
    SENTRY_DSN = "https://47a43c1e88cb4c4d8d193aac9dac05bc:9c326700cec14d32920e84b2b7ab4492@sentry.kuainiujinke.com/229"

    REDIS_HOST = "172.30.3.149"
    REDIS_PORT = "6379"
    REDIS_PWD = "kuainiujinke"

    # celery 配置
    BROKER_URL = "redis://:kuainiujinke@172.30.3.149:6379/6"
    CELERY_RESULT_BACKEND = "redis://:kuainiujinke@172.30.3.149:6379/7"

    # Jenkins run case 配置
    JENKINS_RUN_JOB = "Auto_Test_Api_Run_Case12"
