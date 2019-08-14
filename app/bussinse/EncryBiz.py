# -*- coding: utf-8 -*-
# @ProjectName:    gaea-api$
# @Package:        $
# @ClassName:      InitBiz$
# @Description:    描述
# @Author:         Fyi zhang
# @CreateDate:     2019/1/19$ 22:49$
# @UpdateUser:     更新者
# @UpdateDate:     2019/1/19$ 22:49$
# @UpdateRemark:   更新内容
# @Version:        1.0

import requests,json

from app.common.tools.UnSerializer import UnSerializer
from app.common.tools.Serializer import Serializer
from environment.common.config import Config
from flask import current_app
from app.models.ErrorCode import ErrorCode
class EncryBiz(UnSerializer):

    def encry_data(self,request):
        result={}
        try:
            request_dict = request.json
            print(request_dict)
            for key ,value in request_dict.items():
                data = self.generate_data(key,value)
                encry_data = self.reuqest_encrp(data)
                # result[key] = value
                # encry_key = key + '_encry'
                result[key] = encry_data
            return result
        except Exception as e:
            current_app.logger.exception(e)
            return ErrorCode.ERROR_CODE


    def reuqest_encrp(self,data):
        try:
            url = Config.ENCRY_URL
            headers = {'content-type': 'application/json'}
            req = requests.post(url, data=json.dumps(data), headers=headers,timeout=10)
            result = req.json()
            if result['code']==0:
                return result['data'][0]['hash']
            return req.json()
        except Exception as e:
            current_app.logger.exception(e)
            raise str(e)


    def reuqest_de_encrp(self,data):
        try:
            deencry_url = Config.DEENCRY_URL
            headers = {'content-type': 'application/json'}
            print(data, type(data))
            print(json.dumps(data))
            if not isinstance(data, list):
                new_data = [data]
            req = requests.post(deencry_url, data=json.dumps(new_data), headers=headers,timeout=10)
            print(deencry_url, json.dumps(data))
            result = req.json()
            print(result)
            if result['code']==0:
                return result['data']
            return result["message"]
        except Exception as e:
            current_app.logger.exception(e)
            return ErrorCode.ERROR_CODE



    def generate_data(self,type,value):
        if type =="idnum":
            return {
                "type":2,
                "plain":value
            }
        elif type =="mobile":
            return {
                "type":1,
                "plain":value
            }
        elif type =="card_number":
            return {
                "type":3,
                "plain":value
            }
        elif type =="name":
            return {
                "type":4,
                "plain":value
            }
        elif type =="email":
            return {
                "type":5,
                "plain":value
            }
        elif type =="address":
            return {
                "type":6,
                "plain":value
            }

    def de_encry_data(self,request):
        try:
            result={}
            new_result = {}
            request_dict = request.json
            for key ,value in request_dict.items():
                data = self.generate_data_deencry(value)
                encry_data = self.reuqest_de_encrp(data)
                # encry_key = key + '_de_encry'
                result[key] = encry_data
                new_result[key] = encry_data[value] if not isinstance(encry_data, int) else encry_data

            return {"old": result, "new": new_result}
        except Exception as e:
            current_app.logger.exception(e)
            return "{0}:{1} get error. {2}".format(key, value, encry_data)

    def generate_data_deencry(self,value):
        return {
            "hash":value
        }
