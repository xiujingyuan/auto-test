# -*- coding: utf-8 -*-
# @Title: CaseBussinse
# @ProjectName gaea-api
# @Description: TODO
# @author fyi zhang
# @date 2019/1/6 16:29
from app.models.MockModel import MockModel

class MockBussinse(object):


    def get_bussinse_data(self,case_id):

        if (MockModel.check_exists_bycaseid(case_id)==False):
            print("caseid")
            return None
        return MockModel.get_mock_byid(case_id)

    def add_mock(self,request):
        mockInfo = request.json
        mock = MockModel()
        mock.__dict__.update(mockInfo)
        mock.mock_id=None
        return MockModel.add_mock(mock)

    def change_mock(self,data,mock_id):
        return MockModel.change_mock(data,mock_id)

    def check_exists_bymockid(self,mock_id):
        return MockModel.check_exists_bymockid(mock_id)

   