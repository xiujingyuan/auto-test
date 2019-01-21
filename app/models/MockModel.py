# -*- coding: utf-8 -*-
# @Title: CaseModel
# @ProjectName gaea-api
# @Description: TODO
# @author fyi zhang
# @date 2019/1/5 0:46

from app import db
from datetime import datetime
from app.common.tools.Serializer import Serializer


class MockModel(db.Model,Serializer):
    __tablename__ = 'finlab_cases_api_mock'
    mock_id=db.Column(db.Integer,primary_key=True)
    mock_case_id=db.Column(db.Integer,db.ForeignKey("finlab_cases.case_id"))
    mock_case_step_id=db.Column(db.Integer)
    mock_name=db.Column(db.String(255))
    mock_api_path=db.Column(db.String(255))
    mock_response=db.Column(db.Text)
    mock_expression=db.Column(db.Text)
    mock_status=db.Column(db.String(255))
    mock_memo=db.Column(db.String(255))
    mock_create_at=db.Column(db.DateTime,default=datetime.now())
    mock_create_user=db.Column(db.String(255))
    mock_update_at=db.Column(db.DateTime,default=datetime.now(),onupdate=datetime.now())
    mock_update_user=db.Column(db.String(255))
    def __repr__(self):
        return '<finlab_cases %r>' % self.case_id

    def serialize(self):
        return Serializer.serialize(self)
