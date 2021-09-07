# coding: utf-8
from app import db


class MockConfig(db.Model):
    __tablename__ = 'mock_config'

    mock_config_id = db.Column(db.Integer, primary_key=True, info='自增长')
    mock_config_desc = db.Column(db.String(100), nullable=False, server_default=db.FetchedValue(), info='mock描述')
    mock_config_key = db.Column(db.String(20), nullable=False, server_default=db.FetchedValue(), info='mock关键字描述')
    mock_config_name = db.Column(db.String(20), nullable=False, server_default=db.FetchedValue(), info='mock的配置文件名称')
    mock_config_program = db.Column(db.String(20), nullable=False, server_default=db.FetchedValue(), info='所属系统')
    mock_config_value = db.Column(db.String(500), nullable=False, server_default=db.FetchedValue(), info='需要替换值的描述')
    mock_config_order = db.Column(db.Integer, server_default=db.FetchedValue(), info='mock显示顺序')
    mock_config_is_collect = db.Column(db.Integer, server_default=db.FetchedValue(), info='mock是否喜爱')
    mock_config_is_active = db.Column(db.Integer, server_default=db.FetchedValue(), info='mock是否激活')
    mock_config_timeout = db.Column(db.Integer, nullable=False, info='替换超时时间')
    mock_config_creater = db.Column(db.String(8), nullable=False, server_default=db.FetchedValue(), info='mock创建人')
    mock_config_updater = db.Column(db.String(8), nullable=False, server_default=db.FetchedValue(), info='mock最后更新人')
    mock_config_create_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='mock创建时间')
    mock_config_update_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='mock更新时间')
