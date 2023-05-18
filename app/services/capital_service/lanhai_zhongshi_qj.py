from decimal import Decimal

from app.services.capital_service import BusinessMock


class LanhaizhongshiqjMock(BusinessMock):

    def __init__(self, project, asset, asset_extend, asset_tran_list, period_start, period_end):
        self.channel = 'lanhai_zhongshi_qj'
        super(LanhaizhongshiqjMock, self).__init__(project, asset, asset_extend, asset_tran_list,
                                                   period_start, period_end)
        self.trail_url = '/qingjia/lanhai_zhongshi_qj/repayTrial'
        self.trail_query_url = ''
        self.repay_plan_url = ''
        self.repay_apply_url = ''
        self.repay_apply_query_url = '/qingjia/lanhai_zhongshi_qj/repayResultQuery'

    def repay_trail_mock(self, status, principal_over=False, interest_type='less'):
        principal_amount, interest_amount, _, _, _ = self.__get_trail_amount__()
        principal_amount = principal_amount + 100 if principal_over else principal_amount
        if interest_type == 'less':
            interest_amount = interest_amount - 100
        elif interest_type == 'more':
            interest_amount = interest_amount + 100
        elif interest_type == 'zero':
            interest_amount = 0
        other = {}
        for at in self.asset_tran_list:
            if at.asset_tran_period == self.period_start and at.asset_tran_category == 'fee':
                other[at.asset_tran_type] = at.asset_tran_balance_amount - 100
            continue
        value = dict(zip(('$.data.repaytotal', '$.data.repaycapital', '$.data.repayinterest',
                          '$.data.repayguarantFee', '$.data.repaydeductFee'),
                         (self.fen2yuan(principal_amount + interest_amount + other['guarantee'] + other['technical_service']),
                          self.fen2yuan(principal_amount),
                          self.fen2yuan(interest_amount),
                          self.fen2yuan(other['guarantee']),
                          self.fen2yuan(other['technical_service']))))
        return self.update_by_json_path(self.trail_url, value, method='post')

    def repay_apply_query_mock(self, withhold, withhold_detail, success_type='success'):
        principal_amount, _, _, _, _ = self.__get_trail_amount__()
        principal_amount = float(Decimal(principal_amount / 100).quantize(Decimal("0.00"))),
        principal_amount = principal_amount[0]
        interest_detail = tuple(filter(lambda x: x.withhold_detail_asset_tran_type == 'repayinterest', withhold_detail))
        guarantee_detail = tuple(filter(lambda x: x.withhold_detail_asset_tran_type == 'guarantee', withhold_detail))
        technical_service_detail = tuple(filter(lambda x: x.withhold_detail_asset_tran_type == 'technical_service',
                                                withhold_detail))
        interest = float(Decimal(interest_detail[0].withhold_detail_withhold_amount / 100).quantize(Decimal("0.00"))) \
            if interest_detail else 0
        guarantee = float(Decimal(
            guarantee_detail[0].withhold_detail_withhold_amount / 100).quantize(Decimal("0.00"))) \
            if interest_detail else 0
        technical_service = float(Decimal(
            technical_service_detail[0].withhold_detail_withhold_amount / 100).quantize(Decimal("0.00"))) \
            if interest_detail else 0
        code = 0 if success_type.lower() == 'success' else 90000
        status = '000000' if success_type.lower() == 'success' else '000001'
        value = dict(zip(('$.data.amount', '$.data.errocode'),
                         (principal_amount + interest + guarantee + technical_service, status)))
        return self.update_by_json_path(self.repay_apply_query_url, value, method='post')
