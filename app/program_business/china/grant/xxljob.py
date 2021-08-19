from app.common.xxljob_util import XxlJob


class ChinaGrantXxlJob(XxlJob):
    def __init__(self, env):
        super(ChinaGrantXxlJob, self).__init__('china', 'grant', env)
