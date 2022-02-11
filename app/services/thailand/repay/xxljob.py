from app.common.xxljob_util import XxlJob


class ThailandRepayXxlJob(XxlJob):
    def __init__(self, env):
        super(ThailandRepayXxlJob, self).__init__('tha', 'repay', env)

    def run_auto_repay(self):
        self.trigger_job('withholdAutoV1')
