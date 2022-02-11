from app.common.xxljob_util import XxlJob


class MexicoRepayXxlJob(XxlJob):
    def __init__(self, env):
        super(MexicoRepayXxlJob, self).__init__('mexico', 'repay', env)

    def run_auto_repay(self):
        self.trigger_job('withholdAutoV1')
