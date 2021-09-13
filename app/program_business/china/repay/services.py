
import copy
import json
import time

from functools import reduce
from sqlalchemy import desc
from app import db
from app.common.http_util import Http
from app.common.tools import get_date
from app.model.AutoAssetDb import AutoAsset
from app.program_business import BaseAuto
from app.program_business.china.biz_central.services import ChinaBizCentralAuto
from app.program_business.china.grant.services import ChinaGrantAuto
from app.program_business.china.repay import query_withhold
from app.program_business.china.repay.Model import Asset, AssetExtend, Task, WithholdOrder, AssetTran, \
    SendMsg, Withhold, CapitalAsset, CapitalTransaction, Card, CardAsset, AssetOperationAuth, WithholdAssetDetailLock, \
    WithholdRequest, WithholdDetail


class ChinaRepayAuto(BaseAuto):
    def __init__(self, env, run_env, check_req=False, return_req=False):
        super(ChinaRepayAuto, self).__init__('china', 'repay', env, run_env, check_req, return_req)
        self.grant = ChinaGrantAuto(env, run_env, check_req, return_req)
        self.biz_central = ChinaBizCentralAuto(env, run_env, check_req, return_req)
        self.decrease_url = self.repay_host + "/asset/bill/decrease"
        self.offline_recharge_url = self.repay_host + "/account/recharge-encrypt"
        self.offline_repay_url = self.repay_host + "/asset/repayPeriod"
        self.active_repay_url = self.repay_host + "/paydayloan/repay/combo-active-encrypt"
        self.fox_repay_url = self.repay_host + "/fox/manual-withhold-encrypt"
        self.refresh_url = self.repay_host + "/asset/refreshLateFee"
        self.send_msg_url = self.repay_host + "/paydayloan/repay/bindSms"
        self.pay_svr_callback_url = self.repay_host + "/paysvr/callback"
        self.reverse_url = self.repay_host + "/asset/repayReverse"
        self.withdraw_success_url = self.repay_host + "/sync/asset-withdraw-success"
        self.run_task_id_url = self.repay_host + '/task/run?taskId={0}'
        self.run_msg_id_url = self.repay_host + '/msg/run?msgId={0}'
        self.run_task_order_url = self.repay_host + '/task/run?orderNo={0}'

    def auto_loan(self, channel, count, amount, source_type, from_system_name='香蕉'):
        self.log.log_info("rbiz_loan_tool_auto_import...env=%s, channel_name=%s" % (self.env, channel))
        element = self.get_four_element()
        # item_no 大单, x_item_no 小单, x_rights 权益单
        # item_no, x_item_no, x_rights = '20201630050959854539', '', ''
        item_no, x_item_no, x_rights, source_type, x_source_type, x_right, from_system = \
            self.grant.get_asset_item_info(channel, source_type, from_system_name)
        # 大单
        asset_info, old_asset = self.grant.asset_import(item_no, channel, element, count, amount, source_type,
                                                        from_system_name, from_system, x_item_no)
        self.grant.asset_import_success(asset_info)
        withdraw_success_data = self.grant.get_withdraw_success_data(item_no, old_asset, x_item_no, asset_info)
        self.grant.asset_withdraw_success(withdraw_success_data)
        capital_data = self.grant.get_capital_asset_data(item_no)
        self.grant.capital_asset_success(capital_data)

        # 小单
        x_list = (x_source_type, x_right)
        for index, x_asset in enumerate((x_item_no, x_rights)):
            if x_asset:
                x_ref_asset = item_no if index == 1 else ''
                no_asset_info, no_old_asset = self.grant.asset_no_loan_import(asset_info, item_no, x_asset,
                                                                              x_list[index])
                self.grant.asset_import_success(no_asset_info)
                withdraw_success_data_no = self.grant.get_withdraw_success_data(x_asset, no_old_asset, x_ref_asset,
                                                                                no_asset_info)
                self.grant.asset_withdraw_success(withdraw_success_data_no)
        if item_no:
            self.add_asset(item_no, channel, count, 0)
        return item_no, x_item_no, x_rights

    def send_msg(self, serial_no):
        req_data = {
            "busi_key": "413123123123123",
            "data": {
                "order_no": serial_no
            },
            "from_system": "Rbiz",
            "key": self.__create_req_key__('', prefix='Msg'),
            "sync_datetime": 0,
            "type": "SendBindSms"
        }
        ret = Http.http_post(self.send_msg_url, req_data)
        if ret['code'] != 0:
            raise ValueError('发送短信失败, {0}'.format(ret['message']))
        verify_seq = ret['data']['verify_seq']
        return verify_seq

    def change_asset(self, item_no, item_no_rights, advance_day, advance_month):
        item_no_x = self.get_no_loan(item_no)
        item_tuple = tuple([x for x in [item_no, item_no_x, item_no_rights] if x])
        asset_list = self.db_session.query(Asset).filter(Asset.asset_item_no.in_(item_tuple)).all()
        if not asset_list:
            raise ValueError('not found the asset, check the env!')
        asset_tran_list = self.db_session.query(AssetTran).filter(
            AssetTran.asset_tran_asset_item_no.in_(item_tuple)).order_by(AssetTran.asset_tran_period).all()
        capital_asset = self.db_session.query(CapitalAsset).filter(
            CapitalAsset.capital_asset_item_no == item_no).first()
        capital_tran_list = self.db_session.query(CapitalTransaction).filter(
            CapitalTransaction.capital_transaction_item_no == item_no).all()
        self.change_asset_due_at(asset_list, asset_tran_list, capital_asset, capital_tran_list, advance_day,
                                 advance_month)
        self.biz_central.change_asset(item_no, item_no_x, item_no_rights, advance_day, advance_month)

    def get_asset_tran_balance_amount_by_period(self, item_no, period_start, period_end):
        asset_tran_list = self.db_session.query(AssetTran).filter(AssetTran.asset_tran_asset_item_no == item_no,
                                                                  AssetTran.asset_tran_period >= period_start,
                                                                  AssetTran.asset_tran_period <= period_end).all()
        return reduce(lambda x, y: x + y.asset_tran_balance_amount, asset_tran_list, 0)

    def get_no_loan(self, item_no):
        item_no_x = ''
        asset_extend = self.db_session.query(AssetExtend).filter(
                AssetExtend.asset_extend_asset_item_no == item_no,
                AssetExtend.asset_extend_type == 'ref_order_no'
            ).first()
        if asset_extend:
            ref_order_type = self.db_session.query(AssetExtend).filter(
                AssetExtend.asset_extend_asset_item_no == item_no,
                AssetExtend.asset_extend_type == 'ref_order_type'
            ).first()
            item_no_x = asset_extend.asset_extend_val if ref_order_type and \
                                                         ref_order_type.asset_extend_val != 'lieyin' else ''
        return item_no_x

    def set_asset_tran_status(self, period, item_no, status='finish'):
        if not period or not item_no:
            raise ValueError('period or item_no can not be none!')
        if status not in ('finish', 'nofinish'):
            raise ValueError('status error, only finish, nofinish!')
        item_no_x = self.get_no_loan(item_no)
        asset = self.db_session.query(Asset).filter(Asset.asset_item_no == item_no).first()
        asset_x = self.db_session.query(Asset).filter(Asset.asset_item_no == item_no_x).first()
        asset_tran_list = self.db_session.query(AssetTran).filter(
            AssetTran.asset_tran_asset_item_no.in_((item_no, item_no_x))).all()
        asset.asset_balance_amount = asset.asset_repaid_amount = 0
        asset_x.asset_balance_amount = asset_x.asset_repaid_amount = 0
        no_status = 'finish' if status == 'nofinish' else 'nofinish'

        def set_asset_tran(tran_item, item_status):
            tran_item.asset_tran_balance_amount = 0 if item_status == 'finish' else tran_item.asset_tran_amount
            tran_item.asset_tran_repaid_amount = tran_item.asset_tran_amount if item_status == 'finish' else 0
            tran_item.asset_tran_status = item_status
            tran_item.asset_tran_finish_at = get_date() if item_status == 'finish' else '1000-01-01'

        for asset_tran in asset_tran_list:
            if asset_tran.asset_tran_period <= period:
                set_asset_tran(asset_tran, status)
            else:
                set_asset_tran(asset_tran, no_status)
            if asset_tran.asset_tran_asset_item_no == item_no:
                asset.asset_repaid_amount += asset_tran.asset_tran_repaid_amount
                asset.asset_balance_amount += asset_tran.asset_tran_balance_amount
            elif asset_tran.asset_tran_asset_item_no == item_no_x:
                asset_x.asset_repaid_amount += asset_tran.asset_tran_repaid_amount
                asset_x.asset_balance_amount += asset_tran.asset_tran_balance_amount

        for fee_type in ('principal', 'interest', 'late', 'fee'):
            setattr(asset, 'asset_repaid_{0}_amount'.format(fee_type), self._sum_amount_(fee_type, asset_tran_list))

        self.db_session.add_all(asset_tran_list)
        self.db_session.add(asset)
        self.db_session.commit()

    def set_trail_mock(self, item_no, period_start, period_end, channel, status, principal_over=False, interest_type='less'):
        """
        设置微神马试算金额
        :param item_no:资产编号
        :param period_start: 还款开始期次
        :param period_end: 还款到期期次
        :param channel: 资方
        :param status: 试算返回状态 0：成功，1：失败，2：其他，3：不存在
        :param principal_over: 是否本金和试算本金不一致
        :param interest_type: 利息类型，normal：等于利息，more：大于当前剩余利息，less，小于当前剩余利息
        :return: 无返回
        """
        at_list = self.db_session.query(AssetTran).filter(
            AssetTran.asset_tran_period >= period_start,
            AssetTran.asset_tran_period <= period_end,
            AssetTran.asset_tran_asset_item_no == item_no,
            AssetTran.asset_tran_type.in_(('repayprincipal', 'repayinterest'))).all()
        principal_amount = 0
        interest_amount = 0
        for at in at_list:
            if at.asset_tran_type == 'repayprincipal':
                principal_amount += at.asset_tran_balance_amount
            elif at.asset_tran_period == period_start:
                interest_amount = at.asset_tran_balance_amount
        if principal_over:
            principal_amount = principal_amount - 1
        if interest_type == 'less':
            interest_amount = interest_amount - 1
        elif interest_type == 'more':
            interest_amount = interest_amount + 1
        self.easy_mock.update_trail_amount(channel, principal_amount, interest_amount, status)

    @staticmethod
    def _sum_amount_(amount_type, amount_list):
        return sum([x.asset_tran_repaid_amount for x in amount_list if x.asset_tran_category == amount_type])

    def get_task_msg(self, request_no, serial_no, id_num, item_no):
        task_order_no = tuple(request_no + serial_no + [id_num['card_acc_id_num_encrypt'], item_no])
        task_list = self.db_session.query(Task).filter(
            Task.task_order_no.in_(task_order_no)).order_by(desc(Task.task_id)).all()
        msg_list = self.db_session.query(SendMsg).filter(
            SendMsg.sendmsg_order_no.in_(task_order_no)).order_by(desc(SendMsg.sendmsg_id)).all()
        task_list = list(map(lambda x: x.to_spec_dict, task_list))
        msg_list = list(map(lambda x: x.to_spec_dict, msg_list))
        return dict(zip(('task', 'msg'), (task_list, msg_list)))

    def get_biz_capital_info(self, item_no):
        return self.biz_central.get_capital_info(item_no)

    def get_biz_task_msg(self, request_no, serial_no, id_num, item_no):
        return self.biz_central.get_task_msg(request_no, serial_no, id_num, item_no)

    @query_withhold
    def active_repay(self, item_no, item_no_rights='', repay_card=1, amount=0, x_amount=0, rights_amount=0,
                     verify_code='', verify_seq=None, agree=False, period_start=None, period_end=None):
        item_no_x = self.get_no_loan(item_no) if item_no else ''
        if item_no_rights:
            rights_info = self.db_session.query(AssetExtend).filter(
                AssetExtend.asset_extend_asset_item_no == item_no_rights,
                AssetExtend.asset_extend_type == 'ref_order_type',
                AssetExtend.asset_extend_val == 'lieyin').first()
            if not rights_info:
                raise ValueError('The item {0} is not rights asset!'.format(item_no_rights))
        if not item_no and not item_no_rights:
            raise ValueError('need item_no or item_no_rights one is not null!')
        amount = self.__get_repay_amount__(amount, item_no, period_start, period_end)
        x_amount = self.__get_repay_amount__(x_amount, item_no_x, period_start, period_end)
        rights_amount = self.__get_repay_amount__(rights_amount, item_no_rights, period_start, period_end)
        if amount == 0 and x_amount == 0 and rights_amount == 0:
            return "当前已结清", "", []
        request_data = self.__get_active_request_data__(item_no, item_no_x, item_no_rights, amount, x_amount,
                                                        rights_amount, repay_card, verify_code=verify_code,
                                                        verify_seq=verify_seq)
        resp = Http.http_post(self.active_repay_url, request_data)
        if resp['code'] == 0 and agree:
            # 协议支付 发短信
            first_serial_no = resp['data']['project_list'][0]['order_no']
            agree_request_data = copy.deepcopy(request_data)
            verify_seq = self.send_msg(first_serial_no) if verify_seq is None else verify_seq
            # 第二次发起
            agree_request_data['key'] = self.__create_req_key__(item_no, prefix='Agree')
            agree_request_data['data']['order_no'] = first_serial_no
            agree_request_data['data']['verify_code'] = verify_code
            agree_request_data['data']['verify_seq'] = verify_seq
            agree_resp = Http.http_post(self.active_repay_url, agree_request_data)
            # 执行协议签约任务
            request_data = [request_data, agree_request_data]
            resp = [resp, agree_resp]
        return request_data, self.active_repay_url, resp

    def __get_repay_amount__(self, amount, item_no, period_start, period_end):
        if amount == 0 and period_start is not None and period_end is not None:
            amount = self.get_asset_tran_balance_amount_by_period(item_no, period_start, period_end)
        return amount

    def __get_active_request_data__(self, item_no, item_no_x, item_no_rights, amount, x_amount, rights_amount,
                                    repay_card, item_no_priority=12, item_no_rights_priority=5,
                                    item_no_x_priority=1, coupon_num=None, coupon_amount=None, order_no='',
                                    verify_code='', verify_seq=''):
        card_info = self.get_active_card_info(item_no, repay_card)
        key = self.__create_req_key__(item_no, prefix='Active')
        active_request_data = {
            "type": "PaydayloanUserActiveRepay",
            "key": key,
            "from_system": "DSQ",
            "data": {
                "total_amount": amount + x_amount + rights_amount,
                "project_list": [],
                "order_no": order_no,
                "verify_code": verify_code,
                "verify_seq": verify_seq
            }
        }
        for four_element_key, four_element_value in self.__get_four_element_key__(repay_card).items():
            active_request_data['data'][four_element_key] = card_info[four_element_value]
        amount_info_list = [(item_no, amount, item_no_priority, None, None),
                            (item_no_rights, rights_amount, item_no_rights_priority, None, None),
                            (item_no_x, x_amount, item_no_x_priority, coupon_num, coupon_amount)]
        amount_info_key = ("project_num", "amount", "priority", "coupon_num", "coupon_amount")
        for amount_info in amount_info_list:
            if amount_info[1] != 0:
                active_request_data['data']['project_list'].append(dict(zip(amount_info_key, amount_info)))
        return active_request_data

    @staticmethod
    def __get_four_element_key__(repay_card):
        repay_key = ('card_num_encrypt', 'card_user_id_encrypt', 'card_user_name_encrypt', 'card_user_phone_encrypt')
        if repay_card == 1:
            card_element = ('card_acc_num_encrypt', 'card_acc_id_num_encrypt', 'card_acc_tel_encrypt',
                            'card_acc_name_encrypt')
        elif repay_card in (0, 2):
            card_element = ('bank_code_encrypt', 'id_number_encrypt', 'user_name_encrypt', 'phone_number_encrypt')
        return dict(zip(repay_key, card_element))

    def get_active_card_info(self, item_no, repay_card):
        # 1-还款卡还款
        card_info = self.get_repay_card_by_item_no(item_no)
        if repay_card in (0, 2):
            # 0-还款人身份证相同银行卡不同;2-还款人身份证和银行卡都不同
            id_num = card_info['card_acc_id_num_encrypt'] if repay_card == 0 else None
            card_info = self.get_four_element(id_num=id_num)['data']
        return card_info

    def get_repay_card_by_item_no(self, item_no):
        sql = "select card_acc_id_num_encrypt, card_acc_num_encrypt, card_acc_tel_encrypt, card_acc_name_encrypt " \
              "from card join card_asset on card_no = card_asset_card_no where " \
              "card_asset_asset_item_no='{0}'and card_asset_type = 'repay'".format(item_no)
        id_num_info = self.db_session.execute(sql)
        return id_num_info[0] if id_num_info else ''

    def get_withhold_info(self, item_no, req_key='', repay_type=''):
        item_no_x = self.get_no_loan(item_no)
        withhold_status = 'success' if repay_type == 'crm_repay' else 'ready'
        request_no, serial_no = set([]), set([])
        if req_key:
            withhold_order_list = self.db_session.query(WithholdOrder).filter(
                WithholdOrder.withhold_order_req_key == req_key).all()
            for withhold_order in withhold_order_list:
                request_no.add(withhold_order.withhold_order_request_no)
                serial_no.add(withhold_order.withhold_order_serial_no)
        if not request_no:
            withhold_order_list = self.db_session.query(WithholdOrder).filter(
                WithholdOrder.withhold_order_reference_no.in_((item_no, item_no_x))
            ).all()
            for withhold_order in withhold_order_list:
                is_add = False
                if repay_type == 'crm_repay' and withhold_order.withhold_order_withhold_status == withhold_status\
                        and withhold_order.withhold_order_serial_no.like('%DECREASE%'):
                    is_add = True
                elif withhold_order.withhold_order_withhold_status == withhold_status:
                    is_add = True
                if is_add:
                    request_no.add(withhold_order.withhold_order_request_no)
                    serial_no.add(withhold_order.withhold_order_serial_no)
        id_num_encrypt = self.get_repay_card_by_item_no(item_no)
        return dict(zip(('request_no', 'serial_no', 'id_num'), (list(request_no), list(serial_no), id_num_encrypt)))

    def get_current_withhold_info(self, item_no, request_no):
        withhold_order_list = self.db_session.query(WithholdOrder).filter(
            WithholdOrder.withhold_order_request_no.in_(request_no),
            WithholdOrder.withhold_order_reference_no == item_no) \
            .order_by(desc(WithholdOrder.withhold_order_create_at)).all()
        serial_no_tuple = tuple(map(lambda x: x.withhold_order_serial_no, withhold_order_list))
        withhold_detail_list = self.db_session.query(WithholdDetail).filter(
            WithholdDetail.withhold_detail_serial_no.in_(serial_no_tuple),
            WithholdDetail.withhold_detail_asset_item_no == item_no).all()
        withhold_list = self.db_session.query(Withhold).filter(
            Withhold.withhold_serial_no.in_(serial_no_tuple)).all()
        withhold_request_list = self.db_session.query(WithholdRequest).filter(
            WithholdRequest.withhold_request_req_key.in_(request_no)).all()
        withhold_order_list = list(map(lambda x: x.to_spec_dict, withhold_order_list))
        withhold_detail_list = list(map(lambda x: x.to_spec_dict, withhold_detail_list))
        withhold_request_list = list(map(lambda x: x.to_spec_dict, withhold_request_list))
        withhold_list = list(map(lambda x: x.to_spec_dict, withhold_list))
        return dict(zip(('withhold', 'withhold_order', 'withhold_detail', 'withhold_request'),
                        (withhold_list, withhold_order_list, withhold_detail_list, withhold_request_list)))

    def get_all_withhold_info(self, item_no):
        withhold_order_list = self.db_session.query(WithholdOrder).filter(
            WithholdOrder.withhold_order_reference_no == item_no)\
            .order_by(desc(WithholdOrder.withhold_order_create_at)).all()
        withhold_detail_list = self.db_session.query(WithholdDetail).filter(
            WithholdDetail.withhold_detail_asset_item_no == item_no)\
            .order_by(desc(WithholdDetail.withhold_detail_create_at)).all()
        req_key_tuple = tuple(set(map(lambda x: x.withhold_order_req_key, withhold_order_list)))
        request_no_tuple = tuple(set(map(lambda x: x.withhold_order_request_no, withhold_order_list)))
        withhold_request_list = self.db_session.query(WithholdRequest).filter(
            WithholdRequest.withhold_request_req_key.in_(req_key_tuple))\
            .order_by(desc(WithholdRequest.withhold_request_create_at)).all()
        withhold_list = self.db_session.query(Withhold).filter(
            Withhold.withhold_request_no.in_(request_no_tuple))\
            .order_by(desc(Withhold.withhold_create_at)).all()
        withhold_order_list = list(map(lambda x: x.to_spec_dict, withhold_order_list))
        withhold_detail_list = list(map(lambda x: x.to_spec_dict, withhold_detail_list))
        withhold_request_list = list(map(lambda x: x.to_spec_dict, withhold_request_list))
        withhold_list = list(map(lambda x: x.to_spec_dict, withhold_list))

        return dict(zip(('withhold', 'withhold_order', 'withhold_detail', 'withhold_request'),
                        (withhold_list, withhold_order_list, withhold_detail_list, withhold_request_list)))

    def add_asset(self, name, channel, period, source_type):
        asset = AutoAsset()
        asset.asset_create_at = self.get_date(fmt="%Y-%m-%d", is_str=True)
        asset.asset_channel = channel
        asset.asset_descript = ''
        asset.asset_name = name
        asset.asset_period = period
        asset.asset_env = self.env
        asset.asset_source_type = source_type
        db.session.add(asset)
        db.session.flush()
        return asset.to_dict

    def get_asset(self, channel, period):
        asset_list = AutoAsset.query.filter(AutoAsset.asset_period == period,
                                            AutoAsset.asset_channel == channel,
                                            AutoAsset.asset_env == self.env)\
            .order_by(desc(AutoAsset.asset_create_at)).all()
        asset_list = list(map(lambda x: x.to_spec_dict, asset_list))
        return asset_list

    def get_asset_info(self, item_no):
        item_no_x = self.get_no_loan(item_no)
        asset_list = self.db_session.query(Asset).filter(Asset.asset_item_no.in_((item_no, item_no_x))).all()
        asset_tran_list = self.db_session.query(AssetTran).filter(AssetTran.asset_tran_asset_item_no.in_(
            (item_no, item_no_x))).all()
        asset_list = list(map(lambda x: x.to_spec_dict, asset_list))
        asset_tran_list = list(map(lambda x: x.to_spec_dict, asset_tran_list))
        return dict(zip(('asset', 'asset_tran'), (asset_list, asset_tran_list)))

    def get_lock_info(self, item_no):
        item_no_x = self.get_no_loan(item_no)
        auth_lock = self.db_session.query(AssetOperationAuth).filter(
            AssetOperationAuth.asset_operation_auth_asset_item_no.in_((item_no, item_no_x))).all()
        auth_lock = list(map(lambda x: x.to_spec_dict, auth_lock))
        detail_lock = self.db_session.query(WithholdAssetDetailLock).filter(
            WithholdAssetDetailLock.withhold_asset_detail_lock_asset_item_no.in_((item_no, item_no_x))).all()
        detail_lock = list(map(lambda x: x.to_spec_dict, detail_lock))
        return dict(zip(('auth_lock', 'detail_lock'), (auth_lock, detail_lock)))

    def refresh_late_fee(self, item_no):
        request_data = {
            "from_system": "Biz",
            "type": "RbizRefreshLateInterest",
            "key": self.__create_req_key__(item_no, prefix='Refresh'),
            "data": {
                "asset_item_no": item_no
            }
        }
        asset = self.db_session.query(Asset).filter(Asset.asset_item_no == item_no).first()
        if not asset:
            raise ValueError("not found the asset, check env!")
        resp = Http.http_post(self.refresh_url, request_data)
        asset_x = self.get_no_loan(item_no)
        if asset_x:
            request_x_data = copy.deepcopy(request_data)
            request_x_data['key'] = self.__create_req_key__(asset_x, prefix='Refresh')
            request_x_data['data']['asset_item_no'] = asset_x
            resp_x = Http.http_post(self.refresh_url, request_x_data)
        return [request_data, request_x_data] if asset_x else [request_data], self.refresh_url, [resp, resp_x] \
            if asset_x else [resp]

    def reverse_item_no(self, item_no, serial_no):
        req_data = {
            "from_system": "Biz",
            "key": self.__create_req_key__(item_no, prefix='Reverse'),
            "type": "AssetRepayReverse",
            "data": {
                "asset_item_no": item_no,
                "serial_no": "",
                "operator_name": "dongyuhong",
                "comment": "decrease and repay",
                "fromSystem": "rbiz",
                "send_change_mq": True
            }
        }
        withhold_info = self.db_session.query(Withhold).filter(Withhold.withhold_serial_no == serial_no).first()
        if not withhold_info:
            raise ValueError('withhold not found !')
        req_data['data']['serial_no'] = withhold_info.withhold_channel_key
        resp = Http.http_post(self.reverse_url, req_data)
        return req_data, self.refresh_url, resp

    def sync_withhold_to_history(self, item_no):
        return self.biz_central.sync_withhold_to_history(item_no)

    @query_withhold
    def crm_repay(self, item_no, amount):
        req_data = {
          "type": "CombineWithholdTaskHandler",
          "key": self.__create_req_key__(item_no, prefix='Crm'),
          "from_system": "DSQ",
          "data": {
            "asset_item_no": item_no,
            "bill_balance_amount": amount,
            "operator": "测试1"
          }
        }
        item_no_x = self.get_no_loan(item_no)
        repay_ret = Http.http_post(self.decrease_url, req_data)
        task_list = self.db_session.query(Task).filter(Task.task_type == 'provisionRecharge',
                                                       Task.task_order_no.in_((item_no, item_no_x))).all()
        for task in task_list:
            self.run_task_by_id(task.task_id)
        return req_data, self.decrease_url, repay_ret

    def offline_recharge_repay(self, item_no, amount, serial_no, period):
        req_data, offline_recharge_url, recharge_ret = self.offline_recharge(item_no, amount, serial_no)
        if recharge_ret['code'] == 0:
            offline_req, offline_repay_url, repay_ret = self.offline_repay(item_no, serial_no, period)
        else:
            offline_req, offline_repay_url, repay_ret = '', '', ''
        return dict(zip(('offline_recharge', 'offline_repay'), ([req_data, offline_recharge_url, recharge_ret],
                                                                [offline_req, offline_repay_url, repay_ret])))

    def offline_repay(self, item_no, serial_no, period):
        req_data = {
          "busi_key": "4123123123",
          "data": {
            "asset_item_no": item_no,
            "comment": "测试",
            "operator_id": 0,
            "operator_name": "test",
            "period": period,
            "recharge_serial_no": serial_no,
            "send_change_mq": True
          },
          "from_system": "BIZ",
          "key": self.__create_req_key__(item_no, prefix='OfflineRepay'),
          "sync_datetime": 0,
          "type": "512312312"
        }
        repay_ret = Http.http_post(self.offline_repay_url, req_data)
        return req_data, self.offline_repay_url, repay_ret

    def offline_recharge(self, item_no, amount, serial_no):
        card = self.db_session.query(Card).join(CardAsset, CardAsset.card_asset_card_no == Card.card_no).filter(
            CardAsset.card_asset_asset_item_no == item_no).first()
        req_data = {
            "busi_key": "4123123123",
            "data": {
                "amount": amount,
                "asset_item_no": item_no,
                "card_num": "",
                "comment": "test",
                "date": self.get_date(is_str=True),
                "merchant_id": "30",
                "operator_id": 0,
                "operator_name": "test",
                "send_change_mq": False,
                "serial_no": serial_no,
                "user_id_num": "",
                "user_id_num_encrypt": card.card_acc_id_num_encrypt,
                "withhold_recharge": False
            },
            "from_system": "BIZ",
            "key": self.__create_req_key__(item_no, prefix='OfflineRecharge'),
            "sync_datetime": 0,
            "type": "4123123"
        }
        repay_ret = Http.http_post(self.offline_recharge_url, req_data)
        return req_data, self.offline_recharge_url, repay_ret

    def repay_callback(self, serial_no, status):
        withhold = self.db_session.query(Withhold).filter(Withhold.withhold_serial_no == serial_no).first()
        if not withhold:
            raise ValueError('代扣记录不存在')
        channel = withhold.withhold_channel if \
            withhold.withhold_channel and \
            withhold.withhold_channel not in ('lanzhou_haoyue', 'hami_tianshan') else 'baofu_4_baidu'
        req_data = {
            "merchant_key": serial_no,
            "channel_name": channel,
            "channel_key": serial_no,
            "finished_at": self.get_date(is_str=True),
            "transaction_status": status,
            "sign": "6401cd046b5ae44ef208b8ea82d398ab",
            "from_system": "paysvr",
            "channel_message": "交易成功" if status == 2 else '交易失败'
        }
        resp = Http.http_post(self.pay_svr_callback_url, req_data)
        if resp['code'] != 0:
            raise ValueError('执行回调接口失败，返回:{0}'.format(resp))
        self.run_callback_task_and_msg(serial_no, status)
        # return dict(zip(('request', 'request_url', 'response', 'withhold_info'),
        #                 (req_data, self.pay_svr_callback_url, resp, [])))
        return req_data, self.pay_svr_callback_url, resp

    def run_callback_task_and_msg(self, serial_no, repay_status):
        withhold_order = self.db_session.query(WithholdOrder).filter(
            WithholdOrder.withhold_order_serial_no == serial_no).first()
        request_no, _, id_num_encrypt = self.get_withhold_info(withhold_order.withhold_order_reference_no)
        self.run_task_by_type_and_order_no('withhold_callback_process', withhold_order.withhold_order_reference_no)
        if repay_status == 2:
            # 跑充值还款任务
            self.run_task_by_type_and_order_no('assetWithholdOrderRecharge', serial_no)
        self.run_task_by_type_and_order_no('withhold_order_sync', serial_no)
        self.run_task_by_type_and_order_no('execute_combine_withhold', request_no)
        self.run_msg_by_type_and_order_no('', id_num_encrypt)

    def run_task_by_type_and_order_no(self, task_type, order_no):
        task_list = self.db_session.query(Task).filter(Task.task_type == task_type,
                                                       Task.task_order_no == order_no,
                                                       Task.task_status == 'open').all()
        for task in task_list:
            self.run_task_by_id(task.task_id)

    def run_msg_by_type_and_order_no(self, order_no, sendmsg_type=''):
        msg_list = self.db_session.query(SendMsg).filter(SendMsg.sendmsg_type == sendmsg_type,
                                                         SendMsg.sendmsg_order_no == order_no).all()
        for msg in msg_list:
            self.run_msg_by_id(msg.sendmsg_id)

    def run_task_by_order_no(self, order_no, task_type):
        for item_order in order_no:
            task = self.db_session.query(Task).filter(Task.task_order_no == item_order,
                                                      Task.task_type == task_type).first()
            if task:
                req = Http.http_get(self.run_task_id_url.format(task.task_id))
                if req['code'] != 0:
                    return req

    def run_crm_task_msg_by_item_no(self, item_no):
        item_no_x = self.get_no_loan(item_no)
        item_no_x_info = self.db_session.query(Asset).filter(Asset.asset_item_no == item_no_x).first()
        item_no_x_status = item_no_x_info.asset_status if item_no_x_info else ''
        item_list = (item_no, item_no_x) if item_no_x_status == 'repay' else (item_no, )
        serial_no_list, request_no_list = set([]), set([])
        for item in item_list:
            task_info = self.db_session.query(Task).filter(Task.task_order_no == item,
                                                           Task.task_type == 'provisionRecharge',
                                                           Task.task_status == 'open').first()
            if task_info:
                serial_no = json.loads(task_info.task_request_data)['data']['rechargeSerialNo']
                serial_no_list.add(serial_no)
                withhold_order = self.db_session.query(WithholdOrder).filter(
                    WithholdOrder.withhold_order_serial_no == serial_no).first()
                if withhold_order:
                    request_no_list.add(withhold_order.withhold_order_request_no)
                self.run_task_by_id(task_info.task_id)
                self.run_task_by_order_no(serial_no, 'withhold_order_sync')
        id_num_encrypt = self.get_repay_card_by_item_no(item_no)['card_acc_id_num_encrypt']
        return dict(zip(('request_no', 'serial_no', 'id_num'), (list(request_no_list), list(serial_no_list),
                                                                id_num_encrypt)))

    @query_withhold
    def fox_repay(self, item_no, amount=0, period_start=None, period_end=None):
        if amount == 0 and period_start is not None and period_end is not None:
            amount = self.__get_repay_amount__(amount, item_no, period_start, period_end)
        req_key = self.__create_req_key__(item_no, prefix='FOX')
        fox_active_data = {
            "busi_key": "20190731061116179",
            "data": {
              "amount": amount,
              "asset_item_no": item_no,
              "asset_period": None,
              "customer_bank_card_encrypt": "enc_03_2767440037125031936_469",
              "customer_bank_code": "CCB",
              "customer_mobile_encrypt": "enc_01_2764219608117807104_022",
              "manual_user_id_num": None,
              "manual_user_id_num_encrypt": None,
              "manual_user_name": None,
              "manual_user_name_encrypt": None,
              "operator": "zss",
              "serial_no": req_key
            },
            "from_system": "Fox",
            "key": req_key,
            "sync_datetime": None,
            "type": "FoxManualWithhold"
        }
        resp = Http.http_post(self.fox_repay_url, fox_active_data)
        return fox_active_data, self.fox_repay_url, resp

    def clear_auto_withhold(self, item_no):
        item_no_x = self.get_no_loan(item_no)
        auto_withhold_order_list = self.db_session.query(WithholdOrder).filter(
            WithholdOrder.withhold_order_reference_no.in_((item_no, item_no_x)),
            WithholdOrder.withhold_order_operate_type == 'auto').all()
        if auto_withhold_order_list:
            auto_request_tuple = tuple(map(lambda x: x.withhold_order_request_no, auto_withhold_order_list))
            auto_withhold_request_list = self.db_session.query(WithholdRequest).filter(
                WithholdRequest.withhold_request_no.in_(auto_request_tuple)).all()
            for withhold_order in auto_withhold_order_list:
                withhold_order.withhold_order_operate_type = 'manual'
            for withhold_request in auto_withhold_request_list:
                withhold_request.withhold_request_operate_type = 'manual'
                withhold_request.withhold_request_trade_type = 'FOX_MANUAL_WITHHOLD'
            self.db_session.add_all(auto_withhold_order_list)
            self.db_session.add_all(auto_withhold_request_list)
            self.db_session.commit()
            time.sleep(1)

    @query_withhold
    def auto_repay(self, item_no):
        self.clear_auto_withhold(item_no)
        self.xxljob.run_auto_repay()
        start = self.get_date()
        while True:
            auto_task = self.db_session.query(Task).filter(Task.task_order_no == item_no,
                                                           Task.task_type == 'auto_withhold_execute',
                                                           Task.task_status == 'open').first()
            retry_auto_task = self.db_session.query(Task).filter(Task.task_order_no == item_no,
                                                                 Task.task_type == 'withhold_retry_execute',
                                                                 Task.task_status == 'open').first()
            if auto_task:
                break
            if retry_auto_task:
                self.run_task_by_id(retry_auto_task.task_id)
            if self.get_date(start, seconds=10) >= self.get_date():
                return '超过时间未找到自动批扣任务', '', ''
            withhold_info = self.get_withhold_info(item_no)
            if withhold_info['request_no']:
                return '有代扣记录存在', '', ''
            asset_tran = self.db_session.query(AssetTran).filter(
                AssetTran.asset_tran_asset_item_no == item_no,
                AssetTran.asset_tran_due_at == self.get_date(hour=0, minute=0, second=0, is_str=True)).first()
            if not asset_tran:
                return '到日期不是当天', '', '',
        ret = self.run_task_by_id(auto_task.task_id)
        return '执行成功', '', ''
