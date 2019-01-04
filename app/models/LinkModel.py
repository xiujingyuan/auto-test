#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
 @author: snow
 @software: PyCharm
 @time: 2018/12/27
 @file: LinkModel.py
 @site:
 @email:
"""
from app import db
from datetime import datetime


class Link(db.Model):
    __tablename__ = 'links'
    link_id = db.Column(db.Integer, primary_key=True)
    link_title = db.Column(db.String(255))
    link_url = db.Column(db.String(255))
    link_user = db.Column(db.String(255))
    link_pwd = db.Column(db.String(255))
    link_type = db.Column(db.Integer, db.ForeignKey('link_types.link_type_id'))
    link_create_at = db.Column(db.DateTime, default=datetime.now)
    link_update_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    def __repr__(self):
        return '<Link %r>' % self.link_id
