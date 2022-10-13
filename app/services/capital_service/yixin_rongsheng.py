from app.services.capital_service import BusinessMock


class YixinrongshengMock(BusinessMock):

    def __init__(self, project, asset, asset_extend, asset_tran_list, period_start, period_end):
        self.channel = 'yixin_rongsheng'
        super(YixinrongshengMock, self).__init__(project, asset, asset_extend, asset_tran_list, period_start, period_end)
        self.trail_url = '/yixin/yixin_rongsheng/calAllAmountInAdvanceSingle'
        self.trail_query_url = ''
        self.repay_plan_url = ''
        self.repay_apply_url = ''
        self.repay_apply_query_url = ''

    def repay_trail_mock(self, status, principal_over=False, interest_type='less'):
        principal_amount, interest_amount, _, _, _ = self.__get_trail_amount__()
        value = dict(zip(('$.data.lnsCurAmt', '$.data.lnsCurInt'),
                         (principal_amount, interest_amount)))
        return self.update_by_json_path(self.trail_url, value, method='post')
