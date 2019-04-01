# -*- coding: utf-8 -*-
# @ProjectName:    gaea-api$
# @Package:        $
# @ClassName:      InitBiz$
# @Description:    描述
# @Author:         Fyi zhang
# @CreateDate:     2019/1/19$ 22:49$
# @UpdateUser:     更新者
# @UpdateDate:     2019/1/19$ 22:49$
# @UpdateRemark:   更新内容
# @Version:        1.0

from app import db
from app.models.InitModel import InitModel
from app.common.tools.UnSerializer import UnSerializer
from app.common.tools.Serializer import Serializer
from flask import current_app

class InitBiz(UnSerializer):

    def get_bussinse_data(self,case_id):

        if (self.check_exists_bycaseid(case_id)==False):
            return None
        return self.get_init_byid(case_id)

    def get_bussinse_data_by_initid(self,init_id):
        if (self.check_exists_byinitid(init_id)==False):
            return None
        return self.get_init_byinitid(init_id)

    def add_init(self,request):
        try:
            initInfo = request.json
            init = InitModel()
            init.__dict__.update(initInfo)
            init.case_init_id=None
            db.session.add(init)
            db.session.flush()
            id = init.case_init_id
            return self.get_init_byinitid(id)
        except Exception as e :
            current_app.logger.exception(e)
            db.session.rollback()
        finally:
            db.session.commit()

    def change_init(self,data,init_id):
        try:
            db.session.query(InitModel).filter(InitModel.case_init_id == init_id).update(data)
        except Exception as e:
            current_app.logger.exception(e)
            db.session.rollback()
        finally:
            db.session.commit()

    def delete_init(self,init_id):
        try:
            init = db.session.query(InitModel).filter(InitModel.case_init_id == init_id).first()
            db.session.delete(init)
        except Exception as e:
            current_app.logger.exception(e)
        finally:
            db.session.commit()

    def delete_init_bycaseid(self,case_id):
        try:
            init = db.session.query(InitModel).filter(InitModel.case_init_case_id == case_id).delete()
            #db.session.delete(init)
        except Exception as e:
            current_app.logger.exception(e)
        finally:
            db.session.commit()




    def check_exists_byinitid(self,initid):
        try:
            count = db.session.query(InitModel).filter(InitModel.case_init_id == initid).count()
            if count==1:
                return True
            else:
                return False
        except Exception as e:
            current_app.logger.exception(e)
            db.session.rollback()
        finally:
            db.session.commit()


    def check_exists_bycaseid(self,caseid):
        try:
            count = db.session.query(InitModel).filter(InitModel.case_init_case_id == caseid).count()
            if count>0:
                return True
            else:
                return False
        except Exception as e:
            current_app.logger.exception(e)
            db.session.rollback()
        finally:
            db.session.commit()

    def get_init_byid(self,caseid):
        try:
            result = db.session.query(InitModel).filter(InitModel.case_init_case_id==caseid).all()
            return Serializer.serialize_list(result)
        except Exception as e:
            current_app.logger.exception(e)
            db.session.rollback()
        finally:
            db.session.commit()

    def get_init_byinitid(self,init_id):
        try:
            result = db.session.query(InitModel).filter(InitModel.case_init_id==init_id).all()
            return Serializer.serialize_list(result)
        except Exception as e:
            current_app.logger.exception(e)
            db.session.rollback()
        finally:
            db.session.commit()
