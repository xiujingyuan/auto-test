# coding: utf-8
from app import db
from app.common.tools.Serializer import Serializer
from datetime import datetime


class RunCase(db.Model, Serializer):
    __tablename__ = 'run_cases'

    run_id = db.Column(db.Integer, primary_key=True)
    run_from_system = db.Column(db.String(100), nullable=False, server_default=db.FetchedValue())
    run_status = db.Column(db.Integer, nullable=False)
    run_report = db.Column(db.String(255), nullable=False, server_default=db.FetchedValue())
    run_case_count = db.Column(db.Integer, server_default=db.FetchedValue())
    run_success = db.Column(db.Integer, server_default=db.FetchedValue())
    run_fail = db.Column(db.Integer, server_default=db.FetchedValue())
    run_skip = db.Column(db.Integer, server_default=db.FetchedValue())
    run_success_rate = db.Column(db.Float, server_default=db.FetchedValue())
    run_durations = db.Column(db.Integer, server_default=db.FetchedValue())
    run_created_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), default=datetime.now, onupdate=datetime.now)

    def __repr__(self):
        return '<run_cases %r>' % self.case_id

    def serialize(self):
        return Serializer.serialize(self)
