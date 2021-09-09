# coding: utf-8
from app import db
from app.common.db_util import BaseToDict


class AutoAsset(db.Model, BaseToDict):
    __tablename__ = 'asset'

    asset_id = db.Column(db.Integer, primary_key=True, info='创建资产的ID')
    asset_name = db.Column(db.String(30), info='资产编号')
    asset_period = db.Column(db.String(2), info='资产期次')
    asset_channel = db.Column(db.String(50), info='放款通道')
    asset_env = db.Column(db.String(10), nullable=False, server_default=db.FetchedValue(), info='所属环境')
    asset_descript = db.Column(db.String(50), info='资产描述')
    asset_create_owner = db.Column(db.String(11), nullable=False, server_default=db.FetchedValue(), info='资产创建人')
    asset_create_at = db.Column(db.Date, nullable=False, info='资产创建时间')
    asset_update_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='资产更新时间')
    asset_type = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), info='0:本地，1:前端联测，2:资方联测')
    asset_source_type = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), info='0:自动放款，1:手动添加')
