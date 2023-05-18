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
        principal_amount, interest_amount, _, _, _ = self.__get_trail_amount__()
        principal_amount = principal_amount + 100 if principal_over else principal_amount
        if interest_type == 'less':
            interest_amount = interest_amount - 100
        elif interest_type == 'more':
            interest_amount = interest_amount + 100
        elif interest_type == 'zero':
            interest_amount = 0
        value = dict(zip(('$.data.result.actual_repay_amount',
                          '$.data.result.repay_principal',
                          '$.data.result.repay_interest'),
                         (self.fen2yuan(principal_amount + interest_amount),
                          self.fen2yuan(principal_amount),
                          self.fen2yuan(interest_amount))))
        return self.update_by_json_path(self.trail_url, value, method='post')

    def repay_apply_query_mock(self, withhold, withhold_detail, success_type='success'):
        interest_detail = [x.withhold_detail_withhold_amount for x in withhold_detail if x.withhold_detail_type == 'interest']
        principal_detail = [x.withhold_detail_withhold_amount for x in withhold_detail if x.withhold_detail_type == 'principal']
        principal = reduce(lambda x, y: x + y, principal_detail, 0)
        interest = interest_detail[0] if interest_detail else 0
        code = "000000" if success_type.lower() == 'success' else 90000
        status = '1' if success_type.lower() == 'success' else '2'
        value = dict(zip(('$.data.result.actual_repay_amount',
                          '$.data.result.repay_principal',
                          '$.data.result.repay_interest',
                          '$.data.result.repay_status',
                          '$.data.code'), (
            self.fen2yuan(principal + interest),
            self.fen2yuan(principal),
            self.fen2yuan(interest),
            status, code)))
        return self.update_by_json_path(self.repay_apply_query_url, value, method='post')
