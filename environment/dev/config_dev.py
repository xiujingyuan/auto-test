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

