import uuid, requests, json
from datetime import datetime
from dateutil.relativedelta import relativedelta
from pprint import pprint

from environment.common.config import Config
from app import db


class WithdrawSuccessGlobalModel(object):
    @classmethod
    def build_asset_info(cls, env, asset_item_no):
        sql = "select task_request_data from global_gbiz%s.task where task_order_no='%s' and " \
              "task_type='AssetImport'" % (env, asset_item_no)
        asset_info = db.session.execute(sql).fetchone()
        asset_info = json.loads(asset_info[0])["data"]["asset"]

        sql = "select * from global_gbiz%s.asset where asset_item_no='%s'" % (env, asset_item_no)
        asset_db = db.session.execute(sql).fetchone()

        pprint(asset_info)
        pprint(asset_db)
        asset = dict()
        asset["asset_item_no"] = asset_item_no
        asset["type"] = "paydayloan"
        asset["sub_type"] = "multiple"
        asset["period_type"] = asset_info["period_type"]
        asset["period_count"] = asset_info["period_count"]
        asset["product_category"] = asset_info["period_day"]
        asset["cmdb_product_number"] = asset_db.asset_cmdb_product_number
        asset["grant_at"] = asset["effect_at"] = asset["actual_grant_at"] = cls.get_date()
        asset["due_at"] = cls.get_date(day=7, fmt="%Y-%m-%d 00:00:00")
        asset["payoff_at"] = cls.get_date(day=8, fmt="%Y-%m-%d 00:00:00")
        asset["from_system"] = asset_info["from_system"]
        asset["status"] = "repay"
        asset["principal_amount"] = round(float(asset_info["amount"]))
        asset["granted_principal_amount"] = round(float(asset_info["amount"]))
        asset["loan_channel"] = asset_info["loan_channel"]
        asset["alias_name"] = ""
        asset["interest_amount"] = asset_db.asset_interest_amount
        asset["fee_amount"] = asset_db.asset_fee_amount
        asset["balance_amount"] = asset_db.asset_balance_amount
        asset["repaid_amount"] = asset_db.asset_repaid_amount
        asset["total_amount"] = asset_db.asset_total_amount
        asset["version"] = str(datetime.now().timestamp()).split('.')[0]
        asset["interest_rate"] = round(float(asset_db.asset_interest_rate), 3)
        asset["charge_type"] = 0
        asset["ref_order_no"] = ""
        asset["ref_order_type"] = ""
        asset["withholding_amount"] = round(float(float(asset_info["amount"]) * 0.2))
        asset["sub_order_type"] = None
        asset["overdue_guarantee_amount"] = 0
        asset["owner"] = asset_db.asset_owner
        asset["from_app"] = asset_db.asset_from_app
        asset["risk_level"] = "1"
        asset["product_name"] = asset_db.asset_product_name
        asset["from_system_name"] = "贷上钱"
        return asset

    @classmethod
    def build_loan_record_info(cls, env, asset_item_no):
        sql = "select * from global_gbiz%s.asset_loan_record where asset_loan_record_asset_item_no='%s'" % (
            env, asset_item_no)
        alr_db = db.session.execute(sql).fetchone()

        loan_record_info = dict()
        loan_record_info["asset_item_no"] = asset_item_no
        loan_record_info["amount"] = alr_db["asset_loan_record_amount"]
        loan_record_info["withholding_amount"] = round(
            float(float(alr_db["asset_loan_record_amount"]) * 0.2))
        loan_record_info["channel"] = alr_db["asset_loan_record_channel"]
        loan_record_info["status"] = 6
        loan_record_info["identifier"] = alr_db["asset_loan_record_identifier"]
        loan_record_info["trade_no"] = alr_db["asset_loan_record_trade_no"]
        loan_record_info["due_bill_no"] = asset_item_no
        loan_record_info["commission_amount"] = None
        loan_record_info["pre_fee_amount"] = None
        loan_record_info["service_fee_amount"] = None
        loan_record_info["is_deleted"] = None
        loan_record_info["finish_at"] = cls.get_date()
        loan_record_info["trans_property"]: None
        loan_record_info["pre_interest"]: None
        loan_record_info["commission_amt_interest"]: None
        loan_record_info["grant_at"] = cls.get_date()
        loan_record_info["push_at"] = cls.get_date()
        return loan_record_info

    @classmethod
    def build_borrower_info(cls, env, asset_item_no):
        sql = "select task_request_data from global_gbiz%s.task where task_order_no='%s' and " \
              "task_type='AssetImport'" % (env, asset_item_no)
        asset_info = db.session.execute(sql).fetchone()
        borrower_info = json.loads(asset_info[0])["data"]["borrower"]
        return borrower_info

    @classmethod
    def build_trans_info(cls, env, asset_item_no):
        sql = "select * from global_gbiz%s.asset_tran where asset_tran_asset_item_no='%s' " \
              "order by asset_tran_type, asset_tran_period" % (env, asset_item_no)
        trans = db.session.execute(sql).fetchall()
        trans_info = list()
        for tran in trans:
            temp = {"asset_item_no": tran.asset_tran_asset_item_no,
                    "type": tran.asset_tran_type,
                    "description": tran.asset_tran_description,
                    "amount": tran.asset_tran_amount,
                    "decrease_amount": tran.asset_tran_decrease_amount,
                    "repaid_amount": tran.asset_tran_repaid_amount,
                    "balance_amount": tran.asset_tran_balance_amount,
                    "total_amount": tran.asset_tran_total_amount,
                    "status": tran.asset_tran_status,
                    "due_at": cls.get_date(day=7, fmt="%Y-%m-%d 00:00:00"),
                    "finish_at": cls.get_date(),
                    "period": tran.asset_tran_period,
                    "late_status": tran.asset_tran_late_status,
                    "remark": tran.asset_tran_remark,
                    "repay_priority": tran.asset_tran_repay_priority,
                    "trade_at": cls.get_date(),
                    "category": tran.asset_tran_category}
            trans_info.append(temp)
        return trans_info

    @classmethod
    def get_calculate_request(cls, asset_info):
        rate_loan_calculate_body = dict()
        rate_loan_calculate_body['from_system'] = "GBIZ"
        rate_loan_calculate_body['key'] = str(uuid.uuid4())
        rate_loan_calculate_body['type'] = "LoanCalculateRepayPlan"
        rate_loan_calculate_body['data'] = dict()
        rate_loan_calculate_body['data']['itemNo'] = asset_info['asset_item_no']
        rate_loan_calculate_body['data']['sign_date'] = datetime.now().strftime(fmt="%Y-%m-%d")
        rate_loan_calculate_body['data']['apply_amount'] = str(asset_info['amount']) + '00'
        rate_loan_calculate_body['data']['period_count'] = asset_info['period_count']
        rate_loan_calculate_body['data']['period_type'] = asset_info['period_type']
        rate_loan_calculate_body['data']['period_term'] = asset_info['product_category']
        rate_loan_calculate_body['data']['product_number'] = asset_info['cmdb_product_number']
        rate_loan_calculate_body['data']['scope'] = asset_info['source_type']
        rate_loan_calculate_body['data']['loan_channel'] = asset_info['loan_channel']
        cmdb_url = Config.CMDB_URL_v6
        header = {"Content-Type": "application/json"}
        resp = requests.post(cmdb_url, data=json.dumps(rate_loan_calculate_body), headers=header, timeout=10).json()
        return resp

    @classmethod
    def get_date(cls, year=0, month=0, day=0, fmt="%Y-%m-%d %H:%M:%S"):
        return (datetime.now() + relativedelta(years=year, months=month, days=day)).strftime(fmt)
