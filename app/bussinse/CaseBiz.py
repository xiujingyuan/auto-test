# -*- coding: utf-8 -*-
# @Title: CaseBiz
# @ProjectName gaea-api
# @Description: TODO
# @author fyi zhang
# @date 2019/1/19 22:29
from sqlalchemy.orm import class_mapper

from app.common.tools.Serializer import Serializer
from app.models.CaseModel import Case
from app import db
from flask import current_app
from sqlalchemy import or_,and_,func
from app.bussinse.PrevBiz import PrevBiz
from app.bussinse.MockBiz import MockBiz
from app.bussinse.InitBiz import InitBiz
from app.models.InitModel import InitModel
from app.models.MockModel import MockModel
from app.models.PrevModel import PrevModel
from app.common.tools.UnSerializer import UnSerializer
from app.models.ErrorCode import ErrorCode



class CaseBiz(UnSerializer):

    def  add_case(self,request):
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
                print(request)
                for single in prevInfo:
                    prev = PrevModel()
                    print(single)
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
            current_app.logger.exception(e)
            db.session.rollback()
            return ErrorCode.ERROR_CODE
        finally:
            return case_id


    def get_bussinse_data(self,case_id):
        try:
            res ={}
            if (self.check_exists_bycaseid(case_id)==False):
                return None
            basicInfo = self.get_case_byid(case_id);
            if basicInfo is not None:
                res['basicInfo'] = basicInfo
                res['prevInfo'] = PrevBiz().get_prev_byid(case_id)
                res['mockInfo'] = MockBiz().get_mock_byid(case_id)
                res['initInfo'] = InitBiz().get_init_byid(case_id)
            return res
        except Exception as e:
            current_app.logger.exception(e)
            return ErrorCode.ERROR_CODE


    def change_case(self,data,case_id):
        try:
            db.session.query(Case).filter(Case.case_id == case_id).update(data)
        except Exception as e:
            current_app.logger.exception(e)
            db.session.rollback()
            return ErrorCode.ERROR_CODE
        finally:
            db.session.commit()

    def delete_case_bycaseid(self,case_id):
        try:

            result = db.session.query(Case).filter(Case.case_id == case_id).first()

            result.case_is_exec = -1
            print(result.case_is_exec)
            #db.session.query(Case).filter(Case.case_id == case_id).update()

            # PrevBiz().delete_prev_bycaseid(case_id)
            # InitBiz().delete_init_bycaseid(case_id)
            # MockBiz().delete_mock_bycaseid(case_id)
        except Exception as e:
            current_app.logger.exception(e)
            db.session.rollback()
            return ErrorCode.ERROR_CODE
        finally:
            db.session.commit()
            return 0

    def get_case_byid(self,caseid):
        try:
            result = db.session.query(Case).filter(Case.case_id==caseid).filter(Case.case_is_exec.in_([0,1])).first()
            return result.serialize()
        except Exception as e:
            current_app.logger.exception(e)
            db.session.rollback()
            return ErrorCode.ERROR_CODE
        finally:
            db.session.commit()

    def check_exists_bycaseid(self,caseid):
        try:
            result = False
            count = db.session.query(Case).filter(Case.case_id == caseid).filter(Case.case_is_exec.in_([0,1])).count()
            if count==1:
                result = True
            return result
        except Exception as e:
            current_app.logger.exception(e)
            db.session.rollback()
            return ErrorCode.ERROR_CODE
        finally:
            db.session.commit()


    def search_case(self,request):
        input_params = request.json
        params =[]
        page_index =1
        page_size=10
        sort_field=""
        try:
            if input_params is not None:
                print(type(input_params))
                if 'case_from_system' in input_params.keys():
                    value = input_params['case_from_system']
                    if value is not None and value!='':
                        params.append(Case.case_from_system.like('%'+value+'%'))
                if 'case_description' in input_params.keys():
                    value = input_params['case_description']
                    if value is not None and value!='':
                        params.append(Case.case_description==value)
                if 'case_name' in input_params.keys():
                    value = input_params['case_name']
                    if value is not None and value!='':
                        params.append(Case.case_name.like('%'+value+'%'))
                if 'case_is_exec' in input_params.keys():
                    value = input_params['case_is_exec']
                    if value is not None and value!='':
                        params.append(Case.case_is_exec==value)
                    else:
                        params.append(Case.case_is_exec.in_([0,1]))
                else:
                    params.append(Case.case_is_exec.in_([0,1]))

                if 'case_executor' in input_params.keys():
                    value = input_params['case_executor']
                    if value is not None and value!='':
                        params.append(Case.case_executor==value)
                if 'case_id' in input_params.keys():
                    value = input_params['case_id']
                    if value is not None and value!='':
                        value = self.get_maincaseid_caseid(value)
                        params.append(Case.case_id==value)

                if 'case_exec_group' in input_params.keys():
                    value = input_params['case_exec_group']
                    if value is not None and value!='':
                        params.append(Case.case_exec_group == value)

                if 'case_exec_priority' in input_params.keys():
                    value = input_params['case_exec_priority']
                    if value is not None and value!='':
                        params.append(Case.case_exec_priority==value)


                if 'case_exec_group_priority' in input_params.keys():
                    value = input_params['case_exec_group_priority']
                    if value is not None and value!='':
                        params.append(Case.case_exec_group_priority==value)
                        sort_field='sub'
                else:
                    sort_field='main'
                    params.append(or_(Case.case_exec_group_priority=="main",Case.case_exec_group_priority=="",Case.case_exec_group_priority == None))


                if 'page_index' in input_params.keys():
                    page_index = input_params['page_index']
                if 'page_size' in input_params.keys():
                    page_size = input_params['page_size']
            # result = db.session.query(Case).filter(*params).paginate(page=page_index, per_page=page_size,error_out=False).items
            query = Case.query.filter(*params)
            #current_app.logger.info(query)
            if sort_field=="main":
                result_paginate=query.order_by(Case.case_id.desc(),Case.case_exec_group).paginate(page=page_index, per_page=page_size, error_out=False)
            else:
                result_paginate=query.order_by(Case.case_exec_priority.asc(),Case.case_exec_group).paginate(page=page_index, per_page=page_size, error_out=False)
            result = result_paginate.items
            count = result_paginate.total
            cases = Case.serialize_list(result)
            data = {}
            data['page_index'] = page_index
            data['cases'] = cases
            data['page_size'] = len(cases)
            data['total'] = count
            return data
        except Exception as e :
            current_app.logger.exception(e)
            return ErrorCode.ERROR_CODE

    def get_exec_caseid(self,caseids):
        try:
            result_case_id =[]

            results = db.session.query(Case).filter(Case.case_id.in_(caseids)).filter(Case.case_is_exec.in_([1])).all()

            for result in results:
                case_exec_group = result.case_exec_group
                if case_exec_group is None or case_exec_group=="":
                    result_case_id.append(result.case_id)
                else:
                    main_case = db.session.query(Case).filter(Case.case_exec_group==case_exec_group).filter(Case.case_exec_group_priority=="main").first()
                    if main_case is not None:
                        result_case_id.append(main_case.case_id)
            return result_case_id
        except Exception as e:
            current_app.logger.exception(e)
            db.session.rollback()
            return ErrorCode.ERROR_CODE
        finally:
            db.session.commit()

    def check_execstatus_bycaseid(self,caseid):
        try:
            result = False
            count = db.session.query(Case).filter(Case.case_id == caseid).filter(Case.case_is_exec.in_([1])).count()
            if count==1:
                result = True
            return result
        except Exception as e:
            current_app.logger.exception(e)
            db.session.rollback()
            return ErrorCode.ERROR_CODE
        finally:
            db.session.commit()


    def get_maincaseid_caseid(self,case_id):
        query = db.session.query(Case).filter(Case.case_id==case_id).filter(Case.case_is_exec.in_([0,1]))
        result = query.first()
        if result.case_exec_group_priority=='main':
            return case_id
        else:
            main_result = db.session.query(Case).filter(Case.case_exec_group == result.case_exec_group).filter(Case.case_exec_group_priority=='main').first()
            if main_result is not None:
                return main_result.case_id

        return case_id


    def get_summary_case(self):
        try:
            query = db.session.query(Case.case_from_system, func.count(Case.case_id)).\
                filter(or_(Case.case_exec_group_priority=="main",Case.case_exec_group_priority=="",Case.case_exec_group_priority ==None)).filter(Case.case_is_exec.in_([0,1])).group_by(Case.case_from_system).order_by(func.count(Case.case_id).desc())
            result = query.all()
            return result
        except Exception as e:
            current_app.logger.exception(e)
            db.session.rollback()
            return ErrorCode.ERROR_CODE
        finally:
            db.session.commit()


    def copy_group_case(self,request):
        try:
            print(request.json)
            input_params = request.json
            error_message =""
            case_id = ""
            case_from_system=""
            case_exec_group=""
            if input_params is not None:
                if 'case_id' in input_params.keys():
                    case_id = input_params['case_id']
                if 'case_exec_group' in input_params.keys():
                    case_exec_group = input_params['case_exec_group']
                if 'case_from_system' in input_params.keys():
                    case_from_system= input_params['case_from_system']
                if case_id is None or case_id =="" \
                    or case_from_system is None or case_from_system=="" :
                    error_message ="case_id ,case_from_system 均不能为空"
                    return ErrorCode.ERROR_CODE,error_message
                if 'case_author' in input_params.keys():
                    case_author = input_params['case_author']

            if case_exec_group is None or case_exec_group=="":
                case_exec_group_new=""
            else:
                case_exec_group_new = str(case_exec_group)+'copy'
                if self.check_group_exists(case_exec_group_new):
                    error_message="复杂用例名称已经存在，不能再次复制"
                    return ErrorCode.ERROR_CODE,error_message

            result = self.get_maxandmin_caseid(case_id,case_exec_group,case_from_system)

            db.session.execute("call gaea_framework.copy_case_from_exists_group ('{0}','{1}','{2}','{3}','{4}','{5}')".format(result[1],result[0],case_exec_group,case_from_system,case_exec_group_new,case_author))
            #db.session.execute("call gaea_framework.copy_case_from_exists_group (?,?,?,?,?)",result[1],result[0],case_exec_group,case_from_system,case_exec_group_new)
            return 0,'复制成功'
        except Exception as e:
            current_app.logger.exception(e)
            db.session.rollback()
            return ErrorCode.ERROR_CODE,error_message
        finally:
            db.session.commit()

    def check_group_exists(self,case_exec_group):
        try:
            params =[]
            if 'case_exec_group' is not None and case_exec_group!="":
                params.append(Case.case_exec_group ==case_exec_group)
            params.append(Case.case_is_exec.in_([0,1]))
            result = db.session.query(func.count(Case.case_id)).filter(*params).first()
            if result[0] >0:
                return True
            else:
                return False
        except Exception as e:
            current_app.logger.exception(e)
            db.session.rollback()
            return ErrorCode.ERROR_CODE
        finally:
            db.session.commit()

    def get_maxandmin_caseid(self,case_id,case_exec_group,case_from_system):
        try:
            params =[]
            if 'case_exec_group' is not None and case_exec_group!="":
                params.append(Case.case_exec_group ==case_exec_group)
            else:
                params.append(Case.case_id == case_id)
            params.append(Case.case_from_system == case_from_system)
            result = db.session.query(func.max(Case.case_id).label("max_case_id"),func.min(Case.case_id).label("min_case_id")).filter(*params).first()
            print(result)
            return result
        except Exception as e:
            current_app.logger.exception(e)
            db.session.rollback()
            return ErrorCode.ERROR_CODE
        finally:
            db.session.commit()

    @staticmethod
    def get_new_cases():
        try:
            ret = []
            new_cases = Case.query.filter(Case.case_exec_group_priority == "main").order_by(Case.case_id.desc()).limit(8)
            for new_case in new_cases:
                ret.append(new_case.serialize())
        except Exception as e:
            current_app.logger.exception(e)
            return ret, ErrorCode.ERROR_CODE
        else:
            return ret, "success"
