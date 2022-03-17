from app.common.xxljob_util import XxlJob


class MexGrantXxlJob(XxlJob):
    def __init__(self, env):
        super(MexGrantXxlJob, self).__init__('mex', 'grant', env)
