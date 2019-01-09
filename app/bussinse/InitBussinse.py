# -*- coding: utf-8 -*-
# @Title: CaseBussinse
# @ProjectName gaea-api
# @Description: TODO
# @author fyi zhang
# @date 2019/1/6 16:29
from app.models.InitModel import InitModel

class InitBussinse(object):


    def get_bussinse_data(self,case_id):

        if (InitModel.check_exists_bycaseid(case_id)==False):
            return None
        return InitModel.get_init_byid(case_id)

    def add_init(self,request):
        initInfo = request.json
        init = InitModel()
        init.__dict__.update(initInfo)
        init.case_init_id=None
        return InitModel.add_init(init)

    def change_init(self,data,init_id):
        return InitModel.change_init(data,init_id)

    def check_exists_byinitid(self,init_id):
        return InitModel.check_exists_byinitid(init_id)

