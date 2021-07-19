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

from resource.config import AutoTestConfig

db = SQLAlchemy(session_options={"autocommit": True})


def create_app():
    app = Flask(__name__)
    # 导致指定的配置对象
    app.config.from_object(AutoTestConfig)
    # 调用config.py的init_app()
    AutoTestConfig.init_app(app)
    db.init_app(app, )

    from app.api.nacos import api_nacos as api_nacos_blueprint
    app.register_blueprint(api_nacos_blueprint, url_prefix='/api/nacos/')

    from app.api.xxljob import api_xxljob as api_xxljob_blueprint
    app.register_blueprint(api_xxljob_blueprint, url_prefix='/api/xxljob/')

    from app.api.easymock import api_easy_mock as api_easy_mock_blueprint
    app.register_blueprint(api_easy_mock_blueprint, url_prefix='/api/easy_mock/')

    from app.api.database import api_data_base as api_data_base_blueprint
    app.register_blueprint(api_data_base_blueprint, url_prefix='/api/data_base/')

    return app
