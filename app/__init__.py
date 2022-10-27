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
    app.global_data = {}

    from app.api.nacos import api_nacos as api_nacos_blueprint
    app.register_blueprint(api_nacos_blueprint, url_prefix='/api/nacos/')

    from app.api.xxljob import api_xxljob as api_xxljob_blueprint
    app.register_blueprint(api_xxljob_blueprint, url_prefix='/api/xxljob/')

    from app.api.easymock import api_easy_mock as api_easy_mock_blueprint
    app.register_blueprint(api_easy_mock_blueprint, url_prefix='/api/easy_mock/')

    from app.api.biz_central import api_biz_central as api_biz_central_blueprint
    app.register_blueprint(api_biz_central_blueprint, url_prefix='/api/biz_central/')

    from app.api.repay import api_repay as api_repay_blueprint
    app.register_blueprint(api_repay_blueprint, url_prefix='/api/repay/')

    from app.api.grant import api_grant as api_grant_blueprint
    app.register_blueprint(api_grant_blueprint, url_prefix='/api/grant/')

    from app.api.clean import api_clean as api_clean_blueprint
    app.register_blueprint(api_clean_blueprint, url_prefix='/api/clean/')

    from app.api.test_case import api_test_case as api_test_case_blueprint
    app.register_blueprint(api_test_case_blueprint, url_prefix='/api/test_case/')

    from app.api.web import api_web as api_web_blueprint
    app.register_blueprint(api_web_blueprint, url_prefix='/api/backend/')

    return app
