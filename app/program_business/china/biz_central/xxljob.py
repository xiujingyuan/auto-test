from app.common.xxljob_util import XxlJob


class ChinaBizCentralXxlJob(XxlJob):
    def __init__(self, env):
        super(ChinaBizCentralXxlJob, self).__init__('china', 'biz-central', env)
