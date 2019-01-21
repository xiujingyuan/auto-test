# -*- coding: utf-8 -*-
# @ProjectName:    gaea-api$
# @Package:        $
# @ClassName:      PrevBiz$
# @Description:    描述
# @Author:         Fyi zhang
# @CreateDate:     2019/1/19$ 22:43$
# @UpdateUser:     更新者
# @UpdateDate:     2019/1/19$ 22:43$
# @UpdateRemark:   更新内容
# @Version:        1.0

from app import db
from app.models.PrevModel import PrevModel
from app.common.tools.UnSerializer import UnSerializer
from app.common.tools.Serializer import Serializer

class PrevBiz(UnSerializer):


    def get_bussinse_data(self,case_id):

        if (self.check_exists_bycaseid(case_id)==False):
            return None
        return self.get_prev_byid(case_id)

    def add_prev(self,request):
        try:
            prevInfo = request.json
            prev = PrevModel()
            prev.__dict__.update(prevInfo)
            prev.prev_id=None
            db.session.add(prev)
            db.session.flush()
            return prev.prev_id
        except Exception as e :
            print(e)
            db.session.rollback()
        finally:
            db.session.commit()



    def change_prev(self,data,prev_id):
        try:
            db.session.query(PrevModel).filter(PrevModel.prev_id == prev_id).update(data)
        except Exception as e:
            db.session.rollback()
        finally:
            db.session.commit()

    def delete_prev(self,prev_id):
        try:
            prev = db.session.query(PrevModel).filter(PrevModel.prev_id == prev_id).first()
            db.session.delete(prev)
        except Exception as e:
            pass
        finally:
            db.session.commit()

    def check_exists_bycaseid(self,caseid):
        count = db.session.query(PrevModel).filter(PrevModel.prev_case_id == caseid).count()
        if count>0:
            return True
        else:
            return False

    def check_exists_byprevid(self,prev_id):
        count = db.session.query(PrevModel).filter(PrevModel.prev_id == prev_id).count()
        if count==1:
            return True
        else:
            return False

    def get_prev_byid(self,caseid):
        result = db.session.query(PrevModel).filter(PrevModel.prev_case_id==caseid).all()
        return Serializer.serialize_list(result)
