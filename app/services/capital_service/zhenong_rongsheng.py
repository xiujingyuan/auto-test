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
        value = dict(zip(('$.data.data.capital', '$.data.data.interest'),
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
