# -*- coding: utf-8 -*-
# @Time    : 公元19-04-01 下午2:46
# @Author  : 张廷利
# @Site    : 
# @File    : KeyValueModel.py
# @Software: IntelliJ IDEA


from app import db
from datetime import datetime

from app.common.tools.Serializer import Serializer


class KeyvalueModel(db.Model):
    __tablename__ = 'keyvalue'
    __table_args__={'schema':'db_test'}
    keyvalue_id=db.Column(db.Integer,primary_key=True)
    keyvalue_key=db.Column(db.String)
    keyvalue_value=db.Column(db.Text)
    keyvalue_memo=db.Column(db.Text)
    keyvalue_status=db.Column(db.Enum('active','inactive'))
    keyvalue_create_user=db.Column(db.Integer)
    keyvalue_update_user=db.Column(db.Integer)
    keyvalue_create_at=db.Column(db.DateTime)
    keyvalue_update_at=db.Column(db.DateTime)
    def __repr__(self):
        return '<keyvalue %r>' % self.keyvalue_id

    def serialize(self):
        return Serializer.serialize(self)
