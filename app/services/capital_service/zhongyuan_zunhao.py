import time

from app.services import BaseService
from app.services.capital_service import BusinessMock


class ZhongyuanzunhaoMock(BusinessMock):

    def __init__(self, project, asset, asset_extend, asset_tran_list, period_start, period_end):

        super(ZhongyuanzunhaoMock, self).__init__(project, asset, asset_extend, asset_tran_list, period_start,
                                                  period_end)
        self.channel = 'zhongyuan_zunhao'
        self.trail_url = '/zhongzhirong/{0}/repayTrial'.format(self.channel)
        self.trail_query_url = ''
        self.repay_plan_url = ''
        self.repay_apply_url = '/zhongzhirong/{0}/repayApply'.format(self.channel)
        self.repay_apply_query_url = '/zhongzhirong/{0}/transQuery'.format(self.channel)
        self.card_bind_query_url = '/zhongzhirong/{0}/queryBindCard'.format(self.channel)

    def repay_trail_mock(self, status, principal_over=False, interest_type='less'):
        principal_amount, interest_amount, _, _, _ = self.__get_trail_amount__()
        value = dict(zip(('$.data.totalRepayAmt', '$.data.totalPlanamt',
                          '$.data.totalPsPrcpAmt', '$.data.totalPsNormInt'), (
                             principal_amount + interest_amount, principal_amount + interest_amount,
                             principal_amount,
                             interest_amount)))
        return self.update_by_json_path(self.trail_url, value, method='post')

    def repay_apply_query_mock(self, withhold, withhold_detail, success_type='success'):
        principal_amount, interest_amount, fee_amount, _, _ = self.__get_trail_amount__()
        code = 0 if success_type.lower() == 'success' else 90000
        value = dict(zip(('$.data.listApproveInfo[0].loanNo', '$.data.listApproveInfo[0].amt',
                          '$.data.listApproveInfo[0].repayTime', '$.code'), (
            self.asset.asset_due_bill_no, principal_amount + interest_amount + fee_amount,
            self.get_date(is_str=True), code)))
        return self.update_by_json_path(self.repay_apply_query_url, value, method='post')

    def card_bind_query_mock(self, withhold, success_type='success'):
        code = "02" if success_type.lower() == 'success' else "03"
        withhold_list = list((withhold.withhold_user_name, withhold.withhold_user_idnum, withhold.withhold_user_phone,
                              withhold.withhold_card_num))
        withhold_decrypt = BaseService.decrypt_data_list(withhold_list)
        value = dict(zip(('$.data.listAgreement[0].custName', '$.data.listAgreement[0].idNo',
                          '$.data.listAgreement[0].cardNo', '$.data.listAgreement[0].mobileNo',
                          '$.data.listAgreement[0].idNoEncrypt', '$.data.listAgreement[0].cardNoEncrypt',
                          '$.data.listAgreement[0].mobileNoEncrypt', '$.data.listAgreement[0].channelRepayId',
                          '$.data.listAgreement[0].status'),
                         (withhold_decrypt['decrypt_data_list'][withhold.withhold_user_name],
                          withhold_decrypt['decrypt_data_list'][withhold.withhold_user_idnum],
                          withhold_decrypt['decrypt_data_list'][withhold.withhold_user_phone],
                          withhold_decrypt['decrypt_data_list'][withhold.withhold_card_num],
                          withhold.withhold_user_idnum, withhold.withhold_card_num,
                          withhold.withhold_user_phone, 'AIP5481{0}'.format(int(time.time())), code)))
        return self.update_by_json_path(self.card_bind_query_url, value, method='post')
