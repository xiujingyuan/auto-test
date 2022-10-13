from decimal import Decimal

from app.services.capital_service import BusinessMock


class ZhongkehegangMock(BusinessMock):

    def __init__(self, project, asset, asset_extend, asset_tran_list, period_start, period_end):
        self.channel = 'zhongke_hegang'
        super(ZhongkehegangMock, self).__init__(project, asset, asset_extend, asset_tran_list, period_start, period_end)
        self.trail_url = '/hegang/repayTrialQuery/{0}'.format(asset.asset_product_code)
        self.trail_query_url = ''
        self.repay_plan_url = ''
        self.repay_apply_url = '/hegang/repayQuery/{0}'.format(asset.asset_product_code)
        self.repay_apply_query_url = ''

    def repay_trail_mock(self, status, principal_over=False, interest_type='less'):
        principal_amount, interest_amount, _, late_amount, repayPlanDict = self.__get_trail_amount__()
        principal = float(Decimal(float(principal_amount / 100)).quantize(Decimal("0.00")))
        interest = float(Decimal(float(interest_amount / 100)).quantize(Decimal("0.00")))
        value = dict(zip(('$.tradeCapital', '$.tradeInt', '$.tradeAmt'),
                         (principal, interest, principal + interest)))
        trail_url = '/hegang/repayTrialQuery/{0}'.format(self.asset.asset_product_code)
        return self.update_by_json_path(trail_url, value, method='post')

    def repay_apply_query_mock(self, withhold, withhold_detail, success_type='PART'):
        total = 0
        interest = 0
        principal = 0
        for item in self.withhold:
            withhold_amount = float(
                Decimal(float(item.withhold_detail_withhold_amount / 100)).quantize(Decimal("0.00")))
            if item.withhold_detail_type == 'principal':
                principal += withhold_amount
            elif item.withhold_detail_type == 'interest':
                interest += withhold_amount
            total += withhold_amount
        total = float(Decimal(total).quantize(Decimal("0.00")))
        value = dict(zip(('$.rpyTotalAmt', '$.prinAmt', '$.intAmt'), (total, principal, interest)))
        return self.update_by_json_path(self.repay_apply_query_url, value, method='post')
