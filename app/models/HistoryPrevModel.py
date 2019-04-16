# -*- coding: utf-8 -*-
# @Title: CaseModel
# @ProjectName gaea-api
# @Description: TODO
# @author fyi zhang
# @date 2019/1/5 0:46

from app import db
from datetime import datetime
from app.common.tools.Serializer import Serializer


class HistoryPrevModel(db.Model,Serializer):
    __tablename__ = 'history_prev_condition'
    history_id = db.Column(db.Integer,primary_key=True)
    run_id = db.Column(db.Integer,db.ForeignKey("history_finlab_cases.run_id"))
    prev_id = db.Column(db.Integer)
    prev_case_id=db.Column(db.Integer,db.ForeignKey("history_finlab_cases.history_case_id"))
    prev_task_type=db.Column(db.String(255))
    prev_name=db.Column(db.String(255))
    prev_description=db.Column(db.String(255))
    prev_flag=db.Column(db.String(255))
    prev_setup_type=db.Column(db.String(255))
    prev_api_address=db.Column(db.String(255))
    prev_api_method=db.Column(db.String(255))
    prev_api_params=db.Column(db.Text)
    prev_api_header=db.Column(db.String(255))
    prev_api_expression=db.Column(db.Text)
    prev_sql_statement=db.Column(db.Text)
    prev_sql_params=db.Column(db.Text)
    prev_sql_database=db.Column(db.String(255))
    prev_sql_expression=db.Column(db.Text)
    prev_expression=db.Column(db.Text)
    prev_params=db.Column(db.Text)
    prev_except_expression=db.Column(db.Text)
    prev_except_value=db.Column(db.Text)
    prev_priority=db.Column(db.Integer)
    prev_wait_time=db.Column(db.Integer)
    prev_in_user=db.Column(db.String(255))
    prev_last_user=db.Column(db.String(255))
    prev_in_date=db.Column(db.DateTime,default=datetime.now())
    prev_last_date=db.Column(db.DateTime,default=datetime.now(),onupdate=datetime.now())


    def __repr__(self):
        return '<finlab_cases %r>' % self.history_id

    def serialize(self):
        return Serializer.serialize(self)