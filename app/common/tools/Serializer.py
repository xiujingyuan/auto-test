# -*- coding: utf-8 -*-
# @Title: Serializer
# @ProjectName gaea-api
# @Description: TODO
# @author fyi zhang
# @date 2019/1/6 15:53

from sqlalchemy.inspection import inspect
from datetime import datetime

class Serializer(object):

    def serialize(self):
        return {c: self.format_date(getattr(self, c)) for c in inspect(self).attrs.keys()}

    #将datetime转成时间
    def format_date(self,value):
        if isinstance(value,datetime):
            value = value.strftime("%Y-%m-%d %H:%M:%S")
        return value




    @staticmethod
    def serialize_list(l):
        return [m.serialize() for m in l]

