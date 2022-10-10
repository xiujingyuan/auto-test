from app.services.capital_service import BusinessMock


class YiLianDingFengMock(BusinessMock):

    def __init__(self, project, asset, asset_extend, asset_tran_list, period_start, period_end):
        super(YiLianDingFengMock, self).__init__(project, asset, asset_extend, asset_tran_list, period_start, period_end)
        self.channel = 'yilian_dingfeng'
        self.trail_url = '/qingjia/yilian_dingfeng/repayTrial'
        self.trail_query_url = ''
        self.repay_plan_url = ''
        self.repay_apply_url = ''
        self.repay_apply_query_url = ''

    def repay_trail_mock(self, status, principal_over=False, interest_type='less'):
        principal_amount, interest_amount, _, _, _ = self.__get_trail_amount__()
        principal = round(float(principal_amount / 100), 2)
        interest = round(float(interest_amount / 100), 2)
        value = dict(zip(('$.data.repaytotal', '$.data.repaycapital', '$.data.repayinterest'),
                         (principal + interest, principal, interest)))
        return self.easy_mock.update_by_json_path(self.trail_url, value, method='post')
