# -*- coding: utf-8 -*-
# @Time    : 公元19-05-09 下午5:26
# @Author  : 张廷利
# @Site    :
# @File    : CapitalPlan.py
# @Software: IntelliJ IDEA
import traceback
import uuid,requests,json
import datetime as dt
import datetime
from environment.common.config import Config
from flask import current_app
from dateutil.relativedelta import relativedelta

class CapitalPlanModel(object):



    @classmethod
    def get_calculate_request(cls,product_name,principal_amount,period_count,sign_date):
        guid = str(uuid.uuid4())
        return Config.CMDB_URL_v6, {
            "from_system" : "BIZ",
            "key" : guid,
            "type" : "CalculateRepayPlan",
            "data" : {
                "sign_date" : sign_date,
                "apply_amount" : principal_amount,
                "period_count" : period_count,
                "product_number" : product_name
            }
        }


    @classmethod
    def http_request_post(cls,data,url,headers):
        try:
            req = requests.post(url, data=json.dumps(data), headers=headers,timeout=10)
            current_app.logger.info(req)
            result = req.json()
            current_app.logger.info(url+str(result))
            return result
        except Exception as e:
            current_app.logger.info(traceback.format_exc())
            current_app.logger.exception(e)
            return req.text

    @classmethod
    def build_all_params(cls,channel,item_no,period_count,period,sign_at,granted_amount,cmdb_no,calc_rate,fee_rate,interest_rate):
        if calc_rate['code']==400:
            return "获取费率系统失败"
        basic_info = cls.build_basic_params(channel,item_no,period_count,period,sign_at,granted_amount,cmdb_no)
        trans_info = cls.build_transaction_params_new(calc_rate,period_count,item_no,sign_at,fee_rate,interest_rate)
        basic_info['capital_transactions']=trans_info
        return basic_info


    @classmethod
    def build_basic_params(cls,channel,item_no,period_count,period,sign_at,granted_amount,cmdb_no):
        basic_info = {}
        basic_info['channel'] = channel
        basic_info['status'] = 'repay'
        basic_info['version'] = 0
        basic_info['item_no'] = item_no
        basic_info['period_count'] = period_count
        if period_count==1:
            basic_info['period_type'] = 'day'
        else:
            basic_info['period_type'] = 'month'
        basic_info['period_term'] = period
        base_at = cls.string_to_datetime(sign_at)
        delta1=dt.timedelta(hours=+1)
        basic_info['push_at'] =cls.date_to_datetime(base_at+delta1)
        delta2=dt.timedelta(hours=+2)
        basic_info['granted_at'] = cls.date_to_datetime(base_at+delta2)
        basic_info['granted_amount'] = granted_amount

        if period_count == 1:
            if channel=='qnn':
                due_at={
                    "qnn_lm_1_30d_20190103":30,
                    "qnn_lm_1_30d_180d_20190701":180,
                    "qnn_lm_1_30d_360d_20190701":360,
                    "qnn_lm_1_30d_540d_20190701":540
                }
                try:
                    delta3 = dt.timedelta(days=+due_at[cmdb_no])
                except:
                    delta3 = dt.timedelta(days=+period)
            else:
                delta3 = dt.timedelta(days=+period)
        else:
            delta3 = relativedelta(months=+ period_count)
        basic_info['due_at'] = cls.date_to_datetime(base_at+delta3)
        basic_info['cmdb_no'] = cmdb_no
        basic_info['year_days'] = 365
        basic_info['create_at'] = sign_at
        delta2=dt.timedelta(hours=+3)
        basic_info['update_at'] = cls.date_to_datetime(base_at+delta2)
        basic_info['finish_at'] = "1000-01-01 00:00:00"
        return basic_info

    @classmethod
    def build_transaction_params_new(cls,calc_rate,period_count,item_no,sign_at,fee_rate,interest_rate):
        tran_info_list = []

        principal_list=None
        interest_list = None
        service_list = None
        technical_service_list=None
        after_loan_manage_list=None
        technical_service1_list=None

        principal = None
        service = None
        interest = None
        technical_service=None
        after_loan_manage=None
        technical_service1=None
        current_app.logger.info("calc_rate is {0}".formate(calc_rate))
        trans = calc_rate['data']['calculate_result']
        if 'principal' in trans.keys():
            principal = trans['principal']
        if 'interest' in trans.keys():
            interest = trans['interest']
        if 'fee' in trans.keys():
            fees = trans['fee']
            if 'technical_service' in fees.keys():
                technical_service = trans['fee']['technical_service']
            if 'after_loan_manage' in fees.keys():
                after_loan_manage = trans['fee']['after_loan_manage']
            if 'service' in fees.keys():
                service=trans['fee']['service']
            if 'technical_service1' in fees.keys():
                technical_service1 = trans['fee']['technical_service1']

        if principal is not None and len(principal)>0:
            principal_list=cls.generate_params_trans('principal',principal,period_count,sign_at,item_no,fee_rate,interest_rate)
        if interest is not None and len(interest)>0:
            interest_list=cls.generate_params_trans('interest',interest,period_count,sign_at,item_no,fee_rate,interest_rate)
        if service is not None and len(service)>0:
            service_list=cls.generate_params_trans('service',service,period_count,sign_at,item_no,fee_rate,interest_rate)
        if technical_service is not None and len(technical_service)>0:
            technical_service_list=cls.generate_params_trans('technical_service',technical_service,period_count,sign_at,item_no,fee_rate,interest_rate)
        if after_loan_manage is not None and len(after_loan_manage) > 0:
            after_loan_manage_list = cls.generate_params_trans('after_loan_manage', after_loan_manage, period_count,sign_at, item_no, fee_rate, interest_rate)
        if technical_service1 is not None and len(technical_service1) > 0:
            technical_service1_list = cls.generate_params_trans('technical_service1', technical_service1, period_count, sign_at, item_no, fee_rate,interest_rate)

        if principal_list is not None and len(principal_list)>0:
            tran_info_list.extend(principal_list)
        if interest_list is not None and len(interest_list)>0:
            tran_info_list.extend(interest_list)
        if service_list is not None and len(service_list)>0:
            tran_info_list.extend(service_list)
        if technical_service_list is not None and len(technical_service_list)>0:
            tran_info_list.extend(technical_service_list)
        if after_loan_manage_list is not None and len(after_loan_manage_list)>0:
            tran_info_list.extend(after_loan_manage_list)
        if technical_service1_list is not None and len(technical_service1_list)>0:
            tran_info_list.extend(technical_service1_list)

        return tran_info_list

    @classmethod
    def build_transaction_params(cls,calc_rate,period_count,item_no,sign_at,fee_rate,interest_rate):
        tran_info_list =[]

        manage=None
        interest_list =None
        service_list =None
        manage_list=None
        principal =None
        service = None
        interest=None


        trans = calc_rate['data']['calculate_result']
        if 'principal' in trans.keys():
            principal = trans['principal']
        if 'interest' in trans.keys():
            interest = trans['interest']
        if 'fee' in trans.keys():
            fees = trans['fee']
            if 'service' in fees.keys():
                service = trans['fee']['service']
            if 'manage' in fees.keys():
                manage = trans['fee']['manage']

        if principal is not None and len(principal)>0:
            principal_list=cls.generate_params_trans('principal',principal,period_count,sign_at,item_no,fee_rate,interest_rate)
        if interest is not None and len(interest)>0:
            interest_list=cls.generate_params_trans('interest',interest,period_count,sign_at,item_no,fee_rate,interest_rate)
        if service is not None and len(service)>0:
            service_list=cls.generate_params_trans('service',service,period_count,sign_at,item_no,fee_rate,interest_rate)
        if manage is not None and len(manage)>0:
            manage_list=cls.generate_params_trans('our_service',manage,period_count,sign_at,item_no,fee_rate,interest_rate)

        if principal_list is not None and len(principal_list)>0:
            tran_info_list.extend(principal_list)
        if interest_list is not None and len(interest_list)>0:
            tran_info_list.extend(interest_list)
        if service_list is not None and len(service_list)>0:
            tran_info_list.extend(service_list)
        if manage_list is not None and len(manage_list)>0:
            tran_info_list.extend(manage_list)

        return tran_info_list



    @classmethod
    def generate_params_trans(cls,type,entity,period_count,sign_at,item_no,fee_rate,interest_rate):
        tran_infos=[]

        for i in range(len(entity)):
            tran_info = {}
            tran_info['period'] = i+1
            tran_info['type'] = type
            tran_info['amount'] =0
            if type =="interest":
                tran_info['rate'] =interest_rate
            elif type =='service':
                tran_info['rate'] =fee_rate
            else:
                tran_info['rate'] =0
            tran_info['item_no'] =item_no
            tran_info['period_term'] =30
            if period_count ==1:
                tran_info['period_type'] ="day"
                tran_info['repayment_type'] ="rtlataio"
            else:
                tran_info['period_type'] ="month"
                tran_info['repayment_type'] ="acpi"
            #tran_info['expect_finished_at'] =cls.get_expect_finished_at(i,sign_at)
            tran_info['expect_finished_at'] =entity[i]['date']
            delta4=dt.timedelta(hours=+4)
            tran_info['create_at'] = cls.date_to_datetime(cls.string_to_datetime(sign_at)+delta4)
            delta5=dt.timedelta(hours=+5)
            tran_info['update_at'] = cls.date_to_datetime(cls.string_to_datetime(sign_at)+delta5)
            tran_info['origin_amount'] =entity[i]['amount']
            tran_info['user_repay_at'] ="1000-01-01 00:00:00"
            tran_info['user_repay_channel'] =""
            tran_info['actual_finished_at'] ="1000-01-01 00:00:00"
            tran_info['operate_type'] ='grant'
            tran_infos.append(tran_info)

        return tran_infos



    @classmethod
    def date_to_datetime(cls,date_time=None):
        if date_time is None:
            date_time = dt.now()
        return date_time.strftime("%Y-%m-%d %H:%M:%S")

    @classmethod
    def string_to_datetime(cls,date_string):
        return datetime.datetime.strptime(date_string,"%Y-%m-%d %H:%M:%S")


