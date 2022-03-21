#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
 @author: snow
 @software: PyCharm  
 @time: 2018/12/18
 @file: __init__.py.py
 @site:
 @email:
"""

from flask import Blueprint

auth = Blueprint('auth', __name__)

from . import forms, views