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
        principal_amount = float(Decimal(principal_amount / 100).quantize(Decimal("0.00"))),
        principal_amount = principal_amount[0]
        interest_amount = float(Decimal(interest_amount / 100).quantize(Decimal("0.00"))),
        interest_amount = interest_amount[0]
        principal_amount = principal_amount + 1 if principal_over else principal_amount
        if interest_type == 'less':
            interest_amount = interest_amount - 1
        elif interest_type == 'more':
            interest_amount = interest_amount + 1
        elif interest_type == 'zero':
            interest_amount = 0
        value = dict(zip(('$.data.actualRepayAmount',
                          '$.data.repayPrincipal',
                          '$.data.repayInterest'),
                         (principal_amount + interest_amount, principal_amount, interest_amount)))
        return self.update_by_json_path(self.trail_url, value, method='post')

    def repay_apply_query_mock(self, withhold, withhold_detail, success_type='success'):
        interest_detail = [x.withhold_detail_withhold_amount for x in withhold_detail
                           if x.withhold_detail_type == 'interest']
        principal_detail = [x.withhold_detail_withhold_amount for x in withhold_detail
                            if x.withhold_detail_type == 'principal']
        fee_detail = [x.withhold_detail_withhold_amount for x in withhold_detail if x.withhold_detail_type == 'fee']
        penalty_detail = [x.withhold_detail_withhold_amount for x in withhold_detail if x.withhold_detail_type == 'late']
        principal = reduce(lambda x, y: x + y, principal_detail, 0)
        principal = float(Decimal(principal / 100).quantize(Decimal("0.00")))
        interest = float(Decimal(interest_detail[0] / 100).quantize(Decimal("0.00"))) if interest_detail else 0
        fee_amount = reduce(lambda x, y: x + y, fee_detail, 0)
        fee_amount = float(Decimal(fee_amount / 100).quantize(Decimal("0.00")))
        penalty_amount = reduce(lambda x, y: x + y, penalty_detail, 0)
        penalty_amount = float(Decimal(penalty_amount / 100).quantize(Decimal("0.00")))
        code = "0" if success_type.lower() == 'success' else 100
        status = 'S' if success_type.lower() == 'success' else 'F'
        value = dict(zip(('$.data.actualRepayAmount',
                          '$.data.repayPrincipal',
                          '$.data.repayInterest',
                          '$.data.repayPenaltyAmount',
                          '$.data.status',
                          '$.code'), (
            str(principal + interest),
            str(principal),
            str(interest),
            str(penalty_amount),
            status, code)))
        return self.update_by_json_path(self.repay_apply_query_url, value, method='post')
