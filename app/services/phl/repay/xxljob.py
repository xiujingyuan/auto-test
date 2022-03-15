from app.common.xxljob_util import XxlJob


class PhlRepayXxlJob(XxlJob):
    def __init__(self, env):
        super(PhlRepayXxlJob, self).__init__('phl', 'repay', env)

    def run_auto_repay(self):
        self.trigger_job('withholdAutoV1')
