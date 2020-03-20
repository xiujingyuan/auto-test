# -*- coding: utf-8 -*-
# @Title: CaseBiz
# @ProjectName gaea-api
# @Description: TODO
# @author fyi zhang
# @date 2019/1/19 22:29


import time
from app import db
import traceback,datetime,decimal,json
from app.models.HistoryCaseModel import HistoryCaseModel
from app.models.HistoryInitModel import HistoryInitModel
from app.models.HistoryPrevModel import HistoryPrevModel
from app.models.ErrorCode import ErrorCode
from sqlalchemy import and_, or_
from flask import current_app

from app.models.RunCasesModel import RunCase


class HistoryBiz(object):

    def search_history(self,request):
        try:
            input_params = request.json

            params =[]
            page_index =1
            page_size=10
            params.append(HistoryCaseModel.history_case_in_date.between("2019-07-01 00:00:00", "2019-07-02 00:00:00"))
            params.append(HistoryCaseModel.history_case_exec_group_priority == "main")
            params.append(HistoryCaseModel.history_case_from_system == "manaowan")
            if input_params is not None:
                if 'history_id' in input_params.keys():
                    value = input_params['history_id']
                    if value is not None and value!='':
                        params.append(HistoryCaseModel.history_id==value)
                if 'case_from_system' in input_params.keys():
                    value = input_params['case_from_system']
                    if value is not None and value!='':
                        params.append(HistoryCaseModel.history_case_from_system.like('%'+value+'%'))
                if 'run_id' in input_params.keys():
                    value = input_params['run_id']
                    if value is not None and value!='':
                        params.append(HistoryCaseModel.run_id==value)
                if 'case_id' in input_params.keys():
                    value = input_params['case_id']
                    if value is not None and value!='':
                        params.append(HistoryCaseModel.history_case_id==value)
                if 'prev_id' in input_params.keys():
                    value = input_params['prev_id']
                    if value is not None and value!='':
                        params.append(HistoryPrevModel.prev_id ==value )
                if 'init_id' in input_params.keys():
                    value = input_params['init_id']
                    if value is not None and value!='':
                        params.append(HistoryInitModel.case_init_id==value)
                if 'case_name' in input_params.keys():
                    value = input_params['case_name']
                    if value is not None and value!='':
                        params.append(HistoryCaseModel.history_case_name.like('%'+value+'%'))
                if 'case_exec_group' in input_params.keys():
                    value = input_params['case_exec_group']
                    if value is not None and value!='':
                        params.append(HistoryCaseModel.history_case_exec_group.like('%'+value+'%'))

                if 'page_index' in input_params.keys():
                    page_index = input_params['page_index']
                if 'page_size' in input_params.keys():
                    page_size = input_params['page_size']
                query = db.session.query(HistoryCaseModel.history_id,
                                         HistoryCaseModel.history_case_name,
                                         HistoryCaseModel.run_id,
                                         HistoryCaseModel.history_case_id,
                                         HistoryPrevModel.prev_id,
                                         HistoryInitModel.case_init_id,
                                         HistoryCaseModel.history_case_exec_group,
                                         HistoryCaseModel.history_case_exec_group_priority,
                                         HistoryCaseModel.history_case_api_address,
                                         HistoryCaseModel.history_case_api_method,
                                         HistoryCaseModel.history_case_api_params,
                                         HistoryCaseModel.history_case_except_value,
                                         HistoryCaseModel.history_case_actual_value,
                                         HistoryCaseModel.history_case_vars,
                                         HistoryCaseModel.history_case_result,
                                         HistoryCaseModel.history_case_sql_actual_statement,
                                         HistoryCaseModel.history_case_sql_params,
                                         HistoryCaseModel.history_case_replace_expression,
                                         HistoryCaseModel.history_case_from_system,
                                         HistoryPrevModel.prev_flag,
                                         HistoryPrevModel.prev_setup_type,
                                         HistoryPrevModel.prev_task_type,
                                         HistoryPrevModel.prev_params,
                                         HistoryPrevModel.prev_expression,
                                         HistoryPrevModel.prev_api_address,
                                         HistoryPrevModel.prev_api_params,
                                         HistoryPrevModel.prev_api_expression,
                                         HistoryPrevModel.prev_sql_statement,
                                         HistoryPrevModel.prev_sql_params,
                                         HistoryPrevModel.prev_sql_expression,
                                         HistoryInitModel.case_init_api_address,
                                         HistoryInitModel.case_init_name,
                                         HistoryInitModel.case_init_api_params,
                                         HistoryInitModel.case_init_api_expression,
                                         HistoryInitModel.case_init_sql,
                                         HistoryInitModel.case_init_sql_params,
                                         HistoryInitModel.case_init_sql_database
                                         )


                query = query.join(HistoryInitModel,
                                   and_(HistoryCaseModel.run_id == HistoryInitModel.run_id,
                                   HistoryInitModel.case_init_case_id==HistoryCaseModel.history_case_id),isouter=True
                                    ).join(HistoryPrevModel,and_(HistoryPrevModel.prev_case_id == HistoryCaseModel.history_case_id,
                                    HistoryCaseModel.run_id == HistoryPrevModel.run_id),isouter=True)

                query = query.filter(*params)
                current_app.logger.info(int(time.time()))
                query=query.order_by(HistoryCaseModel.run_id.desc()).order_by(HistoryCaseModel.history_case_exec_group).order_by(HistoryCaseModel.history_case_exec_priority)
                result_paginate=query.paginate(page=page_index, per_page=page_size, error_out=False)
                current_app.logger.info(int(time.time()))
                result = result_paginate.items
                count = result_paginate.total
                col_name = ('history_id',
                            'history_case_name',
                            'run_id',
                            'history_case_id',
                            'prev_id',
                            'case_init_id',
                            'history_case_exec_group',
                            'history_case_exec_group_priority',
                            'history_case_api_address',
                            'history_case_api_method',
                            'history_case_api_params',
                            'history_case_except_value',
                            'history_case_actual_value',
                            'history_case_vars',
                            'history_case_result',
                            'history_case_sql_actual_statement',
                            'history_case_sql_params',
                            'history_case_replace_expression',
                            'history_case_from_system',
                            'prev_flag',
                            'prev_setup_type',
                            'prev_task_type',
                            'prev_params',
                            'prev_expression',
                            'prev_api_address',
                            'prev_api_params',
                            'prev_api_expression',
                            'prev_sql_statement',
                            'prev_sql_params',
                            'prev_sql_expression',
                            'case_init_api_address',
                            'case_init_name',
                            'case_init_api_params',
                            'case_init_api_expression',
                            'case_init_sql',
                            'case_init_sql_params',
                            'case_init_sql_database'
                )

                results = []
                for res in result:
                    temp={}
                    for col in range(len(col_name)):
                        temp[col_name[col]] = res[col]
                    results.append(temp)
                print(time.time())
                results = self.SerializerDict(results)
                print(time.time())
                data = {}
                data['page_index'] = page_index
                data['cases'] = results
                data['page_size'] = len(results)
                data['total'] = count
                return data
        except Exception as e:
            current_app.logger.exception(e)
            return ErrorCode.ERROR_CODE




    def SerializerDict(self,result):
        if isinstance(result,(list,tuple)):
            for r in result:
                for key,value in r.items():
                    if isinstance(value,datetime.datetime):
                        r[key] = value.strftime("%Y-%m-%d %H:%M:%S")
                    elif isinstance(value,decimal.Decimal):
                        temp= str(value)
                        tem_value = temp.split(".")
                        if(len(tem_value)>1 and int(tem_value[1])==0):
                            r[key]=tem_value[0]
                        else:
                            r[key]=temp
                    elif isinstance(value,str):
                        try:
                            r[key]=json.loads(value,encoding="utf-8")
                        except Exception as e:
                            pass

        elif isinstance(result,dict):
            for key,value in result.items():
                if isinstance(value,datetime.datetime):
                    result[key] = value.strftime("%Y-%m-%d %H:%M:%S")
                elif isinstance(value,decimal.Decimal):
                    temp= str(value)
                    tem_value = temp.split(".")
                    if(len(tem_value)>1 and int(tem_value[1])==0):
                        result[key]=tem_value[0]
                    else:
                        result[key]=temp
                elif isinstance(value,str):
                    try:
                        result[key] = json.loads(value,encoding="utf-8")
                    except Exception as e:
                        pass
        return result

    @staticmethod
    def last_update_history():
        try:
            ret = []
            new_cases = RunCase.query.order_by(RunCase.run_id.desc()).limit(20)
            for new_case in new_cases:
                ret.append(new_case.serialize())
        except Exception as e:
            current_app.logger.exception(e)
            return ret, ErrorCode.ERROR_CODE
        else:
            return ret, "success"

    @staticmethod
    def get_run_case(build_id, request):
        data = {}
        page_index = 1 if "page_index" not in request.json else int(request.json["page_index"])
        page_size = 10 if "page_size" not in request.json else int(request.json["page_size"])
        run_case_list = HistoryCaseModel.query.filter(and_(HistoryCaseModel.build_id == build_id,
                                                           HistoryCaseModel.history_case_exec_group_priority != "sub")
                                                      ).paginate(page=page_index,
                                                                 per_page=page_size,
                                                                 error_out=False)
        if run_case_list:
            result = run_case_list.items
            count = run_case_list.total
            ret = HistoryCaseModel.serialize_list(result)
            data['page_index'] = page_index
            data['cases'] = ret
            data['page_size'] = len(ret)
            data['total'] = count
        return data, "success"

    @staticmethod
    def get_run_case_sub(build_id, exec_group):
        ret = ""
        run_case_list = HistoryCaseModel.query.filter(and_(HistoryCaseModel.build_id == build_id,
                                                           HistoryCaseModel.history_case_exec_group_priority == "sub",
                                                           HistoryCaseModel.history_case_exec_group == exec_group)
                                                      ).all()
        if run_case_list:
            ret = HistoryCaseModel.serialize_list(run_case_list)
        return ret, "success"
