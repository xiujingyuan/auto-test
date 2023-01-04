from app.services.capital_service import BusinessMock


class YuminzhongbaoMock(BusinessMock):

    def __init__(self, project, asset, asset_extend, asset_tran_list, period_start, period_end):
        self.channel = 'yumin_zhongbao'
        super(YuminzhongbaoMock, self).__init__(project, asset, asset_extend, asset_tran_list, period_start, period_end)
        self.trail_url = '/zhongzhirong/yumin_zhongbao/ym.repay.trial'
        self.trail_query_url = ''
        self.repay_plan_url = '/zhongzhirong/yumin_zhongbao/ym.repay.plan'
        self.repay_apply_url = ''
        self.repay_apply_query_url = ''

    def repay_trail_mock(self, status, principal_over=False, interest_type='less'):
        principal_amount, interest_amount, _, _, _ = self.__get_trail_amount__()
        value = dict(zip(('$.data.repymtPnpAmt', '$.data.repymtIntAmt'),
                         (principal_amount, interest_amount)))
        return self.update_by_json_path(self.trail_url, value, method='post')

    def repay_plan_mock(self):
        value = dict(zip(('$.data.planList[0].loanNo', '$.data.planList[1].loanNo', '$.data.planList[2].loanNo',
                          '$.data.planList[3].loanNo', '$.data.planList[4].loanNo', '$.data.planList[5].loanNo',
                          '$.data.planList[6].loanNo', '$.data.planList[7].loanNo', '$.data.planList[8].loanNo',
                          '$.data.planList[9].loanNo', '$.data.planList[10].loanNo', '$.data.planList[11].loanNo'),
                         (self.asset.asset_due_bill_no, self.asset.asset_due_bill_no,
                          self.asset.asset_due_bill_no, self.asset.asset_due_bill_no,
                          self.asset.asset_due_bill_no, self.asset.asset_due_bill_no,
                          self.asset.asset_due_bill_no, self.asset.asset_due_bill_no,
                          self.asset.asset_due_bill_no, self.asset.asset_due_bill_no,
                          self.asset.asset_due_bill_no, self.asset.asset_due_bill_no)))
        return self.update_by_json_path(self.repay_plan_url, value, method='post')
