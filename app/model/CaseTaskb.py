# coding: utf-8
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()



class CaseTask(db.Model):
    __tablename__ = 'case_task'

    case_task_id = db.Column(db.Integer, primary_key=True, info='自增ID')
    case_task_name = db.Column(db.String(256), info='任务名称')
    case_task_creator = db.Column(db.String(11), info='创建者')
    case_task_updatoer = db.Column(db.String(11), info='最后更新人')
    case_task_execute_time = db.Column(db.String(20), info='执行时间')
    case_task_create_at = db.Column(db.DateTime, info='创建时间')
    case_task_update_at = db.Column(db.DateTime, info='更新时间')
    case_task_country = db.Column(db.String(10), info='国家')
    case_task_program = db.Column(db.String(10), info='系统')
    case_task_type = db.Column(db.String(1), info='任务类型，0:具体时间；1:cron')
