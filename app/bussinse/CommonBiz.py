# -*- coding: utf-8 -*-
# @Title: CaseBiz
# @ProjectName gaea-api
# @Description: TODO
# @author fyi zhang
# @date 2019/1/19 22:29

import app.common.config.config as config

from app import db
from flask import current_app
from app.common.tools.UnSerializer import UnSerializer
from app.common.tools.Serializer import Serializer
from app.models.PrevModel import PrevModel
from app.models.CommonToolsModel import CommonToolsModel

class CommonBiz(UnSerializer,Serializer):

    def get_variable_database_list(self):
        return config.variable_database_list;


    def get_prev_flag(self):
        try:
            result = PrevModel.query.with_entities(PrevModel.prev_flag).distinct().all()
            temp = []
            for re in result :
                temp.append(re[0])
            return temp
        except Exception as e:
            current_app.logger.exception(e)
            db.session.rollback()
            return 9999
        finally:
            db.session.close()

    def get_common_tools(self):
        try:
            temp = db.session.query(CommonToolsModel).all()
            result = CommonToolsModel.serialize_list(temp)
        except Exception as e:
            current_app.logger.exception(e)
            db.session.rollback()
            return 9999
        finally:
            return result
            db.session.close()

