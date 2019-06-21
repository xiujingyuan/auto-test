# -*- coding: utf-8 -*-
# @Time    : 公元19-05-09 下午5:26
# @Author  : 张廷利
# @Site    :
# @File    : CapitalPlan.py
# @Software: IntelliJ IDEA
import uuid,requests,json
import datetime as dt
import datetime
from environment.common.config import Config
from flask import current_app
from dateutil.relativedelta import relativedelta

class WithdrawSuccessModel(object):



    @classmethod
    def get_calculate_request(cls,product_name,principal_amount,period_count,sign_date):
        guid = str(uuid.uuid4())
        return Config.CMDB_URL, {
            "from_system" : "BIZ",
            "key" : guid,
            "type" : "CalculateRepayPlan",
            "data" : {
                "sign_date" : sign_date,
                "principal_amount" : principal_amount,
                "period_count" : period_count,
                "product_number" : product_name,
                "borrow_days" :None
            }
        }


    @classmethod
    def http_request_post(cls,data,url,headers):
        try:
            req = requests.post(url, data=json.dumps(data), headers=headers,timeout=10)
            result = req.json()
            current_app.logger.info(url+str(result))
            return result
        except Exception as e:
            current_app.logger.exception(e)
            raise str(e)

    @classmethod
    def build_all_params(cls,reqeust_body):

        basic_info = cls.build_basic_params(reqeust_body)
        loan_info = cls.build_loanrecord_params(reqeust_body)
        trans_info,fee_info = cls.generate_params_trans(reqeust_body)

        result =  {
            "type":"AssetWithdrawSuccess",
            "key":str(uuid.uuid1()),
            "from_system": "BIZ",
            "data":{
                "asset":basic_info,
                "loan_record":loan_info,
                "dtransactions":trans_info,
                "fees":fee_info
            }

        }
        # print(json.dumps(result))
        return result



    @classmethod
    def build_basic_params(cls,reqeust_body):
        basic_info = {}
        period_count = reqeust_body['data']['asset']['period_count']
        base_at = cls.string_to_datetime(reqeust_body['data']['asset']['grant_at'])
        period_day = int(reqeust_body['data']['asset']['period_day'])

        basic_info['asset_item_no'] = reqeust_body['data']['asset']['item_no']
        basic_info['type'] = reqeust_body['data']['asset']['type']
        basic_info['sub_type'] = reqeust_body['data']['asset']['sub_type']
        basic_info['period_type'] = reqeust_body['data']['asset']['period_type']
        basic_info['period_count'] = period_count
        basic_info['product_category'] = period_day
        basic_info['cmdb_product_number'] = reqeust_body['data']['asset']['cmdb_product_number']
        basic_info['grant_at'] = reqeust_body['data']['asset']['grant_at']
        basic_info['effect_at'] = reqeust_body['data']['asset']['grant_at']
        delta4=dt.timedelta(hours=+4)

        if period_count ==1:
            deltal = dt.timedelta(days=+period_day)
            due_at = cls.date_to_datetime(base_at+deltal)
        else:
            deltal = relativedelta(months=+ period_count)
            due_at = cls.date_to_datetime(base_at+deltal)


        basic_info['actual_grant_at'] = cls.date_to_datetime(base_at+delta4)
        basic_info['due_at'] = due_at
        basic_info['payoff_at'] = due_at
        basic_info['from_system'] = 'dsq' #reqeust_body['from_system']
        basic_info['status'] = 'repay'
        basic_info['principal_amount'] = int(reqeust_body['data']['asset']['principal_amount']*100)
        basic_info['granted_principal_amount'] = int(reqeust_body['data']['asset']['principal_amount']*100)
        basic_info['loan_channel'] = reqeust_body['data']['asset']['loan_channel']
        basic_info['alias_name'] = reqeust_body['data']['asset']['item_no']
        basic_info['interest_amount'] = int(reqeust_body['data']['asset']['interest_amount'] *100)
        basic_info['fee_amount'] = int(reqeust_body['data']['asset']['fee_amount']*100)
        basic_info['balance_amount'] = 0
        basic_info['repaid_amount'] = 0
        basic_info['total_amount'] = int(reqeust_body['data']['asset']['total_amount']*100)
        basic_info['version'] = 1
        basic_info['interest_rate'] = reqeust_body['data']['asset']['interest_rate']
        basic_info['charge_type'] = reqeust_body['data']['asset']['charge_type']
        basic_info['ref_order_no'] = reqeust_body['data']['asset']['source_number']
        basic_info['ref_order_type'] = reqeust_body['data']['asset']['source_type']
        basic_info['withholding_amount'] = 0
        basic_info['sub_order_type'] = reqeust_body['data']['asset']['sub_order_type']
        return basic_info


    @classmethod
    def build_loanrecord_params(cls,reqeust_body):
        basic_info = {}
        base_at = cls.string_to_datetime(reqeust_body['data']['asset']['grant_at'])
        basic_info['asset_item_no'] = reqeust_body['data']['asset']['item_no']
        basic_info['amount'] = int(reqeust_body['data']['asset']['principal_amount']) * 100
        basic_info['withholding_amount'] = 0
        basic_info['channel'] = reqeust_body['data']['asset']['loan_channel']
        basic_info['status'] = 6
        basic_info['identifier'] = "ID"+str(uuid.uuid1())
        basic_info['trade_no'] = "RN"+str(uuid.uuid1())
        basic_info['due_bill_no'] = reqeust_body['data']['asset']['item_no']
        basic_info['commission_amount'] = None
        basic_info['pre_fee_amount'] = None
        basic_info['service_fee_amount'] = None
        basic_info['is_deleted'] = None
        delta4=dt.timedelta(hours=+4)
        delta3=dt.timedelta(hours=+3)
        basic_info['finish_at'] = cls.date_to_datetime(base_at+delta4)
        basic_info['trans_property'] = None
        basic_info['pre_interest'] = None
        basic_info['commission_amt_interest'] = reqeust_body['data']['asset']['interest_amount']
        basic_info['grant_at'] =cls.date_to_datetime(base_at+delta4)
        basic_info['push_at'] = cls.date_to_datetime(base_at+delta3)
        return basic_info


    @classmethod
    def generate_params_trans(cls,reqeust_body):

        tran_infos=[]
        fee_infos=[]
        dtransactions = reqeust_body['data']['dtransactions']
        fees = reqeust_body['data']['fees']
        base_at = cls.string_to_datetime(reqeust_body['data']['asset']['grant_at'])
        delta4=dt.timedelta(hours=+4)
        for i in range(len(dtransactions)):
            tran_info = {}
            type = dtransactions[i]['dtransaction_type']
            tran_info['asset_item_no']=reqeust_body['data']['asset']['item_no']
            tran_info['type']=type
            tran_info['status']='nofinish'
            tran_info['due_at']=dtransactions[i]['dtransaction_expect_finish_time']
            tran_info['finish_at']="1000-01-01 00:00:00"
            tran_info['period']=dtransactions[i]['dtransaction_period']
            tran_info['late_status']='normal'
            tran_info['remark']=''
            tran_info['trade_at']=cls.date_to_datetime(base_at+delta4)
            tran_info['category']=type

            if type =='grant':
                tran_info['description']='放款'
                tran_info['status']='finish'
                tran_info['finish_at']=cls.date_to_datetime(base_at+delta4)
                tran_info['due_at']=cls.date_to_datetime(base_at+delta4)
                tran_info['period']=0
                tran_info['repay_priority']=1
                tran_info['category']='grant'
            elif type=="repayinterest":
                tran_info['description']='偿还利息'
                tran_info['repay_priority']=11
                tran_info['category']='interest'
            elif type =="repayprincipal":
                tran_info['description']='偿还本金'
                tran_info['repay_priority']=1
                tran_info['category']='principal'

            tran_info['amount']= int(dtransactions[i]['dtransaction_amount'] * 100)
            tran_info['decrease_amount']=0
            tran_info['repaid_amount']=0
            tran_info['balance_amount']=0
            tran_info['total_amount']= int(dtransactions[i]['dtransaction_total_amount']*100)
            tran_infos.append(tran_info)
        for i in range(len(fees)):
            tran_info = {}
            type = fees[i]['fee_type']
            tran_info['asset_item_no']=reqeust_body['data']['asset']['item_no']
            tran_info['type']=type
            tran_info['status']='nofinish'
            tran_info['due_at']=fees[i]['fee_expect_finish_time']
            tran_info['finish_at']="1000-01-01 00:00:00"
            tran_info['period']=fees[i]['fee_period']
            tran_info['late_status']='normal'
            tran_info['remark']=''
            tran_info['trade_at']=cls.date_to_datetime(base_at+delta4)
            tran_info['category']='fee'
            tran_info['description']='技术服务费'
            tran_info['repay_priority']=21
            tran_info['amount']= int(fees[i]['fee_amount'] * 100)
            tran_info['decrease_amount']=0
            tran_info['repaid_amount']=0
            tran_info['balance_amount']=0
            tran_info['total_amount']= int(fees[i]['fee_total_amount']*100)
            fee_infos.append(tran_info)


        return tran_infos,fee_infos



    @classmethod
    def date_to_datetime(cls,date_time=None):
        if date_time is None:
            date_time = dt.now()
        return date_time.strftime("%Y-%m-%d %H:%M:%S")

    @classmethod
    def string_to_datetime(cls,date_string):
        return datetime.datetime.strptime(date_string,"%Y-%m-%d %H:%M:%S")


