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

import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
    WTF_CSRF_SECRET_KEY = "my csrf key is easy"
    SSL_DISABLE = False
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True
    MAIL_SERVER = 'smtp.qq.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = "625046831@qq.com"
    MAIL_PASSWORD = "vdpritgxwgcnbajd"

    JC_MOCK_MAIL_SUBJECT_PREFIX = '[Jc-Mock]'
    JC_MOCK_MAIL_SENDER = MAIL_USERNAME
    JC_MOCK_ADMIN = os.environ.get('Jc-Mock_ADMIN')
    JC_MOCK_POSTS_PER_PAGE = 20
    JC_MOCK_FOLLOWERS_PER_PAGE = 50
    JC_MOCK_COMMENTS_PER_PAGE = 30
    JC_MOCK_SLOW_DB_QUERY_TIME = 0.5
    ENCRY_URL ='http://test-encryptor.qianshengqian.com/encrypt/'
    DEENCRY_URL = 'http://test-encryptor.qianshengqian.com/decrypt/plain/'
    @staticmethod
    def init_app(app):
        pass
