from decimal import Decimal
from functools import reduce

from app.services.capital_service import BusinessMock


class DaxinganlingzhongyiMock(BusinessMock):

    def __init__(self, project, asset, asset_extend, asset_tran_list, period_start, period_end):
        self.channel = 'daxinganling_zhongyi'
        super(DaxinganlingzhongyiMock, self).__init__(project, asset, asset_extend, asset_tran_list, period_start, period_end)
        self.trail_url = '/daxinganling_zhongyi/v2/query/trial/early_settlement'
        self.trail_query_url = ''
        self.repay_plan_url = ''
        self.repay_apply_url = ''
        self.repay_apply_query_url = '/daxinganling_zhongyi/v2/query/queryDeductionResult'

    def repay_trail_mock(self, status, principal_over=False, interest_type='less'):
        principal_amount, interest_amount, _, _, repayPlanDict = self.__get_trail_amount__()
        principal_amount = principal_amount + 1 if principal_over else principal_amount
        if interest_type == 'less':
            interest_amount = interest_amount - 1
        elif interest_type == 'more':
            interest_amount = interest_amount + 1
        elif interest_type == 'zero':
            interest_amount = 0
        value = dict(zip(('$.data.residualPrincipal', '$.data.settleAmount'),
                         (principal_amount, principal_amount + interest_amount)))
        return self.update_by_json_path(self.trail_url, value, method='post')

    def repay_apply_query_mock(self, withhold, withhold_detail, success_type='success'):
        interest_detail = [x.withhold_detail_withhold_amount for x in withhold_detail if
                           x.withhold_detail_type == 'interest']
        principal_detail = [x.withhold_detail_withhold_amount for x in withhold_detail if
                            x.withhold_detail_type == 'principal']
        principal = reduce(lambda x, y: x + y, principal_detail, 0)
        interest = interest_detail[0] if interest_detail else 0
        code = 2000 if success_type.lower() == 'success' else 30000
        value = dict(zip(('$.data[0].deductionSerialNo', '$.data[0].state', '$.data[0].principal',
                          '$.data[0].interest', '$.code'),
                         (withhold.withhold_serial_no, success_type, principal, interest, code)))
        return self.update_by_json_path(self.repay_apply_query_url, value, method='post')
