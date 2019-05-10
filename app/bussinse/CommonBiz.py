# -*- coding: utf-8 -*-
# @Title: CaseBiz
# @ProjectName gaea-api
# @Description: TODO
# @author fyi zhang
# @date 2019/1/19 22:29

import app.common.config.config as config
import smtplib,json
from app import db
from flask import current_app
from app.common.tools.UnSerializer import UnSerializer
from app.common.tools.Serializer import Serializer
from app.models.PrevModel import PrevModel
from app.models.CommonToolsModel import CommonToolsModel
from app.models.CapitalPlanModel import CapitalPlanModel
from app.models.WithdrawSuccessModel import WithdrawSuccessModel
from email.header import Header
from email.mime.text import MIMEText



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
            return 9999
        #finally:
            #db.session.close()

    def get_common_tools(self):
        try:
            temp = db.session.query(CommonToolsModel).all()
            result = CommonToolsModel.serialize_list(temp)
        except Exception as e:
            current_app.logger.exception(e)
            db.session.rollback()
            return 9999
        finally:
            return result
            #db.session.close()

    def sendMail(self,request):
        try:
            request_json = request.json
            to_email = request_json['to_mail'].split(";")

            content = request_json['content']
            #to_cc = request_json['to_cc']
            sender = '634586189@qq.com'
            sender_mail = 'p_scm@kuainiugroup.com'
            sender_passwd = 'ftlhypyhtcrjbddh'
            mail_title = request_json['mail_title']
            message = MIMEText(content,'html','utf-8')
            message['From'] = Header(sender_mail, 'utf-8')
            message['To'] = Header(','.join(to_email), 'utf-8')
            message['Subject'] =Header(mail_title, 'utf-8')
            current_app.logger.info(to_email)
            smtp = smtplib.SMTP_SSL(host='smtp.qq.com')
            smtp.connect(host='smtp.qq.com',port=465)
            smtp.login(sender, sender_passwd)
            current_app.logger.info(to_email)
            print(to_email)
            smtp.sendmail(sender, to_email, message.as_string())
            print("发送邮件成功！！！")
            smtp.quit()
        except Exception as e:
            current_app.logger.exception(e)
            print("发送邮件失败！！！")
            return 9999

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
            if 'call_back' in request_json.keys():
                interest_rate = request_json['interest_rate']

            cmdb_url,cmdb_request = CapitalPlanModel.get_calculate_request(product_name,principal_amount,period_count,sign_date)
            print(cmdb_request)
            headers ={'content-type': 'application/json'}
            result = CapitalPlanModel.http_request_post(cmdb_request,cmdb_url,headers)
            params = CapitalPlanModel.build_all_params(channel,item_no,int(period_count),int(period),sign_date,principal_amount,product_name,result,fee_rate,interest_rate)
            urls = call_back.split(";")
            for url in urls:
                 CapitalPlanModel.http_request_post(params,url,headers)
            return params
        except Exception as e:
            current_app.logger.exception(e)
            return 9999

    def withdrawSuccess(self,request):
        try:
            request_json = request.json
            request_body = request_json['request_body'].replace("'",'"').replace('None','null')
            request_body = json.loads(request_body)
            call_back = request_json['call_back']
            params = WithdrawSuccessModel.build_all_params(request_body)
            urls = call_back.split(";")
            for url in urls:
                headers ={'content-type': 'application/json'}
                WithdrawSuccessModel.http_request_post(params,url,headers)
            return params
        except Exception as e:
            current_app.logger.exception(e)
            return 9999
