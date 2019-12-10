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


bind = '127.0.0.1:8166'

workers = multiprocessing.cpu_count() * 2 + 1

threads = multiprocessing.cpu_count() * 2

backlog = 2048

worker_class = "gevent"

preload_app = True

worker_connections = 1000

debug = False

proc_name = 'gaea'

pidfile = 'logs/gunicorn.pid'

errorlog = 'logs/gunicorn.log'

logfile = 'logs/info.log'

accesslog = 'logs/access.log'
