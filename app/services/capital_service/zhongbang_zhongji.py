from decimal import Decimal
from functools import reduce

from app.services.capital_service import BusinessMock


class ZhongbangzhongjiMock(BusinessMock):

    def __init__(self, project, asset, asset_extend, asset_tran_list, period_start, period_end):
        self.channel = 'zhongbang_zhongji'
        super(ZhongbangzhongjiMock, self).__init__(project, asset, asset_extend, asset_tran_list, period_start, period_end)
        self.trail_url = '/zhongbang/zhongbang_zhongji/NormPrpymntTrl'
        self.trail_query_url = ''
        self.repay_plan_url = ''
        self.repay_apply_url = ''
        self.repay_apply_query_url = '/zhongbang/zhongbang_zhongji/NewRpyStsQry'

    def repay_trail_mock(self, status, principal_over=False, interest_type='less'):
        principal_amount, interest_amount, _, _, repayPlanDict = self.__get_trail_amount__()
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
        value = dict(zip(('$.data.result.actual_repay_amount',
                          '$.data.result.repay_principal',
                          '$.data.result.repay_interest'),
                         (principal_amount + interest_amount, principal_amount, interest_amount)))
        return self.update_by_json_path(self.trail_url, value, method='post')

    def repay_apply_query_mock(self, withhold, withhold_detail, success_type='success'):
        interest_detail = [x.withhold_detail_withhold_amount for x in withhold_detail if x.withhold_detail_type == 'interest']
        principal_detail = [x.withhold_detail_withhold_amount for x in withhold_detail if x.withhold_detail_type == 'principal']
        fee_detail = [x.withhold_detail_withhold_amount for x in withhold_detail if x.withhold_detail_type == 'fee']
        principal = reduce(lambda x, y: x + y, principal_detail, 0)
        principal = float(Decimal(principal / 100).quantize(Decimal("0.00")))
        interest = float(Decimal(interest_detail[0] / 100).quantize(Decimal("0.00"))) if interest_detail else 0
        fee_amount = reduce(lambda x, y: x + y, fee_detail, 0)
        fee_amount = float(Decimal(fee_amount / 100).quantize(Decimal("0.00")))
        code = "000000" if success_type.lower() == 'success' else 90000
        status = '1' if success_type.lower() == 'success' else '2'
        value = dict(zip(('$.data.result.actual_repay_amount',
                          '$.data.result.repay_principal',
                          '$.data.result.repay_interest',
                          '$.data.result.repay_status',
                          '$.data.code'), (
            str(principal + interest + fee_amount),
            str(principal),
            str(interest),
            status, code)))
        return self.update_by_json_path(self.repay_apply_query_url, value, method='post')
