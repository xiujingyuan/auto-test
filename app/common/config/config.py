#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
 @author: snow
 @software: PyCharm  
 @time: 2018/12/18
 @file: config.py
 @site:
 @email:
"""
from environment.dev.config_dev import DevelopmentConfig
from environment.prod.config_prod import ProductionConfig
from environment.test.config_test import TestingConfig

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': ProductionConfig
}


variable_database_list=[
    "gbiz1",
    "gbiz2",
    "gbiz1",
    "gbiz2",
    "gbiz1",
    "gbiz2",
    "gbiz1",
    "gbiz2"
]