from app.common.nacos_util import Nacos


class ChinaBizCentralNacos(Nacos):
    def __init__(self, env):
        self.program = 'biz_central'
        super(ChinaBizCentralNacos, self).__init__('china', ''.join((self.program, env)))

    def update_repay_paysvr_config_by_value(self, value):
        super(ChinaBizCentralNacos, self).update_config('repay_paysvr_config', value)