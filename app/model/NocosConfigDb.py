# coding: utf-8
from app import db


class NacosConfig(db.Model):
    __tablename__ = 'nacos_config'

    nacos_config_id = db.Column(db.Integer, primary_key=True, info='自增长')
    nacos_config_desc = db.Column(db.String(100), nullable=False, server_default=db.FetchedValue(), info='nacos描述')
    nacos_config_key = db.Column(db.String(20), nullable=False, server_default=db.FetchedValue(), info='nacos关键字描述')
    nacos_config_name = db.Column(db.String(20), nullable=False, server_default=db.FetchedValue(), info='nacos的配置文件名称')
    nacos_config_program = db.Column(db.String(20), nullable=False, server_default=db.FetchedValue(), info='所属系统')
    nacos_config_value = db.Column(db.String(500), nullable=False, server_default=db.FetchedValue(), info='需要替换值的描述')
    nacos_config_order = db.Column(db.Integer, server_default=db.FetchedValue(), info='nacos显示顺序')
    nacos_config_is_collect = db.Column(db.Integer, server_default=db.FetchedValue(), info='nacos是否喜爱')
    nacos_config_is_active = db.Column(db.Integer, server_default=db.FetchedValue(), info='nacos是否激活')
    nacos_config_timeout = db.Column(db.Integer, nullable=False, info='替换超时时间')
    nacos_config_creater = db.Column(db.String(8), nullable=False, server_default=db.FetchedValue(), info='nacos创建人')
    nacos_config_updater = db.Column(db.String(8), nullable=False, server_default=db.FetchedValue(), info='nacos最后更新人')
    nacos_config_create_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='nacos创建时间')
    nacos_config_update_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='nacos更新时间')