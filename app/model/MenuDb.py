# coding: utf-8
from app import db
from app.common.db_util import BaseToDict


class Menu(db.Model, BaseToDict):
    __tablename__ = 'menu'

    menu_id = db.Column(db.Integer, primary_key=True)
    menu_create_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='创建时间')
    menu_update_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='更新时间')
    menu_icon = db.Column(db.String(30), nullable=False, server_default=db.FetchedValue(), info='图标')
    menu_title = db.Column(db.String(10), nullable=False, server_default=db.FetchedValue(), info='菜单名字')
    menu_index = db.Column(db.String(50), nullable=False, server_default=db.FetchedValue(), info='菜单地址')
    menu_active = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), info='是否激活菜单')
    menu_order = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), info='菜单顺序')
    menu_parent_id = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), info='父菜单menu_id')
