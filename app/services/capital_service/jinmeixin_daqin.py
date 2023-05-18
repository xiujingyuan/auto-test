from functools import reduce

from _decimal import Decimal

from app.services.capital_service import BusinessMock


class JinmeixindaqinMock(BusinessMock):

    def __init__(self, project, asset, asset_extend, asset_tran_list, period_start, period_end):
        super(JinmeixindaqinMock, self).__init__(project, asset, asset_extend, asset_tran_list, period_start, period_end)
        self.channel = 'jinmeixin_daqin'
        self.trail_url = '/chongtian/{0}/repay/calc'.format(self.channel)
        self.trail_query_url = ''
        self.repay_plan_url = ''
        self.repay_apply_url = '/chongtian/{0}/repay/request'.format(self.channel)
        self.repay_apply_query_url = '/chongtian/{0}/repay/queryStatus'.format(self.channel)

    def repay_plan_mock(self):
        pass

    def repay_trail_mock(self, status, principal_over=False, interest_type='less'):
        principal_amount, interest_amount, fee_amount, _, repayPlanDict = self.__get_trail_amount__()
        if principal_over:
            principal_amount = principal_amount - 100
        if interest_type == 'less':
            interest_amount = interest_amount - 100
        elif interest_type == 'more':
            interest_amount = interest_amount + 100
        elif interest_type == 'zero':
            interest_amount = 0
        repayPlanList = []
        for period in list(range(self.period_start, self.period_end + 1)):
            period_interest_amount = interest_amount if period == self.period_start else 0
            fee_amount = repayPlanDict[period]['fee'] if period == self.period_start else 0
            repayPlanList.append({
                "termNo": period,
                "repayDate": self.get_date(is_str=True, fmt="%Y%m%d"),
                "repayAmt": self.fen2yuan(repayPlanDict[period]['principal'] + period_interest_amount + fee_amount),
                "repayPrin": self.fen2yuan(repayPlanDict[period]['principal']),
                "repayInt": self.fen2yuan(period_interest_amount),
                "repayPen": 0,
                "repayFee": self.fen2yuan(fee_amount)
            })

        req_data = {
            "code": "000000",
            "msg": "成功",
            "data": {
                "loanOrderNo": self.asset_extend.asset_extend_val,
                "repayType ": "DO" if self.repay_type == 'normal' else 'PRE',
                "repayTerm": list(range(self.period_start, self.period_end + 1)),
                "repayAmt": self.fen2yuan(principal_amount + interest_amount + fee_amount),
                "repayPrin": self.fen2yuan(principal_amount),
                "repayInt": self.fen2yuan(interest_amount),
                "repayFee": self.fen2yuan(fee_amount),
                "repayPen": 0,
                "bankCardList": [{}],
                "repayPlanList": repayPlanList
            }
        }

        return self.update_by_value(self.trail_url, req_data)

    def repay_trail_query_mock(self):
        pass

    def repay_apply_mock(self):
        pass

    def repay_apply_query_mock(self, withhold, withhold_detail, success_type='PART'):
        repayPlanDict = {}
        for detail in withhold_detail:
            if detail.withhold_detail_period not in repayPlanDict:
                repayPlanDict[detail.withhold_detail_period] = {}
            if detail.withhold_detail_type not in repayPlanDict[detail.withhold_detail_period]:
                repayPlanDict[detail.withhold_detail_period][detail.withhold_detail_type] \
                    = detail.withhold_detail_withhold_amount
            else:
                repayPlanDict[detail.withhold_detail_period][detail.withhold_detail_type] += \
                    detail.withhold_detail_withhold_amount
        repayPlanList = []
        for period in list(range(self.period_start, self.period_end + 1)):
            fee = repayPlanDict[period]['fee'] if success_type == 'SUCCESS' and period == self.period_start else 0
            interest = repayPlanDict[period]['interest'] if 'interest' in repayPlanDict[period] else 0
            principal = repayPlanDict[period]['principal'] if 'principal' in repayPlanDict[period] else 0
            repayPlanList.append({
                "loanOrderNo": self.asset_extend.asset_extend_val,
                "termNo": period,
                "payOrderId": "R103" + self.__create_req_key__(self.asset.asset_item_no),
                "repayStatus": success_type,
                "repayResult": "part",
                "repayAmt": self.fen2yuan(principal + interest + fee),
                "repayPrin": self.fen2yuan(principal),
                "repayInt": self.fen2yuan(interest),
                "repayPen": 0,
                "repayFee": fee,
                "repayTime": self.get_date(is_str=True)
            })
        req_data = {
            "code": "000000",
            "msg": "成功",
            "data": {
                "orderId": withhold.withhold_serial_no,
                "repayStatus": success_type,
                "repayResult": "部分还款成功",
                "failCode": None,
                "repayPlanList": repayPlanList
            }
        }
        self.update_by_value(self.repay_apply_query_url, req_data)