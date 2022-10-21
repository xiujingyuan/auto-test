from app.services.capital_service.jinmeixin_daqin import JinmeixindaqinMock


class JinmeixinhanchenMock(JinmeixindaqinMock):

    def __init__(self, project, asset, asset_extend, asset_tran_list, period_start, period_end):
        super(JinmeixinhanchenMock, self).__init__(project, asset, asset_extend, asset_tran_list,
                                                   period_start, period_end)
        self.channel = 'jinmeixin_hanchen'
        self.trail_url = '/chongtian/{0}/repay/calc'.format(self.channel)
        self.trail_query_url = ''
        self.repay_plan_url = ''
        self.repay_apply_url = '/chongtian/{0}/repay/request'.format(self.channel)
        self.repay_apply_query_url = '/chongtian/{0}/repay/queryStatus'.format(self.channel)

    def repay_trail_mock(self, status, principal_over=False, interest_type='less'):
        return super(JinmeixinhanchenMock, self).repay_trail_mock(status, principal_over, interest_type)

    def repay_apply_query_mock(self, withhold, withhold_detail, success_type='PART'):
        return super(JinmeixinhanchenMock, self).repay_apply_query_mock(withhold, withhold_detail, success_type)