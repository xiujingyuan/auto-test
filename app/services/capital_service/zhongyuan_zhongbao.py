from functools import reduce

from app.services.capital_service import BusinessMock


class ZhongyuanzhongbaoMock(BusinessMock):

    def __init__(self, project, asset, asset_extend, asset_tran_list, period_start, period_end):
        self.channel = 'zhongyuan_zhongbao'
        super(ZhongyuanzhongbaoMock, self).__init__(project, asset, asset_extend, asset_tran_list, period_start,
                                                    period_end)
        self.trail_url = '/zhongbao/zhongyuan_zhongbao/ZYXF014/indicator/trialRepayment'
        self.trail_query_url = ''
        self.repay_plan_url = '/zhongzhirong/yumin_zhongbao/ym.repay.plan'
        self.repay_apply_url = ''
        self.repay_apply_query_url = '/zhongbao/zhongyuan_zhongbao/ZYXF006/indicator/payQueryInfo'

    def repay_trail_mock(self, status, principal_over=False, interest_type='less'):
        principal_amount, interest_amount, _, _, _ = self.__get_trail_amount__()
        if interest_type == 'less':
            interest_amount -= 100
        elif interest_type == 'more':
            interest_amount += 100
        elif interest_type == "zero":
            interest_amount = 0
        value = dict(zip(('$.data.totalPsPrcpAmt', '$.data.totalPsNormInt'),
                         (self.fen2yuan(principal_amount), self.fen2yuan(interest_amount))))
        return self.update_by_json_path(self.trail_url, value, method='post')

    def repay_apply_query_mock(self, withhold, withhold_detail, success_type='success'):
        principal_amount, _, _, _, _ = self.__get_trail_amount__()
        interest_detail = tuple(filter(lambda x: x.withhold_detail_asset_tran_type == 'repayinterest', withhold_detail))
        fee_detail = tuple(
            filter(lambda x: x.withhold_detail_asset_tran_type == 'technical_service', withhold_detail))
        interest = reduce(lambda x, y: x + y, [x.withhold_detail_withhold_amount for x in interest_detail], 0)
        fee = reduce(lambda x, y: x + y, [x.withhold_detail_withhold_amount for x in fee_detail], 0)
        code = '01' if success_type.lower() == 'success' else '02'
        status = '99' if success_type.lower() == 'success' else '21'
        value = dict(zip(('$.data.listApproveInfo[0].amt', '$.data.listApproveInfo[0].outSts',
                          '$.data.listApproveInfo[0].endMark'), (
            self.fen2yuan(principal_amount + interest + fee),
            status, code)))
        return self.update_by_json_path(self.repay_apply_query_url, value, method='post')
