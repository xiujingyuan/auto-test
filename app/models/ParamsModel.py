# -*- coding: utf-8 -*-
# @Title: CaseModel
# @ProjectName gaea-api
# @Description: TODO
# @author fyi zhang
# @date 2019/1/5 0:46

from app import db
from datetime import datetime
from app.common.tools.Serializer import Serializer


class ParamsModel(db.Model,Serializer):
    __tablename__ = 'finlab_system_params'
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(255))
    type= db.Column(db.String(255))
    value= db.Column(db.String(512))
    action= db.Column(db.String(255))
    status =db.Column(db.Enum('Y','N'))
    indate=db.Column(db.DateTime,default=datetime.now())
    inuser = db.Column(db.String(255))
    lastuser= db.Column(db.String(255))
    lastdate=db.Column(db.DateTime,default=datetime.now(),onupdate=datetime.now())


    def __repr__(self):
        return '<finlab_system_params %r>' % self.id




    def serialize(self):
        return Serializer.serialize(self)
