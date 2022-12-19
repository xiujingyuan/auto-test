from app.common.xxljob_util import XxlJob


class PakRepayXxlJob(XxlJob):
    def __init__(self, env):
        super(PakRepayXxlJob, self).__init__('pak', 'repay', env)

    def run_auto_repay(self):
        self.trigger_job('withholdAutoV1')
