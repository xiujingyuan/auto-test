from decimal import Decimal
from functools import reduce

from app.services.capital_service import BusinessMock


class MengshangzhongyiMock(BusinessMock):

    def __init__(self, project, asset, asset_extend, asset_tran_list, period_start, period_end):
        self.channel = 'mengshang_zhongyi'
        super(MengshangzhongyiMock, self).__init__(project, asset, asset_extend, asset_tran_list, period_start, period_end)
        self.trail_url = '/mengshang/mengshang_zhongyi/repayTrial'
        self.trail_query_url = ''
        self.repay_plan_url = ''
        self.repay_apply_url = ''
        self.repay_apply_query_url = '/mengshang/mengshang_zhongyi/queryDeduction'

    def repay_trail_mock(self, status, principal_over=False, interest_type='less'):
        principal_amount, interest_amount, _, _, _ = self.__get_trail_amount__()
        principal_amount = principal_amount + 1 if principal_over else principal_amount
        if interest_type == 'less':
            interest_amount = interest_amount - 100
        elif interest_type == 'more':
            interest_amount = interest_amount + 100
        elif interest_type == 'zero':
            interest_amount = 0
        value = dict(zip(('$.data.principal', '$.data.interest'),
                         (self.fen2yuan(principal_amount),
                          self.fen2yuan(interest_amount))))
        return self.update_by_json_path(self.trail_url, value, method='post')

    def repay_apply_query_mock(self, withhold, withhold_detail, success_type='success'):
        principal_amount, _, _, _, _ = self.__get_trail_amount__()
        interest_detail = tuple(filter(lambda x: x.withhold_detail_asset_tran_type == 'repayinterest', withhold_detail))
        fee_detail = tuple(filter(lambda x: x.withhold_detail_asset_tran_type in ('consult', 'reserve'), withhold_detail))
        interest = reduce(lambda x, y: x+y, [x.withhold_detail_withhold_amount for x in interest_detail], 0)
        fee = reduce(lambda x, y: x+y, [x.withhold_detail_withhold_amount for x in fee_detail], 0)
        code = 0 if success_type.lower() == 'success' else 90000
        status = '0000' if success_type.lower() == 'success' else '1000'
        value = dict(zip(('$.data.repayInfos[0].repayPrincipal', '$.data.repayInfos[0].repayInterest',
                          '$.data.repayInfos[0].repayGuaranteeFee', '$.data.respcd',
                          '$.data.repaySucTime'), (
            self.fen2yuan(principal_amount), self.fen2yuan(interest), self.fen2yuan(fee),
            status, self.get_date(fmt='%Y%m%d%H%M%S', is_str=True))))
        return self.update_by_json_path(self.repay_apply_query_url, value, method='post')
