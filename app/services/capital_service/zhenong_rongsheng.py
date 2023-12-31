from decimal import Decimal

from app.services.capital_service import BusinessMock


class ZhenongrongshengMock(BusinessMock):

    def __init__(self, project, asset, asset_extend, asset_tran_list, period_start, period_end):
        self.channel = 'zhenong_rongsheng'
        super(ZhenongrongshengMock, self).__init__(project, asset, asset_extend, asset_tran_list, period_start, period_end)
        self.trail_url = '/zhenong/zhenong_rongsheng/repay/query'
        self.trail_query_url = ''
        self.repay_plan_url = ''
        self.repay_apply_url = ''
        self.repay_apply_query_url = '/zhenong/zhenong_rongsheng/repay/result/query'

    def repay_trail_mock(self, status, principal_over=False, interest_type='less'):
        principal_amount, interest_amount, _, _, _ = self.__get_trail_amount__()
        principal_amount = principal_amount + 100 if principal_over else principal_amount
        if interest_type == 'less':
            interest_amount = interest_amount - 100
        elif interest_type == 'more':
            interest_amount = interest_amount + 100
        elif interest_type == 'zero':
            interest_amount = 0
        value = dict(zip(('$.data.data.capital', '$.data.data.interest'),
                         (self.fen2yuan(principal_amount), self.fen2yuan(interest_amount))))
        return self.update_by_json_path(self.trail_url, value, method='post')

    def repay_apply_query_mock(self, withhold, withhold_detail, success_type='success'):
        principal_amount, _, _, _, _ = self.__get_trail_amount__()
        principal_amount = float(Decimal(principal_amount / 100).quantize(Decimal("0.00"))),
        principal_amount = principal_amount[0]
        interest_detail = tuple(filter(lambda x: x.withhold_detail_asset_tran_type == 'repayinterest', withhold_detail))
        interest = float(Decimal(interest_detail[0].withhold_detail_withhold_amount / 100).quantize(Decimal("0.00"))) \
            if interest_detail else 0
        code = 0 if success_type.lower() == 'success' else 90000
        status = 'S' if success_type.lower() == 'success' else 'F'
        value = dict(zip(('$.data.data.applyRepayAmount',
                          '$.data.data.realRepayAmount',
                          '$.data.data.realCapital',
                          '$.data.data.realInterest',
                          '$.data.data.status'), (
            str(principal_amount + interest),
            str(principal_amount + interest),
            str(principal_amount),
            str(interest),
            status, code)))
        return self.update_by_json_path(self.repay_apply_query_url, value, method='post')
