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

    @staticmethod
    def check_exists_bycaseid(caseid):
        count = db.session.query(MockModel).filter(MockModel.mock_case_id == caseid).count()
        if count>0:
            return True
        else:
            return False

    @staticmethod
    def check_exists_bymockid(mockid):
        count = db.session.query(MockModel).filter(MockModel.mock_id == mockid).count()
        if count==1:
            return True
        else:
            return False

    @staticmethod
    def get_mock_byid(caseid):

        result = db.session.query(MockModel).filter(MockModel.mock_case_id==caseid).all()
        return Serializer.serialize_list(result)


    @staticmethod
    def add_mock(mock):
        try:
            db.session.add(mock)
            db.session.flush()
            id = mock.mock_id
            return id
        except Exception as e :
            db.session.rollback()
        finally:
            db.session.commit()


    @staticmethod
    def change_mock(data,mock_id):
        try:
            db.session.query(MockModel).filter(MockModel.mock_id == mock_id).update(data)
        except Exception as e:
            db.session.rollback()
        finally:
            db.session.commit()


    def serialize(self):
        return Serializer.serialize(self)
