from app.common.xxljob_util import XxlJob


class MexRepayXxlJob(XxlJob):
    def __init__(self, env):
        super(MexRepayXxlJob, self).__init__('mex', 'repay', env)

    def run_auto_repay(self):
        self.trigger_job('withholdAutoV1')
