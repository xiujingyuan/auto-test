from decimal import Decimal

from app.services.capital_service.jinmeixin_daqin import JinmeixindaqinMock


class WeipinhanchenjfMock(JinmeixindaqinMock):

    def __init__(self, project, asset, asset_extend, asset_tran_list, period_start, period_end):
        super(WeipinhanchenjfMock, self).__init__(project, asset, asset_extend, asset_tran_list,
                                                     period_start, period_end)
        self.channel = 'weipin_hanchen_jf'
        self.trail_url = '/jingfa/weipin_hanchen_jf/kuainiu/apply/repayTrial'
        self.trail_query_url = ''
        self.repay_plan_url = '/jingfa/weipin_hanchen_jf/kuainiu/query/repayPlanQuery'
        self.repay_apply_url = '/jingfa/weipin_hanchen_jf/kuainiu/apply/repayApply'
        self.repay_apply_query_url = '/jingfa/weipin_hanchen_jf/kuainiu/query/repayResultQuery'

    def repay_trail_mock(self, status, principal_over=False, interest_type='less'):
        principal_amount, interest_amount, _, late_amount, repayPlanDict = self.__get_trail_amount__()
        if interest_type == 'less':
            interest_amount -= 100
        elif interest_type == 'more':
            interest_amount += 100
        elif interest_type == "zero":
            interest_amount = 0
        value = dict(zip(('$.data.data.repaymentPrinciple', '$.data.data.repaymentInterest',
                          '$.data.data.repaymentTotalAmt', '$.data.data.repaymentDefaultInterest'), (
                             principal_amount,
                             interest_amount,
                             interest_amount + principal_amount, repayPlanDict[0]['overdue'])))
        return self.update_by_json_path(self.trail_url, value, method='post')

    def repay_apply_query_mock(self, withhold, withhold_detail, success_type='PART'):
        principal_amount, interest_amount, fee_amount, late_amount, _ = self.__get_trail_amount__()
        code = '1' if success_type.lower() == 'success' else '2'
        period = min(list(map(lambda x: x.withhold_detail_period, withhold_detail)))
        value = dict(zip(('$.data.data.repayList[0].loanNo', '$.data.data.repayList[0].period',
                          '$.data.data.repayList[0].repayDate', '$.data.data.repayList[0].repaymentInterest',
                          '$.data.data.repayList[0].repaymentPrinciple',
                          '$.data.data.repayList[0].repaymentDefaultInterest',
                          '$.data.data.repayList[0].repaymentTotalAmt',
                          '$.data.data.repayList[0].status'),
                          (self.asset.asset_due_bill_no, period, self.get_date(is_str=True, fmt='%Y%m%d'),
                           interest_amount,
                           principal_amount, late_amount, withhold.withhold_amount, code)))
        return self.update_by_json_path(self.repay_apply_query_url, value, method='post')

    def repay_plan_mock(self):
        principal_amount, interest_amount, fee_amount, _, repayPlanDict = self.__get_trail_amount__()
        repayPlanList = []
        for period in list(range(1, self.asset.asset_period_count + 1)):
            overdue_amount = int(repayPlanDict[period]["overdue"] * repayPlanDict[period]["principal"] * 0.001)
            total_amount = repayPlanDict[period]['principal'] + repayPlanDict[period]['interest'] + overdue_amount
            repayPlanList.append(
                {
                    "preRepayPrinciple": repayPlanDict[period]['principal'],
                    "preTotalAmt": total_amount,
                    "preRepayDate": "20291201",
                    "preRepayInterest": repayPlanDict[period]['interest'],
                    "preDefaultInterest": overdue_amount,
                    "currentPeriod": period
                })
        req_data = {
            "code": 0,
            "message": "success",
            "data": {
                "code": "000000",
                "data": {
                    "loanDate": "20291101",
                    "periods": 12,
                    "repayPlans": repayPlanList
                },
                "message": "请求成功"
            }
        }
        return self.update_by_json_path(self.repay_plan_url, req_data, method='post')
