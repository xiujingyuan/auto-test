from app.common.nacos_util import Nacos
from app.common.xxljob_util import XxlJob


class ChinaBizCentralNacos(Nacos):
    def __init__(self, env):
        self.program = 'biz-central'
        super(ChinaBizCentralNacos, self).__init__('china', ''.join((self.program, env)))

    def update_repay_paysvr_config_by_value(self, value):
        super(ChinaBizCentralNacos, self).update_configs('repay_paysvr_config', value)


class ChinaBizCentralXxlJob(XxlJob):
    def __init__(self, env):
        super(ChinaBizCentralXxlJob, self).__init__('china', 'biz-central', env)
