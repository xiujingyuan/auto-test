from app.common.xxljob_util import XxlJob


class PhlGrantXxlJob(XxlJob):
    def __init__(self, env):
        super(PhlGrantXxlJob, self).__init__('phl', 'grant', env)
