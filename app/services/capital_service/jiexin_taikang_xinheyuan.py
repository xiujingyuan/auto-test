import time
import random
from decimal import Decimal

from app.services import BaseService
from app.services.capital_service import BusinessMock


class JiexintaikangxinheyuanMock(BusinessMock):

    def __init__(self, project, asset, asset_extend, asset_tran_list, period_start, period_end):

        super(JiexintaikangxinheyuanMock, self).__init__(project, asset, asset_extend, asset_tran_list, period_start,
                                                         period_end)
        self.channel = 'jiexin_taikang_xinheyuan'
        self.trail_url = '/xinheyuan/{0}/preRepayApply'.format(self.channel)
        self.verify_msg_url = '/xinheyuan/{0}/verifyBindBankSms'.format(self.channel)
        self.send_msg_url = '/xinheyuan/{0}/getBindBankSms'.format(self.channel)
        self.trail_query_url = ''
        self.repay_plan_url = ''
        self.repay_apply_url = '/xinheyuan/{0}/repaymentApply'.format(self.channel)
        self.repay_apply_query_url = '/xinheyuan/{0}/repaymentResult'.format(self.channel)
        self.card_bind_query_url = '/xinheyuan/{0}/repaymentResult1'.format(self.channel)
        self.late_interest_url = '/xinheyuan/{0}/interestPenaltyQuery'.format(self.channel)

    def repay_trail_mock(self, status, principal_over=False, interest_type='less'):
        principal_amount, interest_amount, _, _, _ = self.__get_trail_amount__()
        if interest_type == 'less':
            interest_amount -= 100
        elif interest_type == 'more':
            interest_amount += 100
        value = dict(zip(('$.data.payNormAmt', '$.data.payInteAmt',
                          '$.data.status'), (
                             self.fen2yuan(principal_amount),
                             self.fen2yuan(interest_amount),
                             'SUCCESS')))
        return self.update_by_json_path(self.trail_url, value, method='post')

    def repay_apply_query_mock(self, withhold, withhold_detail, success_type='success'):
        principal_amount, interest_amount, fee_amount, late_amount, _ = self.__get_trail_amount__()
        code = 'SUCCESS' if success_type.lower() == 'success' else 'FAIL'
        value = dict(zip(('$.data.amt', '$.data.repayTime', '$.data.status'),
                          (float(Decimal(float((principal_amount + interest_amount + fee_amount + late_amount)
                                               / 100)).quantize(Decimal("0.00")))
                           , self.get_date(is_str=True), code)))
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

    def msg_send_mock(self, backend_config, success_type='success'):
        backend = backend_config[success_type.lower()]
        param = {}
        for key, value in backend.items():
            param[key] = random.choice(value)
        return self.update_by_json_path(self.send_msg_url, param, method='post')

    def msg_verify_mock(self, withhold, success_type='success'):
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
        return self.update_by_json_path(self.verify_msg_url, value, method='post')
