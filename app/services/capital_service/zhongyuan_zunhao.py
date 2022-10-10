
from app.services.capital_service import BusinessMock


class ZhongyuanzunhaoMock(BusinessMock):

    def __init__(self, project, asset, asset_extend, asset_tran_list, period_start, period_end):
        super(ZhongyuanzunhaoMock, self).__init__(project, asset, asset_extend, asset_tran_list, period_start, period_end)
        self.channel = 'zhongyuan_zunhao'
        self.trail_url = '/zhongzhirong/zhongyuan_zunhao/repayTrial'
        self.trail_query_url = ''
        self.repay_plan_url = ''
        self.repay_apply_url = ''
        self.repay_apply_query_url = ''

    def repay_trail_mock(self, status, principal_over=False, interest_type='less'):
        principal_amount, interest_amount, _, _, _ = self.__get_trail_amount__()
        value = dict(zip(('$.data.totalRepayAmt', '$.data.totalPlanamt',
                          '$.data.totalPsPrcpAmt', '$.data.totalPsNormInt'), (
                             principal_amount + interest_amount, principal_amount + interest_amount,
                             principal_amount,
                             interest_amount)))
        return self.update_by_json_path(self.trail_url, value, method='post')
