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



class ReportModel(db.Model,Serializer):
    __tablename__ = 'finlab_report'
    finlab_report_id= db.Column(db.Integer, primary_key=True)
    finlab_report_description=db.Column(db.String(5000))
    finlab_report_branch_name=db.Column(db.String(500))
    finlab_report_build_number=db.Column(db.INTEGER)
    finlab_report_summary=db.Column(db.String(2000))
    finlab_report_content=db.Column(db.TEXT)
    finlab_report_tester=db.Column(db.String(50))
    finlab_report_total_bug=db.Column(db.INTEGER)
    finlab_report_close_bug=db.Column(db.INTEGER)
    finlab_report_serious_bug=db.Column(db.INTEGER)
    finlab_report_diff_cover=db.Column(db.String(20))
    finlab_report_auto_rate=db.Column(db.String(20))
    finlab_report_snor_rate=db.Column(db.String(20))
    finlab_report_ref_requirement=db.Column(db.String(500))
    finlab_report_case_address=db.Column(db.String(500))
    finlab_report_productor=db.Column(db.String(50))
    finlab_report_begin=db.Column(db.DateTime)
    finlab_report_end=db.Column(db.DateTime)
    finlab_report_notify_address=db.Column(db.String(1000))
    finlab_report_inuser=db.Column(db.String(255))
    finlab_report_indate=db.Column(db.DateTime,default=datetime.now,onupdate=datetime.now)


    def __repr__(self):
        return '<finlab_report %r>' % self.finlab_report_id


    def serialize(self):
        return Serializer.serialize(self)
