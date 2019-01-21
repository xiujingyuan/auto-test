# -*- coding: utf-8 -*-
# @Title: Serializer
# @ProjectName gaea-api
# @Description: TODO
# @author fyi zhang
# @date 2019/1/6 15:53
import json

from sqlalchemy.inspection import inspect
from datetime import datetime


class UnSerializer(object):

    @staticmethod
    def un_serialize(o):
        return {c: UnSerializer.format_date(o[c]) for c in o.keys()}

    #将datetime转成时间
    @staticmethod
    def format_date(value):
        if isinstance(value,datetime):
            value = value.strftime("%Y-%m-%d %H:%M:%S")
        elif isinstance(value,dict):
            try:
                value = json.dumps(value)
            except:
                pass
        return value




    @staticmethod
    def un_serialize_list(l):
        return [m.un_serialize() for m in l]

