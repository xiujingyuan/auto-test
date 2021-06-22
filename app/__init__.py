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

db = SQLAlchemy(session_options={"autocommit": True})


def create_app():
    app = Flask(__name__)
    db.init_app(app, )

    from app.api.nacos import api_nacos as api_nacos_blueprint
    app.register_blueprint(api_nacos_blueprint, url_prefix='/api/nacos/')

    return app
