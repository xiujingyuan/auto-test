# -*- coding: utf-8 -*-
# @Title: CaseBiz
# @ProjectName gaea-api
# @Description: TODO
# @author fyi zhang
# @date 2019/1/19 22:29

import app.common.config.config as config
import smtplib
from app import db
from flask import current_app
from app.common.tools.UnSerializer import UnSerializer
from app.common.tools.Serializer import Serializer
from app.models.PrevModel import PrevModel
from app.models.CommonToolsModel import CommonToolsModel
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
        try:
            smtp = smtplib.SMTP()
            smtp.connect('smtp.qq.com')
            smtp.login(sender, sender_passwd)
            print(to_email)
            smtp.sendmail(sender, to_email, message.as_string())
            print("发送邮件成功！！！")
            smtp.quit()
        except smtplib.SMTPException as e:
            print(str(e))
            print("发送邮件失败！！！")
            return 9999


