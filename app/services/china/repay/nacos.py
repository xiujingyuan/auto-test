from app.common.nacos_util import Nacos


class ChinaRepayNacos(Nacos):
    def __init__(self, env):
        self.program = 'repay'
        super(ChinaRepayNacos, self).__init__('china', ''.join((self.program, env)))

    def update_repay_paysvr_config_by_value(self, mock_paysvr_url):
        super(ChinaRepayNacos, self).update_config('repay_paysvr_config', mock_paysvr_url)


class QinnongRepayNacos(ChinaRepayNacos):
    def __init__(self, env):
        self.kv_name = 'repay_qinnong_config'
        super(QinnongRepayNacos, self).__init__(env)
        self.config_content = self.get_config_content(self.kv_name)



