# -*- coding: utf-8 -*-
# @Title: CaseBussinse
# @ProjectName gaea-api
# @Description: TODO
# @author fyi zhang
# @date 2019/1/6 16:29
from app.models.PrevModel import PrevModel

class PrevBussinse(object):


    def get_bussinse_data(self,case_id):

        if (PrevModel.check_exists_bycaseid(case_id)==False):
            return None
        return PrevModel.get_prev_byid(case_id)

    def add_prev(self,request):
        prevInfo = request.json
        prev = PrevModel()
        prev.__dict__.update(prevInfo)
        prev.prev_id=None
        return PrevModel.add_init(prev)

    def change_prev(self,data,prev_id):
        return PrevModel.change_prev(data,prev_id)

    def check_exists_byprevid(self,prev_id):
        return PrevModel.check_exists_bymockid(prev_id)