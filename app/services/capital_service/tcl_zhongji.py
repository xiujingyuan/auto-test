from decimal import Decimal
from functools import reduce

from app.services.capital_service import BusinessMock


class TclzhongjiMock(BusinessMock):

    def __init__(self, project, asset, asset_extend, asset_tran_list, period_start, period_end):
        self.channel = 'tcl_zhongji'
        super(TclzhongjiMock, self).__init__(project, asset, asset_extend, asset_tran_list, period_start, period_end)
        self.trail_url = '/tcl/tcl_zhongji/S010010Q'
        self.trail_query_url = ''
        self.repay_plan_url = ''
        self.repay_apply_url = ''
        self.repay_apply_query_url = '/tcl/tcl_zhongji/S011600Q'

    def repay_trail_mock(self, status, principal_over=False, interest_type='less'):
        principal_amount, interest_amount, fee_amount, _, _ = self.__get_trail_amount__()
        advance = self.__get_advance_day__()
        principal_amount = principal_amount + 1 if principal_over else principal_amount
        if interest_type == 'less':
            interest_amount = interest_amount - 100
        elif interest_type == 'more':
            interest_amount = interest_amount + 100
        elif interest_type == 'zero':
            interest_amount = 0
        value = dict(zip(('$.data.data.totalAmt', '$.data.data.termAmt', '$.data.data.termInt',
                          '$.data.data.termGuaranteeFee', '$.data.data.termServiceFee'),
                         (self.fen2yuan(principal_amount + interest_amount + fee_amount * advance / 31),
                          self.fen2yuan(principal_amount),
                          self.fen2yuan(interest_amount),
                          self.fen2yuan(fee_amount * (advance - 1) / 31), self.fen2yuan(fee_amount / 31))))
        return self.update_by_json_path(self.trail_url, value, method='post')

    def repay_apply_query_mock(self, withhold, withhold_detail, success_type='success'):
        principal_amount, _, _, _, _ = self.__get_trail_amount__()
        interest_detail = tuple(filter(lambda x: x.withhold_detail_asset_tran_type == 'repayinterest', withhold_detail))
        fee_detail = [x.withhold_detail_withhold_amount for x in withhold_detail if x.withhold_detail_type == 'fee']
        fee_amount = reduce(lambda x, y: x + y, fee_detail, 0)
        interest = interest_detail[0].withhold_detail_withhold_amount if interest_detail else 0
        code = '000000' if success_type.lower() == 'success' else '1000000'
        status = '2' if success_type.lower() == 'success' else '1'
        value = dict(zip(('$.data.data.actualRepayAmt', '$.data.data.actualPaymentPrinAmt',
                          '$.data.data.actualPaymentInterestAmt', '$.data.header.retCode',
                          '$.data.data.status'), (
            self.fen2yuan(principal_amount + interest + fee_amount), self.fen2yuan(principal_amount),
            self.fen2yuan(interest), code, status)))
        return self.update_by_json_path(self.repay_apply_query_url, value, method='post')
