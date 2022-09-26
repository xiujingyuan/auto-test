from app.common.xxljob_util import XxlJob


class ChinaCleanXxlJob(XxlJob):
    def __init__(self, env):
        super(ChinaCleanXxlJob, self).__init__('china', 'clean', env)
