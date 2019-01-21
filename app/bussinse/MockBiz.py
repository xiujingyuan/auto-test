# -*- coding: utf-8 -*-
# @ProjectName:gaea-api$
# @Package:        $
# @ClassName:      MockBiz$
# @Description:    描述
# @Author:         Fyi zhang
# @CreateDate:     2019/1/19$ 22:30$
# @UpdateUser:     更新者
# @UpdateDate:     2019/1/19$ 22:30$
# @UpdateRemark:   更新内容
# @Version:        1.0

from app import db
from app.models.MockModel import MockModel
from app.common.tools.UnSerializer import UnSerializer
from app.common.tools.Serializer import Serializer

class MockBiz(UnSerializer):

    def check_exists_bycaseid(self,case_id):
        count = db.session.query(MockModel).filter(MockModel.mock_case_id == case_id).count()
        if count>0:
            return True
        else:
            return False

    def get_mock_byid(self,case_id):
        result = db.session.query(MockModel).filter(MockModel.mock_case_id==case_id).all()
        return Serializer.serialize_list(result)

    def get_bussinse_data(self,case_id):
        if (self.check_exists_bycaseid(case_id)==False):
            return None
        return MockModel.get_mock_byid(case_id)

    def add_mock(self,request):
        try:
            mockInfo = request.json
            mock = MockModel()
            mock.__dict__.update(mockInfo)
            mock.mock_id=None
            db.session.add(mock)
            db.session.flush()
            return mock.mock_id
        except Exception as e :
            db.session.rollback()
        finally:
            db.session.commit()

    def change_mock(self,data,mock_id):
        try:
            db.session.query(MockModel).filter(MockModel.mock_id == mock_id).update(data)
        except Exception as e:
            db.session.rollback()
        finally:
            db.session.commit()

    def check_exists_bymockid(self,mock_id):
        return self.check_exists_bymockid(mock_id)

    def delete_mock(self,mock_id):
        try:
            mock = db.session.query(MockModel).filter(MockModel == mock_id).first()
            db.session.delete(mock)
        except Exception as e:
            pass
        finally:
            db.session.commit()





