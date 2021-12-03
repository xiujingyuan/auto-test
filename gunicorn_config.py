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

bind = '127.0.0.1:6868'

workers = multiprocessing.cpu_count() * 2 + 1

threads = multiprocessing.cpu_count() * 2

backlog = 2048

worker_class = "gevent"

preload_app = True

worker_connections = 1000

debug = False

proc_name = 'auto_test'

pidfile = '/data/www/wwwroot/auto-test/gunicon/gunicorn.pid'

errorlog = '/data/www/wwwroot/auto-test/gunicon/gunicorn.log'

logfile = '/data/www/wwwroot/auto-test/gunicon/info.log'

accesslog = '/data/www/wwwroot/auto-test/gunicon/access.log'
