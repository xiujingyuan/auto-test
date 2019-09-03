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

bind = '127.0.0.1:8166'
workers = multiprocessing.cpu_count() * 2 + 1

backlog = 2048
worker_class = "gevent"
worker_connections = 1000
daemon = True
debug = False
proc_name = 'gaea'
pidfile = '/logs/gunicorn.pid'
errorlog = '/logs/gunicorn.log'
