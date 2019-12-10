# -*- coding: utf-8 -*-
# @Title: CaseModel
# @ProjectName gaea-api
# @Description: TODO
# @author fyi zhang
# @date 2019/1/5 0:46
import time

from app import db
from datetime import datetime
from app.common.tools.Serializer import Serializer
from app.models.HistoryPrevModel import HistoryPrevModel
from app.models.HistoryInitModel import HistoryInitModel



class HistoryCaseModel(db.Model,Serializer):
    __tablename__ = 'history_finlab_cases'
    history_id = db.Column(db.Integer,primary_key=True)
    run_id = db.Column(db.Integer)
    build_id = db.Column(db.String(255))
    history_case_belong_business = db.Column(db.String(255))
    history_case_id= db.Column(db.Integer)
    history_case_exec_priority=db.Column(db.Integer)
    history_case_from_system=db.Column(db.String(255))
    history_case_name=db.Column(db.String(255))
    history_case_description=db.Column(db.String(255))
    history_case_category=db.Column(db.String(255))
    history_case_executor=db.Column(db.String(255))
    history_case_exec_group=db.Column(db.String(255))
    history_case_exec_group_priority=db.Column(db.Integer)
    history_case_api_address=db.Column(db.String(255))
    history_case_api_method=db.Column(db.String(255))
    history_case_api_params=db.Column(db.String(255))
    history_case_api_header=db.Column(db.String(255))
    history_case_check_method=db.Column(db.String(255))
    history_case_except_value=db.Column(db.String)
    history_case_vars =db.Column(db.String)
    history_case_result=db.Column(db.Integer)
    history_case_actual_value=db.Column(db.String)
    history_case_sql_actual_statement=db.Column(db.String)
    history_case_sql_actual_database=db.Column(db.String(255))
    history_case_sql_params=db.Column(db.String)
    history_case_ref_tapd_id=db.Column(db.String(255))
    history_case_is_exec=db.Column(db.String(255))
    history_case_mock_flag=db.Column(db.Enum('Y','N'))
    history_case_next_msg=db.Column(db.String(255))
    history_case_next_task=db.Column(db.String(255))
    history_case_replace_expression=db.Column(db.String)
    history_case_init_id=db.Column(db.String(255))
    history_case_wait_time=db.Column(db.Integer)
    history_case_vars_name=db.Column(db.String(255))
    history_case_author=db.Column(db.String(255))
    history_case_in_date=db.Column(db.DateTime,default=datetime.now)
    history_case_in_user=db.Column(db.String(255))
    history_case_last_user=db.Column(db.String(255))
    history_case_last_date=db.Column(db.DateTime,default=datetime.now,onupdate=datetime.now)
    history_case_result_info = db.Column(db.Text)
    history_case_exec_count = db.Column(db.Integer, default=1)
    action = db.Column(db.Text)
    history_case_exec_index = db.Column(db.Integer, default=1)
    history_main_case_exec_index = db.Column(db.Integer, default=1)

    def __repr__(self):
        return '<finlab_cases %r>' % self.history_id


    def serialize(self):
        return Serializer.serialize(self)
