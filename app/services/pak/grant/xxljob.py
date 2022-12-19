from app.common.xxljob_util import XxlJob


class PakGrantXxlJob(XxlJob):
    def __init__(self, env):
        super(PakGrantXxlJob, self).__init__('pak', 'grant', env)
