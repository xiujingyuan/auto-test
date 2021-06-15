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

gevent.monkey.patch_all()

bind = '127.0.0.1:8233'

workers = multiprocessing.cpu_count() * 2 + 1

threads = multiprocessing.cpu_count() * 2

backlog = 2048

worker_class = "gevent"

preload_app = True

worker_connections = 1000

debug = False

proc_name = 'gaea'

pidfile = '/data1/auto-test/gunicon/logs/gunicorn.pid'

errorlog = '/data1/auto-test/gunicon/logs/gunicorn.log'

logfile = '/data1/auto-test/gunicon/logs/info.log'

accesslog = '/data1/auto-test/gunicon/logs/access.log'
