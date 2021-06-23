from app.common.nacos_util import Nacos


class ChinaRepayNacos(Nacos):
    def __init__(self, env):
        super(ChinaRepayNacos, self).__init__('china', 'repay{0}'.format(env))

    def update_repay_paysvr_config_by_value(self, value):
        super(ChinaRepayNacos, self).update_configs('repay_paysvr_config', value)

    def update_repay_paysvr_config_by_gate(self):
        payment_gate_url = 'http://kong-api-test.kuainiujinke.com/payment-staging-tq'
        new_value = {
                        "$.api_config.payment_url": payment_gate_url,
                        "$.api_config.url": payment_gate_url,
                        "$.sign_company_config.sign_subject_domain_mapping[0].payment_domain": payment_gate_url,
                        "$.sign_company_config.sign_subject_domain_mapping[1].payment_domain": payment_gate_url
                    }
        self.update_config_by_json_path('repay_paysvr_config', new_value)

    def update_repay_paysvr_config_by_mock(self):
        payment_mock_url = 'http://easy-mock.k8s-ingress-nginx.kuainiujinke.com/mock/5de5d515d1784d36471d6041' \
                           '/rbiz_auto_test'
        new_value = {
                        "$.api_config.payment_url": payment_mock_url,
                        "$.api_config.url": payment_mock_url,
                        "$.sign_company_config.sign_subject_domain_mapping[0].payment_domain": payment_mock_url,
                        "$.sign_company_config.sign_subject_domain_mapping[1].payment_domain": payment_mock_url
                     }

        self.update_config_by_json_path('repay_paysvr_config', new_value)
