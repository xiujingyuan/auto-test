from app.services.repay import OverseaRepayService, time_print
from app.services.phl.grant.service import PhlGrantService


class PhlRepayService(OverseaRepayService):
    def __init__(self, env, run_env, check_req=False, return_req=False):
        self.repay_host = "http://repay{0}-phl.c99349d1eb3d045a4857270fb79311aa0.cn-shanghai.alicontainer." \
                          "com".format(env)
        super(PhlRepayService, self).__init__('phl', env, run_env, check_req, return_req)
        self.repay_asset_withdraw_success_url = self.repay_host + "/sync/asset/from-grant"
        self.grant = PhlGrantService(env, run_env, check_req, return_req)

    def auto_loan(self, channel, period, amount, source_type='fee_30_normal', from_app='jasmine',
                  withdraw_type='online', days=0):
        element = self.get_four_element()
        asset_info, old_asset, item_no = self.grant.asset_import(channel, period, days, "day", 500000, self.country,
                                                                 from_app, source_type, element, withdraw_type)
        withdraw_success_data = self.grant.get_withdraw_success_data(item_no, old_asset, '', asset_info)
        self.grant.asset_withdraw_success(withdraw_success_data)
        self.add_asset(item_no, 0)
        return item_no, ''

    @time_print
    def sync_plan_to_bc(self, item_no):
        self.run_xxl_job('manualSyncAsset', param={'assetItemNo': [item_no]})
        self.run_task_by_order_no(item_no, 'AssetAccountChangeNotify')
        self.run_msg_by_order_no(item_no, 'AssetChangeNotifyMQ')
