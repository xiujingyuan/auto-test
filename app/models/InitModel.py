# -*- coding: utf-8 -*-
# @Title: CaseModel
# @ProjectName gaea-api
# @Description: TODO
# @author fyi zhang
# @date 2019/1/5 0:46

from app import db
from datetime import datetime
from app.common.tools.Serializer import Serializer


class InitModel(db.Model,Serializer):
    __tablename__ = 'finlab_cases_init'
    case_init_id = db.Column(db.Integer,primary_key=True)
    case_init_case_id = db.Column(db.Integer,db.ForeignKey("finlab_cases.case_id"))
    case_init_type = db.Column(db.String(255))
    case_init_name= db.Column(db.String(255))
    case_init_description= db.Column(db.String(255))
    case_init_api_address= db.Column(db.String(255))
    case_init_api_method= db.Column(db.String(255))
    case_init_api_params= db.Column(db.String(255))
    case_init_api_header= db.Column(db.String(255))
    case_init_api_expression= db.Column(db.Text)
    case_init_sql= db.Column(db.Text)
    case_init_sql_params= db.Column(db.Text)
    case_init_sql_expression= db.Column(db.Text)
    case_init_sql_database= db.Column(db.String(255))
    case_init_indate=db.Column(db.DateTime,default=datetime.now())
    case_init_inuser = db.Column(db.String(255))
    case_init_lastuser= db.Column(db.String(255))
    case_init_lastdate=db.Column(db.DateTime,default=datetime.now(),onupdate=datetime.now())


    def __repr__(self):
        return '<finlab_cases %r>' % self.case_id

    @staticmethod
    def check_exists_byinitid(initid):
        try:
            count = db.session.query(InitModel).filter(InitModel.case_init_id == initid).count()
            if count==1:
                return True
            else:
                return False
        except Exception as e:
            db.session.rollback()
        finally:
            db.session.commit()


    @staticmethod
    def check_exists_bycaseid(caseid):
        try:
            count = db.session.query(InitModel).filter(InitModel.case_init_case_id == caseid).count()
            if count>0:
                return True
            else:
                return False
        except Exception as e:
            db.session.rollback()
        finally:
            db.session.commit()

    @staticmethod
    def get_init_byid(caseid):
        try:
            result = db.session.query(InitModel).filter(InitModel.case_init_case_id==caseid).all()
            return Serializer.serialize_list(result)
        except Exception as e:
            db.session.rollback()
        finally:
            db.session.commit()

    @staticmethod
    def add_init(init):
        try:
            db.session.add(init)
            db.session.flush()
            id = init.case_init_id
            return id
        except Exception as e :
            db.session.rollback()
        finally:
            db.session.commit()


    @staticmethod
    def change_init(data,init_id):
        try:
            db.session.query(InitModel).filter(InitModel.case_init_id == init_id).update(data)
        except Exception as e:
            db.session.rollback()
        finally:
            db.session.commit()


    def serialize(self):
        return Serializer.serialize(self)
