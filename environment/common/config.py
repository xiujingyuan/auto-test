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

import os, logging
basedir = os.path.abspath(os.path.dirname(__file__))
from kombu import Exchange, Queue


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
    WTF_CSRF_SECRET_KEY = "my csrf key is easy"
    SSL_DISABLE = False
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True
    SQLALCHEMY_ECHO = True
    SQLALCHEMY_POOL_RECYCLE = 1800
    MAIL_SERVER = 'smtp.qq.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = "625046831@qq.com"
    MAIL_PASSWORD = "vdpritgxwgcnbajd"
    # ENCRY_URL ='http://test-encryptor.qianshengqian.com/encrypt/'
    # DEENCRY_URL = 'http://test-encryptor.qianshengqian.com/decrypt/plain/'

    ENCRY_URL = 'http://kong-api-test.kuainiujinke.com/encryptor-test/encrypt/'
    DEENCRY_URL = 'http://kong-api-test.kuainiujinke.com/encryptor-test/decrypt/plain/'
    CMDB_URL = "http://kong-api-test.kuainiujinke.com/cmdb1/v5/rate/calculate"
    # v6费率系统
    CMDB_URL_v6 = "http://kong-api-test.kuainiujinke.com/cmdb2/v6/rate/repay/calculate"
    SYNC_ENV_LIST = ['biz1', 'biz2']

    JC_MOCK_MAIL_SUBJECT_PREFIX = '[Jc-Mock]'
    JC_MOCK_MAIL_SENDER = MAIL_USERNAME
    JC_MOCK_ADMIN = os.environ.get('Jc-Mock_ADMIN')
    JC_MOCK_POSTS_PER_PAGE = 20
    JC_MOCK_FOLLOWERS_PER_PAGE = 50
    JC_MOCK_COMMENTS_PER_PAGE = 30
    JC_MOCK_SLOW_DB_QUERY_TIME = 0.5

    log_base_dir = os.path.dirname(basedir)
    log_base_dir = os.path.dirname(log_base_dir)
    LOG_PATH = os.path.join(log_base_dir, 'logs')
    LOG_PATH_ERROR = os.path.join(LOG_PATH, 'error.log')
    LOG_PATH_INFO = os.path.join(LOG_PATH, 'info.log')
    LOG_FILE_MAX_BYTES = 100 * 1024 * 1024
    # 轮转数量是 10 个
    LOG_FILE_BACKUP_COUNT = 10
    SENTRY_DSN = ""

    JENKINS_URL = "https://jenkins-test.kuainiujinke.com/jenkins/"
    USER_ID = "yangxuechao"
    USER_PWD = "11dcb4f46441f9ca3cafb7f239ecb06e26"

    REDIS_HOST = "127.0.0.1"
    REDIS_PORT = "6379"
    REDIS_PWD = "123456"

    CELERY_TIMEZONE = 'Asia/Shanghai'

    CELERY_QUEUES = (
        Queue("default", Exchange("default"), routing_key="default"),
        Queue("app.tasks.case.case_task.run_case_by_case_id", Exchange("for_run_case_task"),
              routing_key="for_run_case_task"),
    )
    # celery路由
    CELERY_ROUTES = {
        'app.tasks.case.case_task.run_case_by_case_id': {"queue": "for_run_case_task",
                                                         "routing_key": "for_run_case_task"},
    }

    @staticmethod
    def init_app(app):
        import logging
        from logging.handlers import RotatingFileHandler
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s %(levelname)s %(process)d %(thread)d '
            '%(pathname)s %(lineno)s %(message)s')


        # FileHandler Info
        file_handler_info = RotatingFileHandler(filename=Config.LOG_PATH_INFO)
        file_handler_info.setFormatter(formatter)
        file_handler_info.setLevel(logging.INFO)
        info_filter = InfoFilter()
        file_handler_info.addFilter(info_filter)
        app.logger.addHandler(file_handler_info)

        # FileHandler Error
        file_handler_error = RotatingFileHandler(filename=Config.LOG_PATH_ERROR)
        file_handler_error.setFormatter(formatter)
        file_handler_error.setLevel(logging.ERROR)
        app.logger.addHandler(file_handler_error)


class InfoFilter(logging.Filter):
    def filter(self, record):
        """only use INFO
        筛选, 只需要 INFO 级别的log
        :param record:
        :return:
        """
        if logging.INFO <= record.levelno < logging.ERROR:
            # 已经是INFO级别了
            # 然后利用父类, 返回 1
            return super().filter(record)
        else:
            return 0
