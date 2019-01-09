# -*- coding: utf-8 -*-
# @Title: CaseBussinse
# @ProjectName gaea-api
# @Description: TODO
# @author fyi zhang
# @date 2019/1/6 16:29
from app.models.CaseModel import Case
from app.models.InitModel import InitModel
from app.models.MockModel import MockModel
from app.models.PrevModel import PrevModel

class CaseBussinse(object):


    def get_bussinse_data(self,case_id):
        res ={}
        if (Case.check_exists_bycaseid(case_id)==False):
            return None
        res['basicInfo'] = Case.get_case_byid(case_id);
        res['prevInfo'] = PrevModel.get_prev_byid(case_id)
        res['mockInfo'] = MockModel.get_mock_byid(case_id)
        res['initInfo'] = InitModel.get_init_byid(case_id)
        return res

    def add_case(self,request):
        basicInfo = request.json['basicInfo']
        case = Case()
        case.__dict__.update(basicInfo)
        case.case_id =None
        case_id = Case.add_case(case)

        prevInfo =request.json['prevInfo']
        if prevInfo is not None and len(prevInfo)>0:
            prev = PrevModel()
            prev.__dict__.update(prevInfo)
            prev.prev_case_id = case_id
            PrevModel.add_prev(prev)

        initInfo = request.json['initInfo']
        if initInfo is not None and len(initInfo)>0:
            init = InitModel()
            init.__dict__.update(initInfo)
            init.case_init_case_id = case_id
            InitModel.add_init(init)

        mockInfo = request.json['mockInfo']
        if mockInfo is not None and len(mockInfo)>0:
            mock = MockModel()
            mock.__dict__.update(mockInfo)
            mock.mock_case_id=case_id
            MockModel.add_mock(mock)
        return case_id

    def change_case(self,data,case_id):
        return Case.change_case(data,case_id)

