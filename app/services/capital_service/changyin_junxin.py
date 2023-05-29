from decimal import Decimal

from app.services.capital_service import BusinessMock


class ChangyinjunxinMock(BusinessMock):

    def __init__(self, project, asset, asset_extend, asset_tran_list, period_start, period_end):
        self.channel = 'changyin_junxin'
        super(ChangyinjunxinMock, self).__init__(project, asset, asset_extend, asset_tran_list, period_start, period_end)
        self.trail_url = '/changyin/changyin_junxin/api/repayment/trial'
        self.trail_query_url = ''
        self.repay_plan_url = ''
        self.repay_apply_url = ''
        self.repay_apply_query_url = '/changyin/changyin_junxin/api/repayment/query'

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
        value = dict(zip(('$.body.totalAmt', '$.body.psRemPrcp', '$.body.odPrcpAmt'),
                         (principal_amount + interest_amount, principal_amount, interest_amount)))
        return self.update_by_json_path(self.trail_url, value, method='post')

    def repay_apply_query_mock(self, withhold, withhold_detail, success_type='success'):
        principal_amount, _, _, _, _ = self.__get_trail_amount__()
        interest_detail = tuple(filter(lambda x: x.withhold_detail_asset_tran_type == 'repayinterest', withhold_detail))
        interest = interest_detail[0].withhold_detail_withhold_amount if interest_detail else 0
        code = 0 if success_type.lower() == 'success' else 90000
        status = '01' if success_type.lower() == 'success' else '02'
        value = dict(zip(('$.body.applyRepayAmt', '$.body.dealRepayAmt', '$.body.billStatus'), (
            self.fen2yuan(principal_amount + interest), self.fen2yuan(principal_amount + interest),
            status)))
        return self.update_by_json_path(self.repay_apply_query_url, value, method='post')
