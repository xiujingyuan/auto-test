# -*- coding: utf-8 -*-
# @Title: CaseBiz
# @ProjectName gaea-api
# @Description: TODO
# @author fyi zhang
# @date 2019/1/19 22:29
from sqlalchemy.orm import class_mapper
from sqlalchemy.sql.functions import current_user

from app.common.redis.redis_cached import update_case_redis
from app.common.tools.Serializer import Serializer
from app.models.CaseModel import Case
from app import db
from flask import current_app
import json

from sqlalchemy import or_, and_, func, inspect
from app.bussinse.PrevBiz import PrevBiz
from app.bussinse.MockBiz import MockBiz
from app.bussinse.InitBiz import InitBiz
from app.models.InitModel import InitModel
from app.models.MockModel import MockModel
from app.models.PrevModel import PrevModel
from app.common.tools.UnSerializer import UnSerializer
from app.models.ErrorCode import ErrorCode
import time


class CaseBiz(UnSerializer):

    def add_case(self, request):
        request = request.json['case']
        basicInfo = request['basicInfo']
        prevInfo = request['prevInfo']
        initInfo = request['initInfo']
        mockInfo = request['mockInfo']
        if basicInfo is None or basicInfo == '':
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
            update_case_redis([case])
            return case_id
        except Exception as e:
            current_app.logger.exception(e)
            db.session.rollback()
            return ErrorCode.ERROR_CODE
        finally:
            return case_id

    def get_bussinse_data(self, case_id):
        try:
            res ={}
            if (self.check_exists_bycaseid(case_id)==False):
                return None
            basicInfo = self.get_case_byid(case_id)
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
            update_case_redis([result], type="delete")
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
            code = 0
            message = '复制成功'
            copy_time = int(time.time())
            copycase_list = []
            if case_exec_group is None or case_exec_group == "":
                copycase = self.copy_case_by_id(case_id, copy_time, case_exec_group)
                copycase_list.append(copycase)
            else:
                all_cases = Case.query.filter(Case.case_exec_group == case_exec_group).all()
                if "_copy_" in case_exec_group:
                    case_exec_group = case_exec_group.split("_copy_")[0]
                case_exec_group_new = "{0}_copy_{1}".format(case_exec_group, copy_time)
                for item_case in all_cases:
                    copycase = self.copy_case_by_id(item_case.case_id, copy_time, case_author, case_exec_group_new)
                    copycase_list.append(copycase)
                # case_exec_group_new = str(case_exec_group)+'copy'
                # if self.check_group_exists(case_exec_group_new):
                #     error_message="复杂用例名称已经存在，不能再次复制"
                #     return ErrorCode.ERROR_CODE,error_message
                #
                # result = self.get_maxandmin_caseid(case_id,case_exec_group,case_from_system)
                #
                # db.session.execute("call gaea_framework.copy_case_from_exists_group ('{0}','{1}','{2}','{3}','{4}','{5}')".format(result[1],result[0],case_exec_group,case_from_system,case_exec_group_new,case_author))
                # #db.session.execute("call gaea_framework.copy_case_from_exists_group (?,?,?,?,?)",result[1],result[0],case_exec_group,case_from_system,case_exec_group_new)

            db.session.commit()
            update_case_redis(copycase_list)
        except Exception as e:
            current_app.logger.exception(e)
            code = ErrorCode.ERROR_CODE
            message = error_message
            db.session.rollback()
        finally:
            return code, message

    def copy_case_by_id(self, case_id, copy_time, case_author, case_exec_group=None):
        oldcase = Case.query.filter(Case.case_id == case_id).one()
        pre_cases = PrevModel.query.filter(PrevModel.prev_case_id == case_id).all()
        init_cases = InitModel.query.filter(InitModel.case_init_case_id == case_id).all()
        copycase = Case()

        for attr in inspect(oldcase).attrs.keys():
            if attr not in ("case_id", "case_last_date", "case_in_date"):
                value = getattr(oldcase, attr)
                if attr == "case_name":
                    if "_copy_" in value:
                        value = value.split("_copy_")[0]
                    value = value + "_copy_{0}".format(copy_time)
                elif attr == "case_exec_group" and case_exec_group is not None:
                    value = case_exec_group
                elif attr in ("case_author", "case_in_user", "case_last_user"):
                    value = case_author
                setattr(copycase, attr, value)
        db.session.add(copycase)
        db.session.flush()

        for pre_case in pre_cases:
            copy_pre_case = PrevModel()
            for pre_attr in inspect(pre_case).attrs.keys():
                if pre_attr not in ("prev_id", "prev_in_date", "prev_last_date"):
                    value = getattr(pre_case, pre_attr)
                    if pre_attr == "prev_case_id":
                        value = copycase.case_id
                    elif pre_attr in ("prev_in_user", "prev_last_user"):
                        value = case_author
                    setattr(copy_pre_case, pre_attr, value)
            db.session.add(copy_pre_case)

        for init_case in init_cases:
            copy_init_case = InitModel()
            for init_attr in inspect(init_case).attrs.keys():

                if init_attr not in ("case_init_id", "case_init_indate", "case_init_lastdate"):
                    value = getattr(init_case, init_attr)
                    if init_attr == "case_init_case_id":
                        value = copycase.case_id
                    elif init_attr in ("case_init_inuser", "case_init_lastuser"):
                        value = case_author
                    setattr(copy_init_case, init_attr, value)
            db.session.add(copy_init_case)
        return copycase

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

    @staticmethod
    def get_all_cases():
        try:

            if current_app.app_redis.exists("gaea_all_cases"):
                ret = json.loads(current_app.app_redis.get("gaea_all_cases"))
            else:
                ret = []
                all_cases = Case.query.filter(Case.case_exec_group_priority == "main")
                for all_case in all_cases:
                    case_serialize = all_case.serialize()
                    ret.append({"case_id": case_serialize["case_id"], "case_name": "{0} {1} {2}".format(
                        case_serialize["case_from_system"],
                        case_serialize["case_category"],
                        case_serialize["case_name"])})
                current_app.app_redis.set("gaea_all_cases", json.dumps(ret, ensure_ascii=False))
        except Exception as e:
            current_app.logger.exception(e)
            return ret, ErrorCode.ERROR_CODE
        else:
            return ret, "success"
