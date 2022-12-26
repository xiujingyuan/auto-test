import copy
import importlib
import json
import random
import time
from functools import reduce

from sqlalchemy import desc

from app import db
from app.common.http_util import Http
from app.model.Model import AutoAsset
from app.services import BaseService, Asset, AssetExtend, time_print, CapitalAsset, AssetTran, CapitalTransaction
from app.services.china.repay import modify_return, WithholdOrder, wait_time
from app.services.china.repay.Model import WithholdRequest, Withhold, SendMsg, \
    AssetOperationAuth, WithholdAssetDetailLock, Task, Buyback, Card, CardAsset
import pytz
from app.services.china.repay import query_withhold


class RepayBaseService(BaseService):
    def __init__(self, country, env, run_env, mock_name, check_req, return_req):
        super(RepayBaseService, self).__init__(country, 'repay', env, run_env, mock_name, check_req, return_req)
        self.decrease_url = self.repay_host + "/asset/bill/decrease"
        self.offline_recharge_url = self.repay_host + "/account/recharge-encrypt"
        self.offline_repay_url = self.repay_host + "/asset/repayPeriod"
        self.active_repay_url = self.repay_host + "/paydayloan/repay/combo-active-encrypt"
        self.fox_repay_url = self.repay_host + "/fox/manual-withhold-encrypt"
        self.refresh_url = self.repay_host + "/asset/refreshLateFee"
        self.send_msg_url = self.repay_host + "/paydayloan/repay/bindSms"
        self.buyback_url = self.repay_host + "/asset/buy-back"
        self.pay_svr_callback_url = self.repay_host + "/paysvr/callback"
        self.pay_svr_offline_callback_url = self.repay_host + "/paysvr/offline-withhold/callback"
        self.reverse_url = self.repay_host + "/asset/repayReverse"
        self.withdraw_success_url = self.repay_host + "/sync/asset-withdraw-success"
        self.run_task_id_url = self.repay_host + '/task/run?taskId={0}'
        self.run_msg_id_url = self.repay_host + '/msg/run?msgId={0}'
        self.run_task_order_url = self.repay_host + '/task/run?orderNo={0}'
        self.bc_query_asset_url = self.repay_host + '/paydayloan/projectRepayQuery'

    def get_debt_item_card(self, joint_debt_item):
        element = self.get_four_element()
        if joint_debt_item:
            joint_debt_asset = self.db_session.query(Asset).filter(Asset.asset_item_no == joint_debt_item).first()
            if joint_debt_asset is None:
                raise ValueError('not fount the joint_debt_asset')
            joint_debt_card_info = self.get_repay_card_by_item_no(joint_debt_asset.asset_item_no)
            if self.country == 'china':
                element["data"]["id_number_encrypt"] = joint_debt_card_info['card_acc_id_num_encrypt']
                element["data"]["bank_code_encrypt"] = joint_debt_card_info['card_acc_num_encrypt']
                element["data"]["bank_account_encrypt"] = joint_debt_card_info['card_acc_num_encrypt']
                element["data"]["mobile_encrypt"] = joint_debt_card_info['card_acc_tel_encrypt']
                element["data"]["user_name_encrypt"] = joint_debt_card_info['card_acc_name_encrypt']
            else:
                element["data"]["id_number_encrypt"] = joint_debt_card_info['card_acc_num_encrypt']
                element["data"]["card_num"] = joint_debt_card_info['card_acc_name_encrypt']
                element["data"]["bank_account_encrypt"] = joint_debt_card_info['card_acc_name_encrypt']
                element["data"]["mobile_encrypt"] = joint_debt_card_info['card_acc_tel_encrypt']
                element["data"]["user_name_encrypt"] = joint_debt_card_info['card_acc_id_num_encrypt']
        return element

    def change_kv(self, kv_type, kv_value):
        kv_type = 'update_repay_{0}_config'.format(kv_type)
        return getattr(self, kv_type)(kv_value)

    def update_repay_paysvr_config(self, kv_value):
        payment_url = 'http://easy-mock.k8s-ingress-nginx.kuainiujinke.com/mock/5de5d515d1784d36471d6041/rbiz_auto_test'
        if kv_value == 'manual':
            payment_url = 'http://easy-mock.k8s-ingress-nginx.kuainiujinke.com/mock/617b69d43083b20020c66359' \
                          '/rbiz_manual_test'
        elif kv_value == 'stating':
            payment_url = 'http://biz-payment-staging.k8s-ingress-nginx.kuainiujinke.com'
        json_path_dict = {
            '$.api_config.payment_url': payment_url,
            '$.api_config.url': payment_url,
            '$.sign_company_config.sign_subject_domain_mapping[0].payment_domain': payment_url,
            '$.sign_company_config.sign_subject_domain_mapping[1].payment_domain': payment_url,
            '$.batch_sign_bind_card_url': '{0}/batchBinding/uploadBindingCard'.format(payment_url)
        }

        return self.nacos.update_config_by_json_path('repay_paysvr_config', json_path_dict)

    def get_withhold_key_info(self, item_no, request_no=None, req_key=None, max_create_at=None):
        item_no_x = self.get_no_loan(item_no)
        max_create_at = max_create_at if max_create_at is not None else self.get_date(is_str=True, days=-7)
        item_no_tuple = tuple(filter(lambda x: x, (item_no, item_no_x)))
        withhold_order_list = self.db_session.query(WithholdOrder).filter(
            WithholdOrder.withhold_order_reference_no.in_(item_no_tuple),
            WithholdOrder.withhold_order_create_at >= max_create_at). \
            order_by(WithholdOrder.withhold_order_create_at).all()
        withhold_order = []
        if request_no is not None:
            withhold_order = list(filter(lambda x: x.withhold_order_request_no in request_no, withhold_order_list))
        if req_key is not None:
            withhold_order = list(filter(lambda x: x.withhold_order_req_key == req_key, withhold_order_list))
        if not withhold_order:
            withhold_order = list(filter(lambda x: x.withhold_order_withhold_status == 'ready', withhold_order_list))
        if not withhold_order and withhold_order_list:
            withhold_order = withhold_order_list
        request_no_tuple = tuple(map(lambda x: x.withhold_order_request_no, withhold_order))
        serial_no_tuple = tuple(map(lambda x: x.withhold_order_serial_no, withhold_order))
        id_num_encrypt_tuple = (self.get_repay_card_by_item_no(item_no)['card_acc_id_num_encrypt'],)
        withhold_order = list(map(lambda x: x.to_spec_dict, withhold_order))
        return request_no_tuple, serial_no_tuple, id_num_encrypt_tuple, item_no_tuple, withhold_order

    def get_active_card_info(self, item_no, repay_card, repay_card_num, bank_code='中国银行'):
        card_info = self.get_repay_card_by_item_no(item_no)
        random_card = self.get_four_element(bank_name=bank_code)['data']
        if repay_card == 1:
            # 1-还款卡还款
            return card_info
        elif repay_card == 0:
            # 0-还款人身份证相同银行卡不同;
            card_info['card_acc_num_encrypt'] = random_card[
                'bank_code_encrypt'] if repay_card_num is None or not repay_card_num else repay_card_num
            # card_info['card_acc_num_encrypt'] = 'enc_03_2953903355913046016_400'
            return card_info
        elif repay_card == 2:
            # 2-还款人身份证相同银行卡都不同;
            if repay_card_num is not None and repay_card_num:
                random_card['bank_code_encrypt'] = repay_card_num
            return random_card

    @modify_return
    def get_withhold(self, withhold_serial_no):
        withhold_list = self.db_session.query(Withhold).filter(
            Withhold.withhold_serial_no.in_(withhold_serial_no)).order_by(desc(Withhold.withhold_id)).all()
        return withhold_list

    @modify_return
    def get_withhold_request(self, withhold_request_no):
        withhold_request_list = self.db_session.query(WithholdRequest).filter(
            WithholdRequest.withhold_request_no.in_(withhold_request_no)).order_by(
            desc(WithholdRequest.withhold_request_id)).all()
        return withhold_request_list

    @modify_return
    def get_card_bind(self, withhold_serial_no):
        meta_class = importlib.import_module('app.services.{0}.repay.Model'.format(self.country))
        CardBind = getattr(meta_class, "CardBind")
        card_bind_list = self.db_session.query(CardBind).filter(
            CardBind.card_bind_serial_no.in_(withhold_serial_no)).order_by(desc(CardBind.card_bind_id)).all()
        return card_bind_list

    @modify_return
    def get_withhold_detail(self, withhold_serial_no):
        meta_class = importlib.import_module('app.services.{0}.repay.Model'.format(self.country))
        WithholdDetail = getattr(meta_class, "WithholdDetail")
        withhold_detail_list = self.db_session.query(WithholdDetail).filter(
            WithholdDetail.withhold_detail_serial_no.in_(withhold_serial_no)).order_by(
            desc(WithholdDetail.withhold_detail_serial_no)).all()
        return withhold_detail_list

    def get_withhold_info(self, item_no, request_no=None, req_key=None):
        """
        获取代扣信息
        :param item_no: 查询的资产编号
        :param max_create_at: 查询的资产编号
        :param request_no: 当次请求的no，如果为None，则查所有代扣信息
        :param req_key: 当次请求的key,如果为None，则查所有代扣信息
        :return:
        """
        request_no_tuple, serial_no_tuple, _, item_no_tuple, \
        withhold_order_list = self.get_withhold_key_info(item_no, request_no, req_key)
        withhold_dict = self.get_withhold(serial_no_tuple)
        withhold_detail_dict = self.get_withhold_detail(serial_no_tuple)
        withhold_request_dict = self.get_withhold_request(serial_no_tuple)
        ret = {'withhold_order': withhold_order_list}
        ret.update(withhold_dict)
        ret.update(withhold_detail_dict)
        ret.update(withhold_request_dict)
        return ret

    def del_row_data(self, item_no, del_id, refresh_type, max_create_at=None):
        obj = eval(refresh_type.title().replace("_", ""))
        self.db_session.query(obj).filter(getattr(obj, '{0}_id'.format(refresh_type)) == del_id).delete()
        self.db_session.flush()
        self.db_session.commit()
        return self.info_refresh(item_no, max_create_at=max_create_at, refresh_type=refresh_type)

    def modify_row_data(self, item_no, modify_id, modify_type, modify_data, max_create_at=None):
        obj = eval(modify_type.title().replace("_", ""))
        record = self.db_session.query(obj).filter(getattr(obj, '{0}_id'.format(modify_type)) == modify_id).first()
        for item_key, item_value in modify_data.items():
            if item_key == 'id':
                continue
            setattr(record, '_'.join((modify_type, item_key)), item_value)
        self.db_session.add(record)
        self.db_session.flush()
        self.db_session.commit()
        return self.info_refresh(item_no, max_create_at=max_create_at, refresh_type=modify_type)

    @staticmethod
    def _sum_amount_(amount_type, amount_list):
        return sum([x.asset_tran_repaid_amount for x in amount_list if x.asset_tran_category == amount_type])

    def run_task_by_id(self, task_id, refresh_type='task', max_create_at=None, item_no=None, excepts={'code': 0}):
        if self.country == 'china':
            self.update_task_next_run_at_forward_by_task_id(task_id)
        ret = super(RepayBaseService, self).run_task_by_id(task_id, excepts=excepts)
        if (task_id or max_create_at is not None) and item_no is not None:
            return self.info_refresh(item_no, max_create_at=max_create_at, refresh_type=refresh_type,
                                     refresh_id=task_id)
        return ret

    def run_msg_by_id(self, msg_id, refresh_type='msg', max_create_at=None, item_no=None):
        ret = super(RepayBaseService, self).run_msg_by_id(msg_id)
        if (max_create_at is not None or msg_id) and item_no is not None:
            return self.info_refresh(item_no, max_create_at=max_create_at, refresh_type=refresh_type, refresh_id=msg_id)
        return ret

    def reverse_item_no(self, item_no, serial_no, refresh_type, max_create_at=None):
        order_info = self.db_session.query(WithholdOrder).filter(WithholdOrder.withhold_order_serial_no == serial_no
                                                                 ).all()
        withhold_info = self.db_session.query(Withhold).filter(Withhold.withhold_serial_no == serial_no).first()
        for order in order_info:
            req_data = {
                "from_system": "Biz",
                "key": self.__create_req_key__(item_no, prefix='Reverse'),
                "type": "AssetRepayReverse",
                "data": {
                    "asset_item_no": order.withhold_order_reference_no,
                    "serial_no": "",
                    "type": "asset",
                    "operator_name": "dongyuhong",
                    "comment": "decrease and repay",
                    "fromSystem": "rbiz",
                    "send_change_mq": True
                }
            }
            req_data['data']['serial_no'] = withhold_info.withhold_channel_key
            resp = Http.http_post(self.reverse_url, req_data)
        if max_create_at is not None:
            info_ret = self.info_refresh(item_no, max_create_at=max_create_at, refresh_type=refresh_type)
            info_ret['request'] = req_data
            info_ret['response'] = resp
            info_ret['request_url'] = self.refresh_url
            return info_ret
        return dict(zip(('request', 'response', 'request_url'), (req_data, self.refresh_url, resp)))

    def set_asset_tran_status(self, period, item_no, refresh_type=None, status='finish'):
        if not period or not item_no:
            raise ValueError('period or item_no can not be none!')
        if status not in ('finish', 'nofinish'):
            raise ValueError('status error, only finish, nofinish!')
        item_no_x = self.get_no_loan(item_no)
        asset = self.db_session.query(Asset).filter(Asset.asset_item_no == item_no).first()
        if item_no_x:
            asset_x = self.db_session.query(Asset).filter(Asset.asset_item_no == item_no_x).first()
            if asset_x:
                asset_x.asset_status = 'repay'
                asset_x.asset_actual_grant_at = '1000-01-01 00:00:00'
                asset_x.asset_balance_amount = asset_x.asset_repaid_amount = 0
            else:
                item_no_x = ''
        item_tuple = tuple(filter(lambda x: x, [item_no, item_no_x]))
        asset_tran_list = self.db_session.query(AssetTran).filter(
            AssetTran.asset_tran_asset_item_no.in_(item_tuple)).all()
        asset.asset_balance_amount = asset.asset_repaid_amount = 0
        no_status = 'finish' if status == 'nofinish' else 'nofinish'

        def set_asset_tran(tran_item, item_status):
            tran_item.asset_tran_balance_amount = 0 if item_status == 'finish' else tran_item.asset_tran_amount
            tran_item.asset_tran_repaid_amount = tran_item.asset_tran_amount if item_status == 'finish' else 0
            tran_item.asset_tran_status = item_status
            tran_item.asset_tran_finish_at = self.get_date() if item_status == 'finish' else '1000-01-01'

        for asset_tran in asset_tran_list:
            if asset_tran.asset_tran_period <= (period - 1):
                set_asset_tran(asset_tran, status)
            else:
                set_asset_tran(asset_tran, no_status)
            if asset_tran.asset_tran_asset_item_no == item_no:
                asset.asset_repaid_amount += asset_tran.asset_tran_repaid_amount
                asset.asset_balance_amount += asset_tran.asset_tran_balance_amount
            elif item_no_x and asset_tran.asset_tran_asset_item_no == item_no_x:
                asset_x.asset_repaid_amount += asset_tran.asset_tran_repaid_amount
                asset_x.asset_balance_amount += asset_tran.asset_tran_balance_amount

        for fee_type in ('principal', 'interest', 'late', 'fee'):
            setattr(asset, 'asset_repaid_{0}_amount'.format(fee_type), self._sum_amount_(fee_type, asset_tran_list))

        self.db_session.add_all(asset_tran_list)
        self.db_session.add(asset)
        if item_no_x:
            self.db_session.add(asset_x)
        self.db_session.commit()

        info_ret = self.info_refresh(item_no, max_create_at=None, refresh_type=refresh_type)
        return info_ret

    def get_lock_info(self, item_no):
        item_no_x = self.get_no_loan(item_no)
        auth_lock = self.db_session.query(AssetOperationAuth).filter(
            AssetOperationAuth.asset_operation_auth_asset_item_no.in_((item_no, item_no_x))).all()
        auth_lock = list(map(lambda x: x.to_spec_dict, auth_lock))
        detail_lock = self.db_session.query(WithholdAssetDetailLock).filter(
            WithholdAssetDetailLock.withhold_asset_detail_lock_asset_item_no.in_((item_no, item_no_x))).all()
        detail_lock = list(map(lambda x: x.to_spec_dict, detail_lock))
        return dict(zip(('asset_operation_auth', 'withhold_asset_detail_lock'), (auth_lock, detail_lock)))

    @time_print
    @wait_time(timeout=1)
    def run_msg_by_order_no(self, order_no, sendmsg_type, excepts={"code": 0}):
        msg = self.db_session.query(SendMsg).filter(SendMsg.sendmsg_order_no == order_no,
                                                    SendMsg.sendmsg_status == 'open',
                                                    SendMsg.sendmsg_type == sendmsg_type).order_by(
            desc(SendMsg.sendmsg_create_at)).first()
        if msg:
            return self.run_msg_by_id(msg.sendmsg_id)
        return None

    def __early_settlement_need_decrease__(self, item_no):
        asset = self.db_session.query(Asset).filter(Asset.asset_item_no == item_no).first()
        ret = False
        if asset is None:
            return ret
        if asset.asset_loan_channel in ('qinnong', 'qinnong_jieyi'):
            config_content = self.nacos.get_config_content('repay_{0}_config'.format(asset.asset_loan_channel))
            advance_settle_decrease = config_content['advanceSettleDecrease']
            advance_settle_decrease_start = config_content['advanceSettleDecreaseStart']
            advance_settle_decrease_end = config_content['advanceSettleDecreaseEnd']
            if advance_settle_decrease:
                if advance_settle_decrease_start is not None:
                    if advance_settle_decrease_end is not None and self.cal_days(advance_settle_decrease_start,
                                                                                 asset.asset_actual_grant_at
                                                                                 ) > 0 \
                            and self.cal_days(asset.asset_actual_grant_at, advance_settle_decrease_end) > 0:
                        ret = True
                    elif self.cal_days(advance_settle_decrease_start, asset.asset_actual_grant_at) > 0:
                        ret = True
                elif advance_settle_decrease_end is not None and self.cal_days(asset.asset_actual_grant_at,
                                                                               advance_settle_decrease_end) > 0:
                    ret = True
        return ret

    def __get_repay_amount__(self, amount, item_no, period_start, period_end, max_period, is_overdue):
        if amount == 0 and period_start is not None and period_end is not None and item_no:
            if period_end == max_period and not is_overdue and self.__early_settlement_need_decrease__(item_no):
                amount = self.calc_qinnong_early_settlement(item_no)
            else:
                amount = self.get_asset_tran_balance_amount_by_period(item_no, period_start, period_end)
        return amount

    def get_asset_tran_balance_amount_by_period(self, item_no, period_start, period_end):
        asset_tran_list = self.db_session.query(AssetTran).filter(AssetTran.asset_tran_asset_item_no == item_no,
                                                                  AssetTran.asset_tran_period >= period_start,
                                                                  AssetTran.asset_tran_period <= period_end).all()
        return reduce(lambda x, y: x + y.asset_tran_balance_amount, asset_tran_list, 0)

    def __get_active_request_data__(self, item_no, item_no_x, item_no_rights, amount, x_amount, rights_amount,
                                    repay_card, bank_code, item_no_priority=12, item_no_rights_priority=5,
                                    item_no_x_priority=1, coupon_num=None, coupon_amount=None, order_no='',
                                    verify_code='', verify_seq='', repay_card_num=None):
        # card_info = self.get_active_card_info('item_no_1634196466', repay_card)

        card_info = self.get_active_card_info(item_no, repay_card, repay_card_num, bank_code)

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

    def __get_four_element_key__(self, repay_card):
        if self.country == 'china':
            repay_key = (
                'card_num_encrypt', 'card_user_id_encrypt', 'card_user_name_encrypt', 'card_user_phone_encrypt')
            if repay_card in (1, 3, 0):
                card_element = ('card_acc_num_encrypt', 'card_acc_id_num_encrypt', 'card_acc_name_encrypt',
                                'card_acc_tel_encrypt')
            elif repay_card == 2:
                card_element = ('bank_code_encrypt', 'id_number_encrypt', 'user_name_encrypt', 'phone_number_encrypt')
        else:
            repay_key = ('card_uuid', 'id_num', 'user_id', 'mobile')
            card_element = ('card_acc_num_encrypt', 'card_acc_id_num_encrypt', 'card_acc_name_encrypt',
                            'card_acc_tel_encrypt')
        return dict(zip(repay_key, card_element))

    @time_print
    def get_task(self, task_order_no, max_create_at, refresh_id):
        task_list = self.db_session.query(Task).filter(
            Task.task_order_no.in_(task_order_no),
            Task.task_create_at >= max_create_at).order_by(desc(Task.task_id)).all()
        task_list = list(map(lambda x: x.to_spec_dict, task_list))
        return {'task': task_list}

    @time_print
    def get_msg(self, task_order_no, max_create_at, refresh_id):
        msg_list = self.db_session.query(SendMsg).filter(
            SendMsg.sendmsg_order_no.in_(task_order_no),
            SendMsg.sendmsg_create_at >= max_create_at).order_by(desc(SendMsg.sendmsg_id)).all()
        msg_list = list(map(lambda x: x.to_spec_dict, msg_list))
        return {'msg': msg_list}

    @time_print
    def info_refresh(self, item_no, max_create_at=None, refresh_type=None, refresh_id=None):
        asset = self.get_asset(item_no)
        max_create_at = self.get_date(is_str=True, days=-7)
        request_no, serial_no, id_num, item_no_tuple, withhold_order = \
            self.get_withhold_key_info(item_no, max_create_at=max_create_at)
        channel = asset['asset'][0]['loan_channel']
        task_order_no = list(request_no) + list(serial_no) + list(id_num) + list(item_no_tuple) + [channel]
        ret = {}
        if refresh_type in ('task', 'msg'):
            ret = getattr(self, 'get_{0}'.format(refresh_type))(task_order_no, max_create_at, refresh_id)
        # elif refresh_type == 'biz_task':
        #     ret = self.biz_central.get_task(task_order_no, item_no, channel, max_create_at, refresh_id)
        # elif refresh_type == 'biz_msg':
        #     ret = self.biz_central.get_msg(item_no, max_create_at)
        elif refresh_type in ('withhold', 'withhold_detail', 'card_bind'):
            ret = getattr(self, 'get_{0}'.format(refresh_type))(serial_no)
        elif refresh_type == 'withhold_order':
            ret = {'withhold_order': withhold_order}
        elif refresh_type == 'withhold_request':
            ret = self.get_withhold_request(request_no)
        elif refresh_type == 'asset_tran':
            ret = getattr(self, 'get_{0}'.format(refresh_type))(item_no)
        # elif refresh_type in ('biz_capital', 'biz_capital_tran', 'biz_capital_notify'):
        #     ret = getattr(self.biz_central, 'get_{0}'.format(refresh_type[4:]))(item_no)
        # elif refresh_type == 'biz_capital_settlement_detail':
        #     ret = self.biz_central.get_capital_settlement_detail(channel)
        elif refresh_type in ('asset_operation_auth', 'withhold_asset_detail_lock'):
            ret = self.get_lock_info(item_no)
        ret.update(asset)
        return ret

    def get_repay_card_by_item_no(self, item_no):
        id_num_info = self.db_session.query(Card).join(
            CardAsset, Card.card_no == CardAsset.card_asset_card_no).\
            filter(CardAsset.card_asset_asset_item_no == item_no).first()
        return id_num_info.to_dict if id_num_info is not None else ''

    def get_asset(self, item_no):
        asset = self.check_item_exist(item_no)
        if asset is None:
            return {'asset': []}
        asset = asset.to_spec_dict
        extend_list = self.db_session.query(AssetExtend).filter(AssetExtend.asset_extend_asset_item_no == item_no).all()
        for extend in extend_list:
            asset[extend.asset_extend_type] = extend.asset_extend_val
        four_ele = self.get_repay_card_by_item_no(item_no)
        asset['id_num'] = four_ele['card_acc_id_num_encrypt']
        asset['id_num_entry'] = self.decrypt_data(four_ele['card_acc_id_num_encrypt'])
        asset['repay_card'] = four_ele['card_acc_num_encrypt']
        asset['repay_card_entry'] = self.decrypt_data(four_ele['card_acc_num_encrypt'])
        asset['repay_name'] = four_ele['card_acc_name_encrypt']
        asset['repay_name_entry'] = self.decrypt_data(four_ele['card_acc_name_encrypt'])
        asset['repay_tel'] = four_ele['card_acc_tel_encrypt']
        asset['repay_tel_entry'] = self.decrypt_data(four_ele['card_acc_tel_encrypt'])
        asset['item_x'] = self.get_no_loan(item_no)
        return {'asset': [asset]}

    def add_buyback(self, item_no, channel, period_start):
        find_exist = self.db_session.query(Buyback).filter(Buyback.buyback_asset_item_no == item_no).first()
        if find_exist:
            return '已经在回购表中'
        param = {
            "from_system": "BIZ",
            "key": self.__create_req_key__(item_no, prefix='Buyback'),
            "type": "asset_buyback_notify",
            "data": {
                "asset_item_no": item_no,
                "period_count": "12",
                "granted_principal_amount": "300000",
                "start_period": period_start,
                "buyback_total_principal_amount": "251762",
                "buyback_total_interest_amount": "2030",
                "channel": channel,
                "buyback_start_date": self.get_date(fmt='%Y-%m-%d 00:00:00', is_str=True)
            }
        }
        return Http.http_post(self.buyback_url, param)

    def remove_buyback(self, item_no, channel):
        self.db_session.query(Buyback).filter(Buyback.buyback_asset_item_no == item_no,
                                              Buyback.buyback_asset_loan_channel == channel).delete()
        self.db_session.flush()
        self.db_session.commit()
        return '移除回购成功'

    @modify_return
    def get_asset_tran(self, item_no):
        item_no_x = self.get_no_loan(item_no)
        item_tuple = (item_no, item_no_x) if item_no_x else (item_no,)
        asset_tran_list = self.db_session.query(AssetTran).filter(
            AssetTran.asset_tran_asset_item_no.in_(item_tuple)).all()
        return asset_tran_list

    def get_asset_info(self, item_no):
        asset_info = {}
        asset = self.get_asset(item_no)
        asset_tran = self.get_asset_tran(item_no)
        asset_info.update(asset)
        asset_info.update(asset_tran)
        return asset_info

    def check_item_exist(self, item_no):
        asset = self.db_session.query(Asset).filter(Asset.asset_item_no == item_no).first()
        return asset

    def get_auto_asset(self, channel, period, asset_type, days=0):
        asset_list = AutoAsset.query.filter(AutoAsset.asset_period == period,
                                            AutoAsset.asset_channel == channel,
                                            AutoAsset.asset_env == self.env,
                                            AutoAsset.asset_country == self.country,
                                            AutoAsset.asset_type == asset_type,
                                            AutoAsset.asset_create_at >= self.get_date(is_str=True, days=-7)) \
            .order_by(desc(AutoAsset.asset_id)).all()
        asset_list = list(map(lambda x: x.to_spec_dict, asset_list))
        ret = {'assets': asset_list}
        if asset_list:
            ret_info = self.get_asset_info(asset_list[0]['name'])
            ret.update(ret_info)
        return ret

    def add_asset(self, name, source_type):
        grant_asset = self.grant.check_item_exist(name)
        repay_asset = self.check_item_exist(name)
        if grant_asset is None and repay_asset is None:
            return '没有该资产'
        exist_asset = AutoAsset.query.filter(AutoAsset.asset_name == name, AutoAsset.asset_env == self.env).first()
        if exist_asset:
            exist_asset.asset_env = self.env
            exist_asset.asset_create_at = self.get_date(fmt="%Y-%m-%d", is_str=True)
            db.session.add(exist_asset)
            db.session.flush()
            return '该资产已经存在'
        else:
            if repay_asset is None:
                pass
            asset = AutoAsset()
            asset.asset_create_at = self.get_date(fmt="%Y-%m-%d", is_str=True)
            asset.asset_channel = grant_asset.asset_loan_channel if grant_asset is not None else \
                grant_asset.asset_loan_channel
            asset.asset_descript = ''
            asset.asset_name = name
            asset.asset_period = grant_asset.asset_period_count if grant_asset is not None else \
                grant_asset.asset_loan_channel
            asset.asset_env = self.env
            asset.asset_type = source_type
            asset.asset_country = self.country
            asset.asset_source_type = 1
            asset.asset_days = int(grant_asset.asset_product_category)
            db.session.add(asset)
            db.session.flush()
            return self.get_auto_asset(grant_asset.asset_loan_channel, grant_asset.asset_period_count, 0,
                                   days=int(grant_asset.asset_product_category))

    def refresh_late_fee(self, item_no):
        if not item_no:
            return
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
            self.run_task_by_type_and_order_no('AssetAccountChangeNotify', asset_x)
            self.run_msg_by_order_no(asset_x, 'AssetChangeNotifyMQ')
            # self.run_msg_by_order_no(asset_x, 'assetFoxSync')
        self.run_task_by_type_and_order_no('AssetAccountChangeNotify', item_no)
        self.run_msg_by_order_no(item_no, 'AssetChangeNotifyMQ')
        # self.run_msg_by_order_no(item_no, 'assetFoxSync')
        return [request_data, request_x_data] if asset_x else [request_data], self.refresh_url, [resp, resp_x] \
            if asset_x else [resp]

    @wait_time(timeout=10)
    def run_task_by_type_and_order_no(self, task_type, order_no):
        task_list = self.db_session.query(Task).filter(Task.task_type == task_type,
                                                       Task.task_order_no == order_no,
                                                       Task.task_status == 'open').all()
        for task in task_list:
            self.run_task_by_id(task.task_id)
        return task_list

    @time_print
    def sync_plan_to_bc(self, item_no):
        now = self.get_date(is_str=True, fmt='%Y-%m-%d')
        self.run_xxl_job('syncAssetToBiz', param={'assetItemNo': [item_no]})
        self.run_task_by_order_no('AssetAccountChangeNotify', item_no)
        self.run_msg_by_order_no(item_no, 'asset_change_fix_status')
        self.biz_central.run_central_msg_by_order_no(item_no, 'AssetChangeNotify', max_create_at=now)

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

    def get_right_item(self, item_no, item_no_x):
        item_no_right = ''
        asset_extend = self.db_session.query(AssetExtend).filter(
            AssetExtend.asset_extend_val == item_no,
            AssetExtend.asset_extend_type == 'ref_order_no'
        ).all()
        if asset_extend:
            item_no_filter = list(filter(lambda x: x.asset_extend_asset_item_no != item_no_x, asset_extend))
            item_no_right = item_no_filter[0] if item_no_filter else ''
        return item_no_right

    @time_print
    def change_asset(self, item_no, item_no_rights, advance_day, advance_month, refresh_late):
        item_no_tuple = tuple(item_no.split(',')) if ',' in item_no else (item_no,)

        for index, item in enumerate(item_no_tuple):
            item_no_x = self.get_no_loan(item)
            item_tuple = tuple([x for x in [item, item_no_x, item_no_rights] if x])
            asset_list = self.db_session.query(Asset).filter(Asset.asset_item_no.in_(item_tuple)).all()
            interval_day = 30 if self.country == 'china' else int(asset_list[0].asset_product_category)
            if not asset_list:
                raise ValueError('not found the asset, check the env!')
            asset_tran_list = self.db_session.query(AssetTran).filter(
                AssetTran.asset_tran_asset_item_no.in_(item_tuple)).order_by(AssetTran.asset_tran_period).all()

            capital_asset = self.db_session.query(CapitalAsset).filter(
                CapitalAsset.capital_asset_item_no == item).first()
            capital_tran_list = self.db_session.query(CapitalTransaction).filter(
                CapitalTransaction.capital_transaction_item_no == item).all()
            self.change_asset_due_at(asset_list, asset_tran_list, capital_asset, capital_tran_list, advance_day,
                                     advance_month, interval_day)
            if self.country == 'china':
                self.biz_central.change_asset(item, item_no_x, item_no_rights, advance_day, advance_month)
        if refresh_late:
            self.refresh_late_fee(item_no)
            self.refresh_late_fee(item_no_rights)
        # self.sync_plan_to_bc(item_no)
        return "修改完成"


TIMEZONE = {
    'mex': 'Mexico/General',
    'tha': 'Asia/Bangkok',
    'phl': 'Asia/Shanghai',
    'ind': 'Asia/Kolkata',
    'pak': 'Asia/Kolkata'
}


class OverseaRepayService(RepayBaseService):

    def __init__(self, country, env, run_env, mock_name, check_req=False, return_req=False):
        super(OverseaRepayService, self).__init__(country, env, run_env, mock_name, check_req, return_req)
        self.encrypt_url = 'http://encryptor-test.k8s-ingress-nginx.kuainiujinke.com/encrypt/'
        self.capital_asset_success_url = self.repay_host + '/capital-asset/grant'
        self.online_refund_url = self.repay_host + '/page/asset/repeated-withhold/online-refund'
        self.offline_refund_url = self.repay_host + '/page/asset/repeated-withhold/offline-refund'
        self.repay_joint_debt_url = self.repay_host + '/asset/settleDebt'
        self.fox_repay_url = self.repay_host + '/fox/withhold'

    def operate_action(self, item_no, extend, op_type, table_name, run_date):
        req = {'max_create_at': extend['create_at'] if hasattr(extend, 'create_at') else None,
                'item_no': item_no,
               'refresh_type': table_name
               }
        if op_type == 'reverse_item_no':
            req['serial_no'] = extend['serial_no']
        elif op_type in ("run_task_by_id", "run_msg_by_id"):
            req[op_type.split("_")[1] + '_id'] = extend['id']
        elif op_type == "del_row_data":
            req['del_id'] = extend['id']
        elif op_type.startswith('repay_callback_'):
            req['serial_no'] = extend['serial_no']
            req['status'] = 3 if op_type.endswith('fail') else 2
            op_type = 'repay_callback'
        return getattr(self, op_type)(**req)

    @query_withhold
    def fox_repay(self, item_no, payment_type, amount=0, period_start=None, period_end=None):
        asset_tran = self.db_session.query(AssetTran).filter(AssetTran.asset_tran_asset_item_no == item_no).all()
        max_period = asset_tran[-1].asset_tran_period
        is_overdue = False if self.cal_days(self.get_date(), asset_tran[-1].asset_tran_due_at) > 0 else True
        if amount == 0 and period_start is not None and period_end is not None:
            amount = self.__get_repay_amount__(amount, item_no, period_start, period_end, max_period, is_overdue)
        req_key = self.__create_req_key__(item_no, prefix='FOX')
        payment_option = payment_type
        if payment_type == 'barcode':
            payment_option = random.choice(["oxxo_cash", "bank_account"])
        elif payment_type == 'paycode':
            payment_option = random.choice(["wallet", "store"])
        fox_active_data = {
            "busi_key": "20190731061116179",
            "data": {
                "amount": amount,
                "item_no": item_no,
                "user_id": "",
                "payment_type": payment_type,
                "payment_option": payment_option,
                "payment_mode": None
            },
            "from_system": "Fox",
            "key": req_key,
            "sync_datetime": None,
            "type": "FoxManualWithhold"
        }
        resp = Http.http_post(self.fox_repay_url, fox_active_data)
        return fox_active_data, self.fox_repay_url, resp

    @query_withhold
    def repay_joint_debt(self, item_no, serial_no):
        request_data = {
            "from_system": "BIZ",
            "key": self.__create_req_key__(item_no, prefix='ReapyJoint'),
            "type": "AssetSettleDebt",
            "data": {
                "asset_item_no": item_no,
                "withhold_serial_no": serial_no,
                "operator_name": "john"
            }
        }
        resp = Http.http_post(self.repay_joint_debt_url, request_data)
        return request_data, self.repay_joint_debt_url, resp

    @query_withhold
    def online_refund(self, amount, serial_no, refund_type):
        request_data = {
            "from_system": "biz",
            "key": self.__create_req_key__(serial_no, prefix='OnlineRefund'),
            "type": "OnlineRepeatRefund",
            "data": {
                "refund_withhold_serial_no": serial_no,
                "refund_amount": amount,
                "operator": "john",
                "refund_type": refund_type,
                "refund_card_uuid": "312241231",
                "refund_channel": "test"
            }
        }

        resp = Http.http_post(self.online_refund_url, request_data)
        return request_data, self.online_refund_url, resp

    @query_withhold
    def offline_refund(self, amount, serial_no):
        request_data = {
            "from_system": "biz",
            "key": self.__create_req_key__(serial_no, prefix='OfflineRefund'),
            "type": "OfflineRepeatRefund",
            "data": {
                "refund_withhold_serial_no": serial_no,
                "refund_amount": amount,
                "operator": "john",
                "refund_type": "OFFLINE",
                "refund_card_uuid": "312241231",
                "refund_channel": "test"
            }
        }

        resp = Http.http_post(self.offline_refund_url, request_data)
        return request_data, self.offline_refund_url, resp

    def __get_active_request_data__(self, item_no, item_no_x, amount, x_amount, repay_card, payment_type,
                                    item_no_priority=12, item_no_x_priority=1, order_no='', coupon_list=None,
                                    repay_card_num=None):
        card_info = self.get_active_card_info(item_no, repay_card, repay_card_num)
        coupon_dict = dict(zip((item_no, item_no_x), ([], [])))
        if coupon_list and coupon_list is not None:
            for coupon in coupon_list.split("\n"):
                coupon_or, coupon_num, coupon_amount, coupon_type = coupon.split(",")
                coupon_or = item_no if coupon_or == '1' else item_no_x
                coupon_num = coupon_num if coupon_num else '{0}{2}_{1}'.format(
                    self.get_date(is_str=True, fmt='%Y%m%d%H%M%S'), coupon_type, coupon_or[0])
                if coupon_amount:
                    coupon_dict[coupon_or].append(dict(zip(('coupon_num', 'coupon_amount', 'coupon_type'),
                                                           (coupon_num, int(coupon_amount), coupon_type))))
        key = self.__create_req_key__(item_no, prefix='Active')
        active_request_data = {
            "type": "PaydayloanUserActiveRepay",
            "key": key,
            "from_system": "DSQ",
            "data": {
                "card_cvv": None,
                "payment_mode": None,
                "user_ip": None,
                "address": None,
                "email": None,
                "user_name": None,
                "individual_uuid": None,
                "payment_type": payment_type,
                "payment_option": random.choice(["oxxo_cash", "bank_account"]) if
                payment_type == 'barcode' else payment_type,
                "card_num_encrypt": None,
                "card_expiry_year": None,
                "card_expiry_month": None,
                "total_amount": amount + x_amount,
                "project_list": [],
                "order_no": order_no,
                "verify_code": None,
                "verify_seq": None
            }
        }

        for four_element_key, four_element_value in self.__get_four_element_key__(repay_card).items():
            active_request_data['data'][four_element_key] = card_info[four_element_value]
        amount_info_list = [(item_no, amount, item_no_priority, None, None, coupon_dict[item_no]),
                            (item_no_x, x_amount, item_no_x_priority, None, None, coupon_dict[item_no_x])]
        amount_info_key = ("project_num", "amount", "priority", "coupon_num", "coupon_amount", "coupon_list")
        for amount_info in amount_info_list:
            if amount_info[1] != 0:
                active_request_data['data']['project_list'].append(dict(zip(amount_info_key, amount_info)))
        return active_request_data

    def get_repay_card_by_item_no(self, item_no):
        sql = "select card_acc_id_num_encrypt, card_acc_num_encrypt, card_acc_tel_encrypt, " \
              "card_borrower_uuid as card_acc_name_encrypt " \
              "from card join card_asset on card_no = card_asset_card_no where " \
              "card_asset_asset_item_no='{0}'and card_asset_type = 'repay'".format(item_no)
        id_num_info = self.db_session.execute(sql)
        return id_num_info[0] if id_num_info else ''

    def get_four_element(self):
        four_element = {
                "borrower_uuid": "400486{0}".format(time.time()).split(".")[0],
                "id_num": "enc_02_4248611931357196288_648",
                "mobile": "enc_01_4248611560530391040_253",
                "borrower_card_uuid": "400488{0}".format(time.time()).split(".")[0],
                "individual_uuid": "400488{0}".format(time.time()).split(".")[0],
        }

        return four_element

    def auto_loan(self, channel, period, days, amount, source_type, joint_debt_item='', x_item_no=False
                  , from_app='phi011', withdraw_type='online'):
        element = self.get_debt_item_card(joint_debt_item)
        asset_info, old_asset, item_no = self.grant.asset_import(channel, period, days, "day", amount, self.country,
                                                                 from_app, source_type, element, withdraw_type)
        print('item_no:', item_no)
        x_item_no = 'no_loan_{0}'.format(item_no) if x_item_no else ''
        import_asset_info = self.grant.asset_import_success(asset_info)
        withdraw_success_data = self.grant.get_withdraw_success_data(item_no, old_asset, x_item_no, asset_info,
                                                                     element=element)
        self.grant.asset_withdraw_success(withdraw_success_data)
        capital_data = self.grant.get_capital_asset_data(item_no)
        self.grant.capital_asset_success(capital_data)
        # 判断是否有小单
        if x_item_no:
            no_asset_info, no_old_asset = self.grant.asset_no_loan_import(asset_info, import_asset_info, item_no,
                                                                          x_item_no, source_type + "_split", element)
            self.grant.asset_import_success(no_asset_info)
            withdraw_success_data_no = self.grant.get_withdraw_success_data(x_item_no, no_old_asset, item_no,
                                                                            no_asset_info, element=element)
            self.grant.asset_withdraw_success(withdraw_success_data_no)
            self.run_msg_by_order_no(x_item_no, 'AssetWithdrawSuccess')
        self.add_asset(item_no, 0)
        return item_no, x_item_no

    @time_print
    def sync_plan_to_bc(self, item_no):
        self.run_xxl_job('manualSyncAsset', param={"assetItemNo": [item_no]})
        self.run_task_by_order_no(item_no, 'AssetAccountChangeNotify')
        self.run_msg_by_order_no(item_no, 'AssetChangeNotifyMQ')

    @query_withhold
    def active_repay(self, item_no, payment_type, amount=0, x_amount=0, period_start=None, period_end=None,
                     coupon_list=''):
        asset_tran = self.db_session.query(AssetTran).filter(AssetTran.asset_tran_asset_item_no == item_no).all()
        max_period = asset_tran[-1].asset_tran_period
        is_overdue = False if self.cal_days(self.get_date(), asset_tran[-1].asset_tran_due_at) > 0 else True
        item_no_x = self.get_no_loan(item_no) if item_no else ''
        if not item_no:
            raise ValueError('need item_no or item_no_rights one is not null!')
        amount = self.__get_repay_amount__(amount, item_no, period_start, period_end, max_period, is_overdue)
        x_amount = self.__get_repay_amount__(x_amount, item_no_x, period_start, period_end, max_period, is_overdue)

        if amount == 0 and x_amount == 0:
            return "当前已结清", "", []
        request_data = self.__get_active_request_data__(item_no, item_no_x, amount, x_amount, 1, payment_type,
                                                        coupon_list=coupon_list)
        print(json.dumps(request_data))
        resp = Http.http_post(self.active_repay_url, request_data)
        return request_data, self.active_repay_url, resp

    def repay_callback(self, serial_no, status, back_amount=0, refresh_type=None, max_create_at=None, item_no=None):
        withhold = self.db_session.query(Withhold).filter(Withhold.withhold_serial_no == serial_no).first()
        if not withhold:
            raise ValueError('代扣记录不存在')
        back_amount = back_amount if back_amount else withhold.withhold_amount
        channel = withhold.withhold_channel if \
            withhold.withhold_channel and \
            withhold.withhold_channel not in ('lanzhou_haoyue', 'hami_tianshan') else 'baofu_4_baidu'
        key = self.__create_req_key__(item_no, prefix='CallBack')
        req_data = {
            "from_system": "paysvr",
            "key": key,
            "type": "withhold",
            "data": {
                "amount": back_amount,
                "platform_code": "E20000",
                "payment_mode": "CREDIT_CARD",
                "merchant_key": serial_no,
                "channel_name": channel,
                "channel_key": serial_no,
                "finished_at": self.get_date(is_str=True, timezone=pytz.timezone(TIMEZONE[self.country])),
                "status": status,
                "channel_message": "交易成功" if status == 2 else '交易失败'
            }
        }
        resp = Http.http_post(self.pay_svr_callback_url, req_data)
        if resp['code'] != 0:
            raise ValueError('执行回调接口失败，返回:{0}'.format(resp))
        if refresh_type is not None:
            return self.info_refresh(item_no, refresh_type=refresh_type, max_create_at=max_create_at)
        return req_data, self.pay_svr_callback_url, resp

    def test(self):
        req_list = []
        amount = ['21000', '14000', '7000']

        for index, item_no in enumerate(('S20221648633013', 'S20221648633026')):
            key = self.__create_req_key__(item_no, prefix='CallBack')
            channel_key = self.__create_req_key__("test", prefix='channel_')
            req_data = {
                "from_system": "paysvr",
                "key": key,
                "type": "withhold",
                "data": {
                    "amount": amount[index],
                    "merchant_key": channel_key,
                    "status": "2",
                    "finished_at": self.get_date(is_str=True, timezone=pytz.timezone(TIMEZONE[self.country])),
                    "channel_key": channel_key,
                    "channel_name": "pandapay_alibey_collect",
                    "from_system": None,
                    "platform_message": "OK",
                    "platform_code": "E20000",
                    "payment_mode": "",
                    "account_no": "test"
                },
                "sync_datetime": None,
                "busi_key": "e82c588cb1fc4885be15b19c130f33f2"
            }
            req_list.append((item_no, req_data, channel_key))
        for item_no, req_data, channel_key in req_list:
            Http.http_post(self.pay_svr_offline_callback_url, req_data)

        for item_no, req_data, channel_key in req_list:
            try:
                self.run_task_by_order_no(channel_key, 'offline_withhold_process')
            except:
                continue

    def repay_offline_callback(self, item_no, item_type, back_amount=0, refresh_type=None, max_create_at=None):
        asset = self.db_session.query(Asset).filter(Asset.asset_item_no == item_no).first()
        if asset is None:
            raise ValueError('not found the asset!')
        account_no = item_no
        if not item_type:
            asset_x = self.get_no_loan(item_no)
            if not asset_x:
                raise ValueError('not found the asset!')
            account_no = asset_x
        back_amount = back_amount if back_amount else asset.asset_balance_amount
        key = self.__create_req_key__(item_no, prefix='OfflineCallBack')
        channel_key = self.__create_req_key__(item_no, prefix='channel_')
        req_data = {
            "from_system": "paysvr",
            "key": key,
            "type": "withhold",
            "data": {
                "amount": back_amount,
                "merchant_key": channel_key,
                "status": "2",
                "finished_at": self.get_date(is_str=True, timezone=pytz.timezone(TIMEZONE[self.country])),
                "channel_key": channel_key,
                "channel_name": "pandapay_alibey_collect",
                "from_system": None,
                "platform_message": "OK",
                "platform_code": "E20000",
                "payment_mode": "",
                "account_no": account_no
            },
            "sync_datetime": None,
            "busi_key": "e82c588cb1fc4885be15b19c130f33f2"
        }
        resp = Http.http_post(self.pay_svr_offline_callback_url, req_data)
        if resp['code'] != 0:
            raise ValueError('执行回调接口失败，返回:{0}'.format(resp))
        self.run_task_by_order_no(channel_key, 'offline_withhold_process')
        # self.run_task_by_order_no(channel_key, 'withhold_callback_process')
        if refresh_type is not None:
            return self.info_refresh(item_no, refresh_type=refresh_type, max_create_at=max_create_at)
        return req_data, self.pay_svr_callback_url, resp
