#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
 @author: snow
 @software: PyCharm
 @time: 2019/09/03
 @file: gunicorn_config.py
 @site:
 @email:
"""
import multiprocessing
import gevent.monkey
import os
basedir = os.path.abspath(os.path.dirname(__file__))

gevent.monkey.patch_all()

bind = '127.0.0.1:6868'

workers = 1

threads = 1

backlog = 2048

worker_class = "gevent"

preload_app = True

worker_connections = 1000

debug = False

proc_name = 'auto_test'

pidfile = os.path.join(basedir, 'logs/gunicon/gunicorn.pid')
errorlog = os.path.join(basedir, 'logs/gunicon/gunicorn.log')
logfile = os.path.join(basedir, 'logs/gunicon/info.log')
accesslog = os.path.join(basedir, 'logs/gunicon/access.log')


