from app.common.xxljob_util import XxlJob


class ThaGrantXxlJob(XxlJob):
    def __init__(self, env):
        super(ThaGrantXxlJob, self).__init__('tha', 'grant', env)
