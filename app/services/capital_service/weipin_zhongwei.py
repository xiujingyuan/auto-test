from decimal import Decimal
from functools import reduce

from app.services.capital_service import BusinessMock


class WeipinzhongweiMock(BusinessMock):

    def __init__(self, project, asset, asset_extend, asset_tran_list, period_start, period_end):

        super(WeipinzhongweiMock, self).__init__(project, asset, asset_extend, asset_tran_list, period_start, period_end)
        self.channel = 'weipin_zhongwei'
        self.trail_url = '/zhongzhirong/{0}/repay.apl.trial'.format(self.channel)
        self.trail_query_url = ''
        self.repay_plan_url = '/zhongzhirong/{0}/repayplan.query'.format(self.channel)
        self.repay_apply_url = '/zhongzhirong/{0}/repay.apl'.format(self.channel)
        self.repay_apply_query_url = '/zhongzhirong/{0}/repay.apl.query'.format(self.channel)

    def repay_trail_mock(self, status, principal_over=False, interest_type='less'):
        principal_amount, interest_amount, _, late_amount, repayPlanDict = self.__get_trail_amount__()
        repayPlanList = []
        total_amount = 0
        for period in list(range(self.period_start, self.period_end + 1)):
            interest = repayPlanDict[period]['interest']
            principal = repayPlanDict[period]['principal']
            total_amount += reduce(lambda x, y: x+y, repayPlanDict[period].values(), 0)
            if period == self.period_start:
                if principal_over:
                    principal = principal - 1
                if interest_type == 'less':
                    interest = interest - 1
                elif interest_type == 'more':
                    interest = interest + 1
                elif interest_type == 'zero':
                    interest = 0
            repayPlanList.append({
                "tenor": period,
                "principalAmount": principal,
                "interestAmount": interest,
                "penaltyAmount": repayPlanDict[period]['late'],
                "feeAmount": 0,
                "compountAmount": 0,
                "delqDays": 0
            })
        req_data = {
            "code": 0,
            "message": "成功",
            "data": {
                "respCode": "000000",
                "respMessage": "访问成功",
                "creditAppNo": self.asset.asset_item_no,
                "userId": "16545892470612460068",
                "repaymentList": [
                    {
                        "totalAmount": float(Decimal(total_amount).quantize(Decimal("0.00"))),
                        "preFeeAmount": None,
                        "planList": repayPlanList
                    }]
            }
        }
        return self.update_by_value(self.trail_url, req_data)

    def repay_apply_query_mock(self, withhold, withhold_detail, success_type='PART'):
        principal_amount, interest_amount, fee_amount, late_amount, repayPlanDict = self.__get_trail_amount__()
        success_type == 'SUCCESS'
        repayPlanList = []
        total_amount = 0
        for period in list(range(self.period_start, self.period_end + 1)):
            total_amount += repayPlanDict[period]['principal'] + repayPlanDict[period]['interest'] + \
                            repayPlanDict[period]['late']
            repayPlanList.append({
                "tenor": period,
                "principalAmount": repayPlanDict[period]['principal'],
                "interestAmount": repayPlanDict[period]['interest'],
                "penaltyAmount": repayPlanDict[period]['late'],
                "feeAmount": 0,
                "compountAmount": 0,
                "delqDays": 0
            })
        req_data = {
            "code": 0,
            "message": "成功",
            "data": {
                "respCode": "000000",
                "respMessage": "访问成功",
                "creditAppNo": self.asset.asset_item_no,
                "userId": "16545892470612460068",
                "repaymentAppNo": withhold.withhold_serial_no,
                "paymentSeqNo": self.__create_req_key__(self.asset.asset_item_no, 'CLO'),
                "paymentStatus": "0",
                "failReason": None,
                "completeTime": self.get_date(fmt='%Y%m%d%H%M%S', is_str=True),
                "guaranteeFee": float(Decimal(float(fee_amount / 100)).quantize(Decimal("0.00"))),
                "repaymentList": [
                    {
                        "totalAmount": float(Decimal(total_amount).quantize(Decimal("0.00"))),
                        "preFeeAmount": 0,
                        "planList": repayPlanList
                    }]
            }
        }
        return self.update_by_value(self.repay_apply_query_url, req_data)

    def repay_plan_mock(self):
        principal_amount, interest_amount, fee_amount, _, repayPlanDict = self.__get_trail_amount__()
        repayPlanList = []
        for period in list(range(1, self.asset.asset_period_count + 1)):
            overdue_amount = repayPlanDict[period]["overdue"] * repayPlanDict[period]["principal"] * 0.001
            repayPlanList.append({
                "tenor": period,
                "paymentDueDate": "20221028",
                "payablePrincipal": repayPlanDict[period]["principal"],
                "paymentPrincipal": 0.00,
                "payableInterest": repayPlanDict[period]["interest"],
                "paymentInterest": 0.00,
                "payablePenaltyInterest": overdue_amount,
                "paymentPenaltyInterest": 0.00,
                "payableCompoundInterest": 0.00,
                "paymentCompoundInterest": 0.00,
                "payableFee": 0.00,
                "paymentFee": 0.00,
                "paymentFlag": "2",
                "paymentDate": None,
                "totalAmount": repayPlanDict[period]["principal"] + repayPlanDict[period]["interest"]
                               + overdue_amount,
                "principalAmount": repayPlanDict[period]["principal"],
                "interestAmount": repayPlanDict[period]["interest"],
                "penaltyIntAmount": overdue_amount,
                "compoundAmount": 0,
                "feeAmount": 0.00,
                "exemptAmount": 0.00,
                "waivedAmount": 0,
                "delqDays": repayPlanDict[period]["overdue"]
            })
        req_data = {
            "code": 0,
            "message": "成功",
            "data": {
                "respCode": "000000",
                "respMessage": "访问成功",
                "creditAppNo": self.asset.asset_item_no,
                "userId": "16545887197922460067",
                "planList": repayPlanList
            }
        }
        return self.update_by_value(self.repay_plan_url, req_data)
