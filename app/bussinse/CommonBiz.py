# -*- coding: utf-8 -*-
# @Title: CaseBiz
# @ProjectName gaea-api
# @Description: TODO
# @author fyi zhang
# @date 2019/1/19 22:29

import app.common.config.config as config
import smtplib,json,os
from app import db
from flask import current_app
from werkzeug.utils import secure_filename
from app.common.tools.UnSerializer import UnSerializer
from app.common.tools.Serializer import Serializer
from app.models.PrevModel import PrevModel
from app.models.CommonToolsModel import CommonToolsModel
from app.models.CapitalPlanModel import CapitalPlanModel
from app.models.CaseModel import Case
from app.models.WithdrawSuccessModel import WithdrawSuccessModel
from app.models.RepaySuccessModel import RepaySuccessModel
from email.header import Header
from email.mime.text import MIMEText
from app.models.ErrorCode import ErrorCode
import datetime
from app.bussinse import executesql
import time


class CommonBiz(UnSerializer,Serializer):

    def get_variable_database_list(self):
        return config.variable_database_list;


    def get_prev_flag(self):
        try:
            result = PrevModel.query.with_entities(PrevModel.prev_flag).distinct().all()
            temp = []
            for re in result :
                temp.append(re[0])
            return temp
        except Exception as e:
            current_app.logger.exception(e)
            db.session.rollback()
            return ErrorCode.ERROR_CODE
        #finally:
        #db.session.close()

    def get_from_system(self):
        try:
            result = PrevModel.query.with_entities(Case.case_from_system).filter(Case.case_from_system!="").distinct().all()
            temp = []
            for re in result :
                temp.append(re[0])
            return temp
        except Exception as e:
            current_app.logger.exception(e)
            db.session.rollback()
            return ErrorCode.ERROR_CODE
        #finally:
        #db.session.close()

    def get_common_tools(self):
        try:
            temp = db.session.query(CommonToolsModel).all()
            result = CommonToolsModel.serialize_list(temp)
        except Exception as e:
            current_app.logger.exception(e)
            db.session.rollback()
            return ErrorCode.ERROR_CODE
        else:
            return result
            #db.session.close()

    def sendMail(self,request):
        try:
            request_json = request.json
            to_email = [x for x in request_json['to_mail'].split(";") if x and x!='\n']
            content = request_json['content']
            #to_cc = request_json['to_cc']
            sender = 'zhangtingli@kuainiugroup.com'
            sender_mail = 'zdcs@kuainiugroup.com'
            sender_passwd = 'LEtgfndJZPzBDYsj'
            mail_title = request_json['mail_title']
            message = MIMEText(content,'html','utf-8')
            message['From'] = Header(sender_mail, 'utf-8')
            message['To'] = Header(','.join(to_email), 'utf-8')
            message['Subject'] =Header(mail_title, 'utf-8')
            current_app.logger.info(to_email)
            smtp = smtplib.SMTP_SSL(host='smtp.exmail.qq.com')
            smtp.connect(host='smtp.exmail.qq.com',port=465)
            smtp.login(sender, sender_passwd)
            current_app.logger.info(to_email)
            smtp.sendmail(sender, to_email, message.as_string())
            print("发送邮件成功！！！")
            smtp.quit()
        except Exception as e:
            current_app.logger.exception(e)
            print("发送邮件失败！！！")
            return ErrorCode.ERROR_CODE

    def capitalPlan(self,request):
        try:
            request_json = request.json
            interest_rate = 0.0
            fee_rate=0.0
            risk_level=None
            channel=None
            if 'product_name' in request_json.keys():
                product_name = request_json['product_name']
            if 'principal_amount' in request_json.keys():
                principal_amount = request_json['principal_amount']
            if 'period_count' in request_json.keys():
                period_count = request_json['period_count']
            if 'sign_date' in request_json.keys():
                sign_date = request_json['sign_date']
            if 'channel' in request_json.keys():
                channel = request_json['channel']
            if 'item_no' in request_json.keys():
                item_no = request_json['item_no']
            if 'period' in request_json.keys():
                period = request_json['period']
            if 'call_back' in request_json.keys():
                call_back = request_json['call_back']
            if 'fee_rate' in request_json.keys():
                fee_rate = request_json['fee_rate']
            if 'interest_rate' in request_json.keys():
                interest_rate = request_json['interest_rate']
            if 'risk_level' in request_json.keys():
                risk_level=request_json['risk_level']
                try:
                    risk_level=int(risk_level)
                except:
                    pass

            if channel=='qnn' and risk_level is not None:
                if risk_level in [0,1,2]:
                    product_name='qnn_lm_1_30d_20190103'
                elif risk_level in [3,4,5]:
                    product_name='qnn_lm_1_30d_180d_20190701'
                elif risk_level in [6,7]:
                    product_name='qnn_lm_1_30d_360d_20190701'
                elif risk_level in [8,9,10,99]:
                    product_name='qnn_lm_1_30d_540d_20190701'


            cmdb_url,cmdb_request = CapitalPlanModel.get_calculate_request(product_name,principal_amount,period_count,sign_date)
            current_app.logger.info(cmdb_request)
            headers ={'content-type': 'application/json'}
            result = CapitalPlanModel.http_request_post(cmdb_request,cmdb_url,headers)
            params = CapitalPlanModel.build_all_params(channel,item_no,int(period_count),int(period),sign_date,principal_amount,product_name,result,fee_rate,interest_rate)
            urls = call_back.split(";")
            for url in urls:
                if  url is not None and url !="":
                    CapitalPlanModel.http_request_post(params,url,headers)
            return params
        except Exception as e:
            current_app.logger.exception(e)
            return ErrorCode.ERROR_CODE

    def withdrawSuccess(self,request):
        try:
            if isinstance(request,dict):
                request_json = request
            else:
                request_json = request.json

            import_params = request_json['request_body']
            if (type(import_params)==dict):
                request_body = import_params
            else:
                request_body = request_json['request_body'].replace("'",'"').replace('None','null')
                request_body = json.loads(request_body)


            call_back = request_json['call_back']
            params = WithdrawSuccessModel.build_all_params(request_body)
            urls = call_back.split(";")

            for url in urls:

                if  url is not None and url !="":
                    headers ={'content-type': 'application/json'}
                    WithdrawSuccessModel.http_request_post(params,url,headers)
            return params
        except Exception as e:
            current_app.logger.exception(e)
            return ErrorCode.ERROR_CODE


    def grantWithdrawSuccess(self,request):
        try:
            request_dict = request.json
            if "item_no" in request_dict.keys():
                item_no = request_dict['item_no']
            if "env" in request_dict.keys():
                env = request_dict['env']
            if "call_back" in request_dict.keys():
                call_back = request_dict['call_back']

            sql = '''
                select task_request_data from {0}.task where task_order_no='{1}'
            '''.format(env,item_no)
            result = db.session.execute(sql).fetchone()
            defualt_withdraw ="http://kong-api-test.kuainiujinke.com/{0}/central/withdraw-success-receive;".format(env[1:])
            if result is None:
                return "放款成功通知失败，进件数据没有进件到gbiz 的task 表"
            call_back = defualt_withdraw +call_back
            result = json.loads(result.task_request_data)
            result['data']['asset']['overdue_guarantee_amount']=0
            result['data']['asset']['info']=""

            request_body = {
                "request_body":result,
                "call_back":call_back
            }
            withdraw_success_result = self.withdrawSuccess(request_body)
            if withdraw_success_result ==ErrorCode.ERROR_CODE:
                return "放款成功通知失败，具体错误信息请联系管理员"

            capital_plan_result = self.grant_capital_plan(result,env)
            if capital_plan_result==ErrorCode.ERROR_CODE or isinstance(capital_plan_result,str):
                return capital_plan_result
            else:
                return capital_plan_result

        except Exception as e:
            current_app.logger.exception(e)
            return ErrorCode.ERROR_CODE

    def grant_capital_plan(self,request,env):
        try:
            risk_level=None
            channel=None
            period_count=None
            request_json = request['data']['asset']
            if 'cmdb_product_number' in request_json.keys():
                product_name = request_json['cmdb_product_number']
            if 'principal_amount' in request_json.keys():
                principal_amount = int(request_json['principal_amount']) *100
            if 'period_count' in request_json.keys():
                period_count = request_json['period_count']
            if 'grant_at' in request_json.keys():
                sign_date = request_json['grant_at']
            if 'loan_channel' in request_json.keys():
                channel = request_json['loan_channel']
            if 'item_no' in request_json.keys():
                item_no = request_json['item_no']
            if 'period_day' in request_json.keys():
                period = request_json['period_day']
            if 'fee_rate' in request_json.keys():
                fee_rate = request_json['fee_rate']
            if 'interest_rate' in request_json.keys():
                interest_rate = request_json['interest_rate']
            if 'risk_level' in request_json.keys():
                risk_level=request_json['risk_level']
                try:
                    risk_level=int(risk_level)
                except:
                    pass

            if channel=='qnn' and risk_level is not None and period_count == 1:
                if risk_level in [0,1,2]:
                    product_name='qnn_lm_1_30d_20190103'
                elif risk_level in [3,4,5]:
                    product_name='qnn_lm_1_30d_180d_20190701'
                elif risk_level in [6,7]:
                    product_name='qnn_lm_1_30d_360d_20190701'
                elif risk_level in [8,9,10,99]:
                    product_name='qnn_lm_1_30d_540d_20190701'

            defualt_capital ="http://kong-api-test.kuainiujinke.com/{0}/capital-asset/asset-loan;http://kong-api-test.kuainiujinke.com/{1}/capital-asset/grant;".format(env[1:],'r'+env[1:])
            cmdb_url,cmdb_request = CapitalPlanModel.get_calculate_request(product_name,principal_amount,period_count,sign_date)
            print(cmdb_request)
            headers ={'content-type': 'application/json'}
            result = CapitalPlanModel.http_request_post(cmdb_request,cmdb_url,headers)
            params = CapitalPlanModel.build_all_params(channel,item_no,int(period_count),int(period),sign_date,principal_amount,product_name,result,fee_rate,interest_rate)
            if isinstance(params,str):
                # return "汇率编号已经失效，无法生成资方还款计划"
                return result["message"] if "message" in result else "费率编号已经失效，无法生成资方还款计划"
            urls = defualt_capital.split(";")
            for url in urls:
                print(url)
                if url is not None and url != "":
                    res = CapitalPlanModel.http_request_post(params, url, headers)
                    res["url"] = url
                    if not isinstance(res, (dict, list)) or ("code" in res and res["code"] == 1):
                        return res
            return params
        except Exception as e:
            current_app.logger.exception(e)
            return ErrorCode.ERROR_CODE


    def upload_save_file(self,request):
        try:
            data = {
                "code": 1,
                "message": ""
            }

            if 'upfile' in request.files:
                file = request.files['upfile']
            print(request)
            if 'branch_name' in request.json:
                branch_name = request.json['branch_name']
            filename_ext = file.filename
            if '.' in filename_ext :
                filename = secure_filename(filename_ext)
                path = os.path.json(config.image_path,branch_name)
                if os.path.exists(path)==False:
                    print(path)
                    os.makedirs(path)
                file.save(os.path.join(path,filename))
                data['code']=0
                data['message']='上传成功'

            return data
        except Exception as e:
            current_app.logger.exception(e)

    def getEveryDay(self,begin_day,end_day):
        date_list = []
        begin_date = datetime.datetime.strptime(begin_day, "%Y-%m-%d")
        end_date = datetime.datetime.strptime(end_day, "%Y-%m-%d")
        while begin_date <= end_date:
            date_str = begin_date.strftime("%Y-%m-%d")
            date_list.append(date_str)
            begin_date += datetime.timedelta(days=1)
        return date_list

    def set_capital_loan_condition(self,request):
        '''

        :param request:
        {
        "env":4,
        "channel":"qnn",
        "period_count":1,
        "begin_day":"2019-10-12",
        "end_day":"2019-10-14"
        }
        :return:
        '''

        request_dict = request.json
        env=request_dict['env']
        env='biz'+str(env)
        begin_day=request_dict['begin_day']
        end_day = request_dict['end_day']
        channel=request_dict['channel']
        period_count=request_dict['period_count']
        period_count=int(period_count)
        if period_count == 1:
            period_type='day'
            period_day=30
        else:
            period_type = 'month'
            period_day = 0
        day_list=self.getEveryDay(begin_day,end_day)
        db=executesql.db_connect()


        if day_list is not None and len(day_list)>0:
            for day in day_list:
                clear_sql='''
                delete  from {0}.capital_loan_condition where capital_loan_condition_channel= '{1}' and capital_loan_condition_period_count= {2} and capital_loan_condition_day= '{3}'
                '''.format(env,channel,period_count,day)
                m=db.do_sql(clear_sql,env)
                print(m)
                print(clear_sql)
                insert_sql='''
                INSERT INTO {0}.capital_loan_condition ( `capital_loan_condition_day`, `capital_loan_condition_channel`, `capital_loan_condition_description`, `capital_loan_condition_amount`, `capital_loan_condition_from_system`, `capital_loan_condition_sub_type`, `capital_loan_condition_period_count`, `capital_loan_condition_period_type`, `capital_loan_condition_period_days`, `capital_loan_condition_update_memo`, `capital_loan_condition_create_at`, `capital_loan_condition_update_at`)
                VALUES
                ( '{1}', '{2}', '分期贷款', 100000000, 'dsq', 'multiple', "{3}", '{4}', {5}, '接口插入', now(), now());
        
                '''.format(env,day,channel,period_count,period_type,period_day)
                print(insert_sql)
                m=db.do_sql(insert_sql,env)
                print(m)


    def repayWithholdSuccess(self,request):
         try:
             #获取还款的一些基本参数
            request_repay = request.json
            if "item_no" in request_repay.keys():
                item_no = request_repay['item_no']
            if "env" in request_repay.keys():
                env = request_repay['env']
            if "period" in request_repay.keys():
                period = str(request_repay['period'])[1:-1]
            #print("还款期次:",period,type(period))
            if "finished" in request_repay.keys():
                finished = request_repay['finished']
            if "qsq_channel" in request_repay.keys():
                qsq_channel = request_repay['qsq_channel']
            if "channel_channel" in request_repay.keys():
                channel_channel = request_repay['channel_channel']

            # 引入数据库相关方法
            db = executesql.db_connect()

            headers = {'content-type': 'application/json'}

            #先刷一次罚息
            late_url = "http://kong-api-test.kuainiujinke.com/{0}/asset/refreshLateFee;".format(env)
            late_request = RepaySuccessModel.get_refresh_late_fee(item_no)
            RepaySuccessModel.http_request_post(late_request, late_url, headers)
            #然后同步罚息消息到biz
            msg_id_sql = ''' select sendmsg_id from {0}.sendmsg where sendmsg_order_no = ('{1}') and sendmsg_status ='open' '''.format(env, item_no)
            msg_ids = db.select_sql(msg_id_sql)[1]
            if msg_ids:
                 msg_id = msg_ids[0][0]
                 print(msg_id)
                 RepaySuccessModel.http_request_get("http://kong-api-test.kuainiujinke.com/{0}/msg/run?msgId={1}".format(env, msg_id))

            #查询还款金额，sql执行后返回的数据是个元祖
            sql_amount = ''' select sum(`asset_tran_balance_amount`) from {0}.asset_tran where asset_tran_asset_item_no='{1}' and asset_tran_period in ({2}) '''.format(
                 env, item_no, period)
            result_amount=db.select_sql(sql_amount)
            amount = str(result_amount[1][0][0])
            #print("应还金额:",amount,type(amount))
            #查询还款用户的四要素，直接使用加密后的数据
            sql_use = '''
                 select card_acc_num_encrypt,card_acc_id_num_encrypt,card_acc_name_encrypt,card_acc_tel_encrypt from {0}.card_asset
                 left join {0}.card on card_asset_card_no = card_no
                 where card_asset_asset_item_no = '{1}' and card_asset_type = 'repay'
             '''.format(env, item_no)
            result_use = db.select_sql(sql_use)
            use = result_use[1][0]
            #print("还款用户身份证号码:",use[1],type(use[1]))

            #请求还款接口的参数准备
            repay_url = "http://kong-api-test.kuainiujinke.com/{0}/paydayloan/repay/combo-active;".format(env)
            repay_request = RepaySuccessModel.get_combo_active_request(use[0],use[1],use[2],use[3],amount,item_no,amount)
            #发起还款
            repay_result = RepaySuccessModel.http_request_post(repay_request,repay_url,headers)
            print(repay_result)
            if repay_result['code'] != 0:
                return repay_result

            #通过还款结果得到代扣流水号，并使用代扣流水号发起回调
            #因为测试环境有时候mock会被换，感觉用回调保险些，但是要注意拆分代扣可能是两个流水号
            merchant_key1 = repay_result['data']['project_list'][0]['order_no']
            print("代扣流水号:", merchant_key1, type(merchant_key1))

            callback_headers = {'content-type': 'text/plain'}
            callback_url = "http://kong-api-test.kuainiujinke.com/{0}/paysvr/callback;".format(env)
            callback_request = RepaySuccessModel.callback(merchant_key1, finished, qsq_channel)
            RepaySuccessModel.http_request_plain(callback_request, callback_url, callback_headers)

            if len(repay_result['data']['project_list']) > 1:
                 merchant_key2 = repay_result['data']['project_list'][1]['order_no']
                 print("代扣流水号:", merchant_key2, type(merchant_key2))
                 callback_request2 = RepaySuccessModel.callback(merchant_key2, finished, channel_channel)
                 RepaySuccessModel.http_request_plain(callback_request2, callback_url, callback_headers)

            #回调成功后，执行task
            RepaySuccessModel.http_request_get("http://kong-api-test.kuainiujinke.com/{0}/task/run?orderNo={1}".format(env, item_no))
            RepaySuccessModel.http_request_get("http://kong-api-test.kuainiujinke.com/{0}/task/run?orderNo={1}".format(env, merchant_key1))
            RepaySuccessModel.http_request_get("http://kong-api-test.kuainiujinke.com/{0}/task/run?orderNo={1}".format(env, merchant_key2))

         #休息5秒钟后再执行msg，不然msg_id会查询不全
            time.sleep(5)
            msg_id_sql = ''' 
                select sendmsg_id from {0}.sendmsg where sendmsg_order_no in ('{1}','{2}','{3}','{3}') and sendmsg_status ='open' 
                '''.format(env, merchant_key1,merchant_key2,use[1],item_no)
            msg = db.select_sql(msg_id_sql)
            print("msg:", msg, type(msg))
            msg_id = db.select_sql(msg_id_sql)[1]
            if msg_id:
                i = 0
                j = len(msg_id)
                while i < j:
                    RepaySuccessModel.http_request_get("http://kong-api-test.kuainiujinke.com/{0}/msg/run?msgId={1}".format(env,msg_id[i][0]))
                    i = i + 1

         except Exception as e:
             current_app.logger.exception(e)
             return ErrorCode.ERROR_CODE





