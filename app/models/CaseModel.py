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
from app.models.MockModel import MockModel
from app.models.InitModel import InitModel
from app.models.PrevModel import PrevModel



class Case(db.Model,Serializer):
    __tablename__ = 'finlab_cases'
    case_id= db.Column(db.Integer, primary_key=True)
    case_exec_priority=db.Column(db.Integer)
    case_from_system=db.Column(db.String(255))
    case_name=db.Column(db.String(255))
    case_description=db.Column(db.String(255))
    case_category=db.Column(db.String(255))
    case_executor=db.Column(db.String(255))
    case_exec_group=db.Column(db.String(255))
    case_exec_group_priority=db.Column(db.Integer)
    case_api_address=db.Column(db.String(255))
    case_api_method=db.Column(db.String(255))
    case_api_params=db.Column(db.String(255))
    case_api_header=db.Column(db.String(255))
    case_check_method=db.Column(db.String(255))
    case_except_value=db.Column(db.String)
    case_sql_actual_statement=db.Column(db.String)
    case_sql_actual_database=db.Column(db.String(255))
    case_sql_params=db.Column(db.String)
    case_sql_reference_name=db.Column(db.String(255))
    case_is_exec=db.Column(db.String(255))
    case_mock_flag=db.Column(db.Enum('Y','N'))
    case_next_msg=db.Column(db.String(255))
    case_next_task=db.Column(db.String(255))
    case_replace_expression=db.Column(db.String)
    case_init_id=db.Column(db.String(255))
    case_wait_time=db.Column(db.Integer)
    case_vars_name=db.Column(db.String(255))
    case_author=db.Column(db.String(255))
    case_in_date=db.Column(db.DateTime,default=datetime.now)
    case_in_user=db.Column(db.String(255))
    case_last_user=db.Column(db.String(255))
    case_last_date=db.Column(db.DateTime,default=datetime.now,onupdate=datetime.now)


    def __repr__(self):
        return '<finlab_cases %r>' % self.case_id

    @staticmethod
    def check_exists_bycaseid(caseid):
        try:
            result = False
            count = db.session.query(Case).filter(Case.case_id == caseid).count()
            if count==1:
                result = True
            return result
        except Exception as e:
            db.session.rollback()
        finally:
            db.session.commit()

    @staticmethod
    def add_case(case):
        try:
            db.session.add(case)
            db.session.flush()
            id = case.case_id
            return id
        except Exception as e :
            db.session.rollback()
        finally:
            db.session.commit()


    @staticmethod
    def change_case(data,caseid):
        try:
            db.session.query(Case).filter(Case.case_id == caseid).update(data)
        except Exception as e:
            db.session.rollback()
        finally:
            db.session.commit()

    @staticmethod
    def get_case_byid(caseid):
        try:
            result = db.session.query(Case).filter(Case.case_id==caseid).first()
            return result.serialize()
        except Exception as e:
            db.session.rollback()
        finally:
            db.session.commit()


    def serialize(self):
        return Serializer.serialize(self)
