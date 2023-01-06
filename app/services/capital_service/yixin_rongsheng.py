from app.services.capital_service import BusinessMock


class YixinrongshengMock(BusinessMock):

    def __init__(self, project, asset, asset_extend, asset_tran_list, period_start, period_end):
        self.channel = 'yixin_rongsheng'
        super(YixinrongshengMock, self).__init__(project, asset, asset_extend, asset_tran_list, period_start, period_end)
        self.trail_url = '/yixin/yixin_rongsheng/calAllAmountInAdvanceSingle'
        self.trail_query_url = ''
        self.repay_plan_url = ''
        self.repay_apply_url = ''
        self.repay_apply_query_url = '/yixin/yixin_rongsheng/repay.result'

    def repay_trail_mock(self, status, principal_over=False, interest_type='less'):
        _, interest_amount, _, _, repayPlanDict = self.__get_trail_amount__()
        principal_amount = repayPlanDict[min(repayPlanDict.keys())]['principal'] * 100
        principal_amount = principal_amount + 1 if principal_over else principal_amount
        if interest_type == 'less':
            interest_amount = interest_amount - 1
        elif interest_type == 'more':
            interest_amount = interest_amount + 1
        elif interest_type == 'zero':
            interest_amount = 0
        value = dict(zip(('$.data.lnsCurAmt', '$.data.lnsCurInt'),
                         (principal_amount, interest_amount)))

        return self.update_by_json_path(self.trail_url, value, method='post')

    def repay_apply_query_mock(self, withhold, withhold_detail, success_type='success'):
        principal_amount, interest_amount, _, _, _ = self.__get_trail_amount__()
        code = 0 if success_type.lower() == 'success' else 90000
        status = 'SUCCESS' if success_type.lower() == 'success' else 'FAIL'
        value = dict(zip(('$.data.repayAmount', '$.data.repayStatus', '$.code'), (
            principal_amount + interest_amount,
            status, code)))
        return self.update_by_json_path(self.repay_apply_query_url, value, method='post')
