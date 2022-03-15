from app.common.xxljob_util import XxlJob


class ThaRepayXxlJob(XxlJob):
    def __init__(self, env):
        super(ThaRepayXxlJob, self).__init__('tha', 'repay', env)

    def run_auto_repay(self):
        self.trigger_job('withholdAutoV1')
