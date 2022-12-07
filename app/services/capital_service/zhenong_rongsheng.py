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
        principal_amount, interest_amount, _, _, repayPlanDict = self.__get_trail_amount__()
        principal_amount = float(Decimal(principal_amount / 100).quantize(Decimal("0.00"))),
        principal_amount = principal_amount[0]
        interest_amount = float(Decimal(interest_amount / 100).quantize(Decimal("0.00"))),
        interest_amount = interest_amount[0]
        value = dict(zip(('$.data.data.capital', '$.data.data.interest'),
                         (principal_amount, interest_amount)))
        return self.update_by_json_path(self.trail_url, value, method='post')

    def repay_apply_query_mock(self, withhold, withhold_detail, success_type='success'):
        principal_amount, interest_amount, _, _, _ = self.__get_trail_amount__()
        principal_amount = float(Decimal(principal_amount / 100).quantize(Decimal("0.00"))),
        principal_amount = principal_amount[0]
        interest_amount = float(Decimal(interest_amount / 100).quantize(Decimal("0.00"))),
        interest_amount = interest_amount[0]
        code = 0 if success_type.lower() == 'success' else 90000
        status = 'S' if success_type.lower() == 'success' else 'F'
        value = dict(zip(('$.data.data.applyRepayAmount',
                          '$.data.data.realRepayAmount',
                          '$.data.data.realCapital',
                          '$.data.data.realInterest',
                          '$.data.data.status'), (
            str(principal_amount + interest_amount),
            str(principal_amount + interest_amount),
            str(principal_amount),
            str(interest_amount),
            status, code)))
        return self.update_by_json_path(self.repay_apply_query_url, value, method='post')
