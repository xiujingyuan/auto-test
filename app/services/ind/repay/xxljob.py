from app.common.xxljob_util import XxlJob


class IndiaRepayXxlJob(XxlJob):
    def __init__(self, env):
        super(IndiaRepayXxlJob, self).__init__('ind', 'repay', env)

    def run_auto_repay(self):
        self.trigger_job('withholdAutoV1')
