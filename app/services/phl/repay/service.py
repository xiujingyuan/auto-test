from app.services import OverseaRepayService, time_print


class PhlRepayService(OverseaRepayService):
    def __init__(self, env, run_env, check_req=False, return_req=False):
        self.repay_host = "http://repay{0}-phl.c99349d1eb3d045a4857270fb79311aa0.cn-shanghai.alicontainer.com".format(env)
        super(PhlRepayService, self).__init__('phl', env, run_env, check_req, return_req)

    @time_print
    def sync_plan_to_bc(self, item_no):
        self.run_xxl_job('manualSyncAsset', param={'assetItemNo': [item_no]})
        self.run_task_by_order_no(item_no, 'AssetAccountChangeNotify')
        self.run_msg_by_order_no(item_no, 'AssetChangeNotifyMQ')
