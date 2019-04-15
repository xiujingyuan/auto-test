# -*- coding: utf-8 -*-
# @Time    : 公元19-04-01 下午2:46
# @Author  : 张廷利
# @Site    : 
# @File    : KeyValueModel.py
# @Software: IntelliJ IDEA


from app import db
from datetime import datetime

from app.common.tools.Serializer import Serializer


class CommonToolsModel(db.Model,Serializer):
    __tablename__ = 'finlab_common_tools'
    id=db.Column(db.Integer,primary_key=True)
    title=db.Column(db.String)
    address=db.Column(db.String)
    method=db.Column(db.String)
    placeholder=db.Column(db.Text)
    description=db.Column(db.String)
    update_user=db.Column(db.String)
    create_user=db.Column(db.String)
    update_time=db.Column(db.DateTime)
    create_time=db.Column(db.DateTime)
    def __repr__(self):
        return '<finlab_common_tools %r>' % self.keyvalue_id

    def serialize(self):
        return Serializer.serialize(self)
