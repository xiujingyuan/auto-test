from app.services.repay import OverseaRepayService, time_print
from app.services.phl.grant.service import PhlGrantService


class PhlRepayService(OverseaRepayService):
    def __init__(self, env, run_env, mock_name, check_req=False, return_req=False):
        self.repay_host = "https://biz-gateway-proxy.starklotus.com/phl_repay{0}".format(env)
        self.grant = PhlGrantService(env, run_env, mock_name, check_req, return_req)
        super(PhlRepayService, self).__init__('phl', env, run_env, mock_name, check_req, return_req)

    def auto_loan(self, channel, period, days, amount, source_type, joint_debt_item='', from_app='phi011'):
        x_item_no = False if channel == 'pico_qr' else True
        return super(PhlRepayService, self).auto_loan(channel, period, days, amount, source_type,
                                                      joint_debt_item=joint_debt_item,
                                                      x_item_no=x_item_no, from_app=from_app)

    @time_print
    def sync_plan_to_bc(self, item_no):
        self.run_xxl_job('manualSyncAsset', param={'assetItemNo': [item_no]})
        self.run_task_by_order_no(item_no, 'AssetAccountChangeNotify')
        self.run_msg_by_order_no(item_no, 'AssetChangeNotifyMQ')
