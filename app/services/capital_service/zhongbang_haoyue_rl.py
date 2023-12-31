from decimal import Decimal
from functools import reduce

from app.services.capital_service import BusinessMock


class ZhongbanghaoyuerlMock(BusinessMock):

    def __init__(self, project, asset, asset_extend, asset_tran_list, period_start, period_end):
        self.channel = 'zhongbang_haoyue_rl'
        super(ZhongbanghaoyuerlMock, self).__init__(project, asset, asset_extend, asset_tran_list, period_start,
                                                    period_end)
        self.trail_url = '/runlou/zhongbang_haoyue_rl/loan.zb.assis.repayment.trial.query'
        self.trail_query_url = ''
        self.repay_plan_url = '/runlou/zhongbang_haoyue_rl/loan.zb.assis.repayment.plan.query'
        self.repay_apply_url = ''
        self.repay_apply_query_url = '/runlou/zhongbang_haoyue_rl/loan.zb.assis.repayment.result.query'

    def repay_trail_mock(self, status, principal_over=False, interest_type='less'):
        principal_amount, interest_amount, _, _, _ = self.__get_trail_amount__()
        principal_amount = principal_amount + 100 if principal_over else principal_amount
        if interest_type == 'less':
            interest_amount = interest_amount - 100
        elif interest_type == 'more':
            interest_amount = interest_amount + 100
        elif interest_type == 'zero':
            interest_amount = 0
        value = dict(zip(('$.data.actualRepayAmount',
                          '$.data.repayPrincipal',
                          '$.data.repayInterest'),
                         (self.fen2yuan(principal_amount + interest_amount),
                          self.fen2yuan(principal_amount),
                          self.fen2yuan(interest_amount))))
        return self.update_by_json_path(self.trail_url, value, method='post')

    def repay_apply_query_mock(self, withhold, withhold_detail, success_type='success'):
        interest_detail = [x.withhold_detail_withhold_amount for x in withhold_detail
                           if x.withhold_detail_type == 'interest']
        principal_detail = [x.withhold_detail_withhold_amount for x in withhold_detail
                            if x.withhold_detail_type == 'principal']
        penalty_detail = [x.withhold_detail_withhold_amount for x in withhold_detail if x.withhold_detail_type == 'late']
        principal = reduce(lambda x, y: x + y, principal_detail, 0)
        interest = interest_detail[0] if interest_detail else 0
        penalty_amount = reduce(lambda x, y: x + y, penalty_detail, 0)
        code = "0"
        status = 'S' if success_type.lower() == 'success' else 'F'
        value = dict(zip(('$.data.actualRepayAmount',
                          '$.data.repayPrincipal',
                          '$.data.repayInterest',
                          '$.data.repayPenaltyAmount',
                          '$.data.status',
                          '$.code'), (
            self.fen2yuan(principal + interest + penalty_amount),
            self.fen2yuan(principal),
            self.fen2yuan(interest),
            self.fen2yuan(penalty_amount),
            status, code)))
        return self.update_by_json_path(self.repay_apply_query_url, value, method='post')

    def repay_plan_mock(self):
        principal_amount, interest_amount, fee_amount, _, repayPlanDict = self.__get_trail_amount__()
        repayPlanList = []
        for period in list(range(1, self.asset.asset_period_count + 1)):
            overdue_amount = float(Decimal(
                repayPlanDict[period]["overdue"] * repayPlanDict[period]["principal"] * 0.001).quantize(
                Decimal("0.00")))
            repayPlanList.append(
                {
                    "termNo": period,
                    "repayDate": "2023-04-05",
                    "principalAmount": repayPlanDict[period]["principal"],
                    "interestAmount": repayPlanDict[period]["interest"],
                    "penaltyAmount": overdue_amount,
                    "paidPrincipal": "0",
                    "paidInterest": "0",
                    "paidPenaltyAmount": "0",
                    "intefine": "0",
                    "paidIntefine": "0",
                    "isOverdue": "1" if overdue_amount else "0"
                })
        req_data = {
            "code": "0",
            "message": "Success",
            "data": {
                "status": "S",
                "repayPlan": repayPlanList
            }
        }
        return self.update_by_value(self.repay_plan_url, req_data)


