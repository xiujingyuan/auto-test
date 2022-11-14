from decimal import Decimal

from app.services.capital_service.jinmeixin_daqin import JinmeixindaqinMock


class JinmeixinhanchenjfMock(JinmeixindaqinMock):

    def __init__(self, project, asset, asset_extend, asset_tran_list, period_start, period_end):
        super(JinmeixinhanchenjfMock, self).__init__(project, asset, asset_extend, asset_tran_list,
                                                     period_start, period_end)
        self.channel = 'jinmeixin_hanchen_jf'
        self.trail_url = '/jingfa/{0}/kuainiu/apply/repayTrial'.format(self.channel)
        self.trail_query_url = ''
        self.repay_plan_url = ''
        self.repay_apply_url = '/jingfa/{0}/kuainiu/apply/repayTrial'.format(self.channel)
        self.repay_apply_query_url = '/jingfa/{0}/kuainiu/query/repayResultQuery'.format(self.channel)

    def repay_trail_mock(self, status, principal_over=False, interest_type='less'):
        principal_amount, interest_amount, _, _, _ = self.__get_trail_amount__()
        if interest_type == 'less':
            interest_amount -= 100
        elif interest_type == 'more':
            interest_amount += 100
        value = dict(zip(('$.data.data.repaymentPrinciple', '$.data.data.repaymentInterest',
                          '$.data.data.repaymentTotalAmt'), (
                             principal_amount,
                             interest_amount,
                             interest_amount + principal_amount)))
        return self.update_by_json_path(self.trail_url, value, method='post')

    def repay_apply_query_mock(self, withhold, withhold_detail, success_type='PART'):
        principal_amount, interest_amount, fee_amount, late_amount, _ = self.__get_trail_amount__()
        code = '1' if success_type.lower() == 'success' else '2'
        period = min(list(map(lambda x: x.withhold_detail_period, withhold_detail)))
        value = dict(zip(('$.data.data.repayList[0].loanNo', '$.data.data.repayList[0].period',
                          '$.data.data.repayList[0].repayDate', '$.data.data.repayList[0].repaymentInterest',
                          '$.data.data.repayList[0].repaymentPrinciple',
                          '$.data.data.repayList[0].repaymentTotalAmt',
                          '$.data.data.repayList[0].status'),
                          (self.asset.asset_due_bill_no, period, self.get_date(is_str=True, fmt='%Y%m%d'),
                           interest_amount,
                           principal_amount, principal_amount + interest_amount, code)))
        return self.update_by_json_path(self.repay_apply_query_url, value, method='post')
