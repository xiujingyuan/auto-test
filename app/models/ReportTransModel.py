# -*- coding: utf-8 -*-
# @Time    : 2019/5/16 15:56
# @Author  : 张廷利
# @Site    : 
# @File    : ReportModel.py
# @Software: IntelliJ IDEA

import time

from app import db
from datetime import datetime
from app.common.tools.Serializer import Serializer



class ReportTransModel(db.Model,Serializer):
    __tablename__ = 'finlab_report_transaction'
    finlab_report_transaction_id= db.Column(db.Integer, primary_key=True)
    finlab_report_transaction_report_id=db.Column(db.Integer)
    finlab_report_transaction_type=db.Column(db.String(20))
    finlab_report_transaction_rate=db.Column(db.String(45))
    finlab_report_transaction_content=db.Column(db.TEXT)
    finlab_report_transaction_image_url=db.Column(db.String(500))
    finlab_report_transaction_link_url=db.Column(db.String(500))
    finlab_report_transaction_inuser=db.Column(db.String(20))
    finlab_report_transaction_indate=db.Column(db.DateTime,default=datetime.now,onupdate=datetime.now)


    def __repr__(self):
        return '<finlab_report_transaction %r>' % self.finlab_report_transaction_id


    def serialize(self):
        return Serializer.serialize(self)
