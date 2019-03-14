# -*- coding: utf-8 -*-
# @Title: CaseBiz
# @ProjectName gaea-api
# @Description: TODO
# @author fyi zhang
# @date 2019/1/19 22:29

from app.models.ParamsModel import ParamsModel
from app import db
from app.common.tools.UnSerializer import UnSerializer

class ParamsBiz(UnSerializer):

    def add_params(self,request):
        try:
            paramsInfo = request.json
            p = ParamsModel()
            p.__dict__.update(paramsInfo)
            p.id=None
            db.session.add(p)
            db.session.flush()
            id = p.id
            db.session.commit()
        except Exception as e:
            db.session.rollback()
        finally:
            return id



    def change_params(self,data,params_id):
        try:
            db.session.query(ParamsModel).filter(ParamsModel.id == params_id).update(data)
        except Exception as e:
            db.session.rollback()
        finally:
            db.session.commit()

    def get_params_byid(self,params_id):
        try:
            result = db.session.query(ParamsModel).filter(ParamsModel.id==params_id).first()
            return result.serialize()
        except Exception as e:
            db.session.rollback()
        finally:
            db.session.commit()


    def search_params(self,request):
        input_params = request.json
        params =[]
        page_index =1
        page_size=10
        print(type(input_params))
        if 'name' in input_params.keys():
            value = input_params['name']
            if value is not None and value!='':
                params.append(ParamsModel.name==value)
        if 'action' in input_params.keys():
            value = input_params['action']
            if value is not None and value!='':
                params.append(ParamsModel.action==value)
        if 'status' in input_params.keys():
            value = input_params['status']
            if value is not None and value!='':
                params.append(ParamsModel.status==value)
        if 'type' in input_params.keys():
            value = input_params['type']
            if value is not None and value!='':
                params.append(ParamsModel.type==value)
        if 'page_index' in input_params.keys():
            page_index = input_params['page_index']
        if 'page_size' in input_params.keys():
            page_size = input_params['page_size']
        for p in params:
            print(p)
        #result_paginate = db.session.query(ParamsModel).filter(*params).paginate(page=page_index, per_page=page_size,error_out=False)
        result_paginate = ParamsModel.query.filter(*params).paginate(page=page_index, per_page=page_size, error_out=False)
        result = result_paginate.items
        total = result_paginate.total
        params =  ParamsModel.serialize_list(result)
        data={}
        data['page_index']=page_index
        data['params']=params
        data['page_size']=len(params)
        data['total']=total
        return data




