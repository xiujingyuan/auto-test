from app.common.xxljob_util import XxlJob


class IndGrantXxlJob(XxlJob):
    def __init__(self, env):
        super(IndGrantXxlJob, self).__init__('ind', 'grant', env)
