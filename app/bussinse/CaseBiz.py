# -*- coding: utf-8 -*-
# @Title: CaseBiz
# @ProjectName gaea-api
# @Description: TODO
# @author fyi zhang
# @date 2019/1/19 22:29

from app.models.CaseModel import Case
from app import db
from app.bussinse.PrevBiz import PrevBiz
from app.bussinse.MockBiz import MockBiz
from app.bussinse.InitBiz import InitBiz
from app.models.InitModel import InitModel
from app.models.MockModel import MockModel
from app.models.PrevModel import PrevModel
from app.common.tools.UnSerializer import UnSerializer
class CaseBiz(UnSerializer):

    def add_case(self,request):
        request = request.json['case']
        basicInfo = request['basicInfo']
        prevInfo =request['prevInfo']
        initInfo = request['initInfo']
        mockInfo = request['mockInfo']
        if basicInfo is None or basicInfo =='':
            return 0
        try:
            case = Case()
            case.__dict__.update(UnSerializer.un_serialize(basicInfo))
            case.case_id =None
            db.session.add(case)
            db.session.flush()
            case_id = case.case_id
            if  prevInfo is not None and len(prevInfo)>0:
                for single in prevInfo:
                    prev = PrevModel()
                    prev.__dict__.update(UnSerializer.un_serialize(single))
                    prev.prev_case_id = case_id
                    prev.prev_id =None
                    db.session.add(prev)
            if initInfo is not None and len(initInfo)>0:
                for single in initInfo:
                    init = InitModel()
                    init.__dict__.update(UnSerializer.un_serialize(single))
                    init.case_init_case_id = case_id
                    init.case_init_id=None
                    db.session.add(init)

            if mockInfo is not None and len(mockInfo)>0:
                for single in mockInfo:
                    mock = MockModel()
                    mock.__dict__.update(UnSerializer.un_serialize(single))
                    mock.mock_case_id=case_id
                    mock.mock_id=None
                    db.session.add(mock)
            db.session.commit()
            return case_id
        except Exception as e:
            print(e)
            case_id =0
            db.session.rollback()
        finally:
            return case_id


    def get_bussinse_data(self,case_id):
        res ={}
        if (self.check_exists_bycaseid(case_id)==False):
            return None
        res['basicInfo'] = self.get_case_byid(case_id);
        res['prevInfo'] = PrevBiz().get_prev_byid(case_id)
        res['mockInfo'] = MockBiz().get_mock_byid(case_id)
        res['initInfo'] = InitBiz().get_init_byid(case_id)
        return res

    def change_case(self,data,case_id):
        try:
            db.session.query(Case).filter(Case.case_id == case_id).update(data)
        except Exception as e:
            db.session.rollback()
        finally:
            db.session.commit()

    def get_case_byid(self,caseid):
        try:
            result = db.session.query(Case).filter(Case.case_id==caseid).first()
            return result.serialize()
        except Exception as e:
            db.session.rollback()
        finally:
            db.session.commit()

    def check_exists_bycaseid(self,caseid):
        try:
            result = False
            count = db.session.query(Case).filter(Case.case_id == caseid).count()
            if count==1:
                result = True
            return result
        except Exception as e:
            db.session.rollback()
        finally:
            db.session.commit()


    def search_case(self,request):
        input_params = request.json
        params =[]
        page_index =1
        page_size=10
        if input_params is not None:
            print(type(input_params))
            if 'case_from_system' in input_params.keys():
                value = input_params['case_from_system']
                if value is not None and value!='':
                    params.append(Case.case_from_system==value)
            if 'case_description' in input_params.keys():
                value = input_params['case_description']
                if value is not None and value!='':
                    params.append(Case.case_description==value)
            if 'case_name' in input_params.keys():
                value = input_params['case_name']
                if value is not None and value!='':
                    params.append(Case.case_name==value)
            if 'case_is_exec' in input_params.keys():
                value = input_params['case_is_exec']
                if value is not None and value!='':
                    params.append(Case.case_is_exec==value)
            if 'case_executor' in input_params.keys():
                value = input_params['case_executor']
                if value is not None and value!='':
                    params.append(Case.case_executor==value)
            if 'page_index' in input_params.keys():
                page_index = input_params['page_index']
            if 'page_size' in input_params.keys():
                page_size = input_params['page_size']
            for p in params:
                print(p)
        # result_paginate = Case.filter(*params).query.paginate(page=page_index, per_page=page_size, error_out=False)
        result_paginate = db.session.query(Case).filter(*params).all().paginate(page=page_index, per_page=page_size,error_out=False)
        result = result_paginate.items
        count = result_paginate.total



        cases = Case.serialize_list(result)
        data = {}
        data['page_index'] = page_index
        data['cases'] = cases
        data['page_size'] =count
        return data




