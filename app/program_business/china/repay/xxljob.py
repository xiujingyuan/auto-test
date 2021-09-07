from app.common.xxljob_util import XxlJob


class ChinaRepayXxlJob(XxlJob):
    def __init__(self, env):
        super(ChinaRepayXxlJob, self).__init__('china', 'repay', env)

    def run_auto_repay(self):
        self.trigger_job('withholdAutoV1')
