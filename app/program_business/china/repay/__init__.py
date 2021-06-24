from app.common.nacos_util import Nacos
from app.model.NocosConfigDb import NacosConfig


class ChinaRepayNacos(Nacos):
    def __init__(self, env):
        self.program = 'repay'
        super(ChinaRepayNacos, self).__init__('china', ''.join((self.program, env)))

    def update_repay_paysvr_config_by_value(self, value):
        super(ChinaRepayNacos, self).update_configs('repay_paysvr_config', value)
