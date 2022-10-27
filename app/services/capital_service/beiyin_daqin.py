from app.services.capital_service.jinmeixin_daqin import JinmeixindaqinMock


class BeiyindaqinMock(JinmeixindaqinMock):

    def __init__(self, project, asset, asset_extend, asset_tran_list, period_start, period_end):
        super(BeiyindaqinMock, self).__init__(project, asset, asset_extend, asset_tran_list, period_start, period_end)
        self.channel = 'beiyin_daqin'
        self.trail_url = '/chongtian/{0}/repay/calc'.format(self.channel)
        self.trail_query_url = ''
        self.repay_plan_url = ''
        self.repay_apply_url = '/chongtian/{0}/repay/request'.format(self.channel)
        self.repay_apply_query_url = '/chongtian/{0}/repay/queryStatus'.format(self.channel)
