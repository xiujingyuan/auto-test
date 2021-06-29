from app.common.nacos_util import Nacos
from app.common.xxljob_util import XxlJob


class ChinaRepayNacos(Nacos):
    def __init__(self, env):
        self.program = 'repay'
        super(ChinaRepayNacos, self).__init__('china', ''.join((self.program, env)))

    def update_repay_paysvr_config_by_value(self, value):
        super(ChinaRepayNacos, self).update_configs('repay_paysvr_config', value)


class ChinaRepayXxlJob(XxlJob):
    def __init__(self, env):
        super(ChinaRepayXxlJob, self).__init__('china', 'repay', env)
