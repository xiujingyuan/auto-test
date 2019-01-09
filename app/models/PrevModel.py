# -*- coding: utf-8 -*-
# @Title: CaseModel
# @ProjectName gaea-api
# @Description: TODO
# @author fyi zhang
# @date 2019/1/5 0:46

from app import db
from datetime import datetime
from app.common.tools.Serializer import Serializer


class PrevModel(db.Model,Serializer):
    __tablename__ = 'finlab_case_prev_condition'
    prev_id = db.Column(db.Integer,primary_key=True)
    prev_case_id=db.Column(db.Integer,db.ForeignKey("finlab_cases.case_id"))
    prev_task_type=db.Column(db.String(255))
    prev_name=db.Column(db.String(255))
    prev_description=db.Column(db.String(255))
    prev_flag=db.Column(db.String(255))
    prev_inner_flag=db.Column(db.String(255))
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
    prev_in_user=db.Column(db.String(255))
    prev_last_user=db.Column(db.String(255))
    prev_in_date=db.Column(db.DateTime,default=datetime.now())
    prev_last_date=db.Column(db.DateTime,default=datetime.now(),onupdate=datetime.now())

    def __repr__(self):
        return '<finlab_cases %r>' % self.case_id

    @staticmethod
    def check_exists_bycaseid(caseid):
        count = db.session.query(PrevModel).filter(PrevModel.prev_case_id == caseid).count()
        if count>0:
            return True
        else:
            return False

    @staticmethod
    def check_exists_byprevid(prev_id):
        count = db.session.query(PrevModel).filter(PrevModel.prev_id == prev_id).count()
        if count==1:
            return True
        else:
            return False

    @staticmethod
    def get_prev_byid(caseid):
        result = db.session.query(PrevModel).filter(PrevModel.prev_case_id==caseid).all()
        return Serializer.serialize_list(result)


    @staticmethod
    def add_prev(prev):
        try:
            db.session.add(prev)
            db.session.flush()
            id = prev.prev_id
            return id
        except Exception as e :
            db.session.rollback()
        finally:
            db.session.commit()


    @staticmethod
    def change_prev(data,prev_id):
        try:
            db.session.query(PrevModel).filter(PrevModel.prev_id == prev_id).update(data)
        except Exception as e:
            db.session.rollback()
        finally:
            db.session.commit()

    def serialize(self):
        return Serializer.serialize(self)