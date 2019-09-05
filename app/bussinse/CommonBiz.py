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
from email.header import Header
from email.mime.text import MIMEText
from app.models.ErrorCode import ErrorCode



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
            defualt_capital ="http://kong-api-test.kuainiujinke.com/{0}/capital-asset/asset-loan;http://kong-api-test.kuainiujinke.com/{1}/capital-asset/grant;".format(env[1:],'r'+env[1:])
            cmdb_url,cmdb_request = CapitalPlanModel.get_calculate_request(product_name,principal_amount,period_count,sign_date)
            print(cmdb_request)
            headers ={'content-type': 'application/json'}
            result = CapitalPlanModel.http_request_post(cmdb_request,cmdb_url,headers)
            params = CapitalPlanModel.build_all_params(channel,item_no,int(period_count),int(period),sign_date,principal_amount,product_name,result,fee_rate,interest_rate)
            if isinstance(params,str):
                # return "汇率编号已经失效，无法生成资方还款计划"
                return result["message"] if "message" in result else "汇率编号已经失效，无法生成资方还款计划"
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



