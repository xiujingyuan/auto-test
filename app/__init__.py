#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
 @author: snow
 @software: PyCharm
 @time: 2019/01/03
 @file: __init__.py.py
 @site:
 @email:
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.common.config.config import config
from flask_wtf.csrf import CSRFProtect
from celery import Celery
from redis import Redis

db = SQLAlchemy()
csrf = CSRFProtect()

celery = Celery(__name__)


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    celery.conf.update(app.config)
    app.app_redis = Redis(host=app.config['REDIS_HOST'],
                          port=app.config['REDIS_PORT'],
                          db=5,
                          password=app.config['REDIS_PWD'])
    #csrf.init_app(app)

    db.init_app(app)

    from app.api.v1 import api_v1 as api_v1_blueprint
    app.register_blueprint(api_v1_blueprint)

    from app.tasks import task_url as tasks_blueprint
    app.register_blueprint(tasks_blueprint, url="/tasks")

    return app
