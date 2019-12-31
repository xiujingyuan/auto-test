import traceback
import uuid,requests,json
from flask import current_app

class RepaySuccessModel(object):

    #还款接口
    @classmethod
    def get_combo_active_request(cls,card_num,card_user_id,card_user_name,card_user_phone,total_amount,project_num,amount):
        guid = str(uuid.uuid4())
        return {
                "type": "PaydayloanComboActiveRepay",
                "key": guid,
                "from_system": "DSQ",
                "data": {
                    "card_num": card_num,
                    "card_user_id": card_user_id,
                    "card_user_name": card_user_name,
                    "card_user_phone": card_user_phone,
                    "card_num_encrypt": card_num,
                    "card_user_id_encrypt": card_user_id,
                    "card_user_name_encrypt": card_user_name,
                    "card_user_phone_encrypt": card_user_phone,
                    "total_amount": total_amount,
                    "project_list": [
                        {
                            "project_num": project_num,
                            "amount": amount,
                            "priority": 1,
                            "coupon_num": "",
                            "coupon_amount": 0
                        }
                    ],
                    "order_no": "",
                    "verify_code": "999999",
                    "verify_seq": "c001124fb6608"
                }
        }

    #回调接口
    @classmethod
    def callback(cls,merchant_key,finished,channel):
        return {
            "sign":"6401cd046b5ae44ef208b8ea82d398ab",
            "merchant_key":merchant_key,
            "channel_key":merchant_key,
            "transaction_status":2,
            "finished_at":finished,
            "channel_name":channel,
            "form_system":"paysvr"
        }

    #刷罚息
    @classmethod
    def get_refresh_late_fee(cls,asset_item_no):
        guid = str(uuid.uuid4())
        return {
            "from_system":"Biz",
            "type":"RbizRefreshLateInterest",
            "key":guid,
            "data":{
                "asset_item_no":asset_item_no
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
            raise str(e)


    @classmethod
    def http_request_plain(cls,data,url,headers):
        try:
            req = requests.post(url, data, headers,timeout=10)
            current_app.logger.info(req)
            result = req.content
            current_app.logger.info(url+str(result))
            return result
        except Exception as e:
            current_app.logger.info(traceback.format_exc())
            current_app.logger.exception(e)
            raise str(e)


    @classmethod
    def http_request_get(cls,url):
        try:
            req = requests.get(url,timeout=10)
            current_app.logger.info(req)
            result = req.json()
            current_app.logger.info(url+str(result))
            return result
        except Exception as e:
            current_app.logger.info(traceback.format_exc())
            current_app.logger.exception(e)
            raise str(e)





