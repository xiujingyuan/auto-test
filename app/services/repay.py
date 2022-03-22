import copy
import importlib
from functools import reduce

from sqlalchemy import desc

from app import db
from app.common.http_util import Http
from app.model.Model import AutoAsset
from app.services import BaseService, Asset, Task, AssetExtend, time_print, CapitalAsset, AssetTran, CapitalTransaction
from app.services.china.repay import modify_return, WithholdOrder
from app.services.china.repay.Model import WithholdRequest, Withhold, SendMsg, \
    AssetOperationAuth, WithholdAssetDetailLock


class RepayBaseService(BaseService):
    def __init__(self, country, env, run_env, check_req, return_req):
        super(RepayBaseService, self).__init__(country, 'repay', env, run_env, check_req, return_req)
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
        self.bc_query_asset_url = self.repay_host + '/paydayloan/projectRepayQuery'

    def get_withhold_key_info(self, item_no, request_no=None, req_key=None, max_create_at=None):
        item_no_x = self.get_no_loan(item_no)
        max_create_at = max_create_at if max_create_at is not None else self.get_date(is_str=True, days=-7)
        item_no_tuple = tuple(filter(lambda x: x, (item_no, item_no_x)))
        withhold_order_list = self.db_session.query(WithholdOrder).filter(
            WithholdOrder.withhold_order_reference_no.in_(item_no_tuple),
            WithholdOrder.withhold_order_create_at >= max_create_at).\
            order_by(WithholdOrder.withhold_order_create_at).all()
        withhold_order = []
        if request_no is not None:
            withhold_order = list(filter(lambda x: x.withhold_order_request_no in request_no, withhold_order_list))
        if req_key is not None:
            withhold_order = list(filter(lambda x: x.withhold_order_req_key == req_key, withhold_order_list))
        if not withhold_order:
            withhold_order = list(filter(lambda x: x.withhold_order_withhold_status == 'ready', withhold_order_list))
        if not withhold_order and withhold_order_list:
            max_request_no = withhold_order_list[-1].withhold_order_request_no
            max_serial_no = withhold_order_list[-1].withhold_order_serial_no
            if max_serial_no.startswith("PROV_"):
                second_request_no = withhold_order_list[-2].withhold_order_request_no
                request_tuple = (max_request_no, second_request_no)
                withhold_order = list(
                    filter(lambda x: x.withhold_order_request_no in request_tuple, withhold_order_list))
            else:
                withhold_order = list(filter(lambda x: x.withhold_order_request_no == max_request_no,
                                             withhold_order_list))
        request_no_tuple = tuple(map(lambda x: x.withhold_order_request_no, withhold_order))
        serial_no_tuple = tuple(map(lambda x: x.withhold_order_serial_no, withhold_order))
        id_num_encrypt_tuple = (self.get_repay_card_by_item_no(item_no)['card_acc_id_num_encrypt'], )
        withhold_order = list(map(lambda x: x.to_spec_dict, withhold_order))
        return request_no_tuple, serial_no_tuple, id_num_encrypt_tuple, item_no_tuple, withhold_order

    def get_active_card_info(self, item_no, repay_card):
        card_info = self.get_repay_card_by_item_no(item_no)
        random_card = self.get_four_element()['data']
        if repay_card == 1:
            # 1-还款卡还款
            return card_info
        elif repay_card == 0:
            # 0-还款人身份证相同银行卡不同;
            card_info['card_acc_num_encrypt'] = random_card['bank_code_encrypt']
            # card_info['card_acc_num_encrypt'] = 'enc_03_2953903355913046016_400'
            return card_info
        elif repay_card == 2:
            # 2-还款人身份证相同银行卡都不同;
            random_card['bank_code_encrypt'] = 'enc_03_2953903355913046016_400'
            return random_card

    @modify_return
    def get_withhold(self, withhold_serial_no, max_create_at):
        withhold_list = self.db_session.query(Withhold).filter(
            Withhold.withhold_serial_no.in_(withhold_serial_no),
            Withhold.withhold_create_at >= max_create_at).all()
        return withhold_list

    @modify_return
    def get_withhold_request(self, withhold_request_no, max_create_at):
        withhold_request_list = self.db_session.query(WithholdRequest).filter(
            WithholdRequest.withhold_request_no.in_(withhold_request_no),
            WithholdRequest.withhold_request_create_at >= max_create_at).all()
        return withhold_request_list

    @modify_return
    def get_card_bind(self, withhold_serial_no, max_create_at):
        meta_class = importlib.import_module('app.services.{0}.repay.Model'.format(self.country))
        CardBind = getattr(meta_class, "CardBind")
        card_bind_list = self.db_session.query(CardBind).filter(
            CardBind.card_bind_serial_no.in_(withhold_serial_no),
            CardBind.card_bind_create_at >= max_create_at).all()
        return card_bind_list

    @modify_return
    def get_withhold_detail(self, withhold_serial_no, max_create_at):
        meta_class = importlib.import_module('app.services.{0}.repay.Model'.format(self.country))
        WithholdDetail = getattr(meta_class, "WithholdDetail")
        withhold_detail_list = self.db_session.query(WithholdDetail).filter(
            WithholdDetail.withhold_detail_serial_no.in_(withhold_serial_no),
            WithholdDetail.withhold_detail_create_at >= max_create_at).all()
        return withhold_detail_list

    def get_withhold_info(self, item_no, max_create_at, request_no=None, req_key=None):
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
        withhold_dict = self.get_withhold(serial_no_tuple, max_create_at)
        withhold_detail_dict = self.get_withhold_detail(serial_no_tuple, max_create_at)
        withhold_request_dict = self.get_withhold_request(serial_no_tuple, max_create_at)
        ret = {'withhold_order': withhold_order_list}
        ret.update(withhold_dict)
        ret.update(withhold_detail_dict)
        ret.update(withhold_request_dict)
        return ret

    def del_row_data(self, item_no, del_id, del_type, max_create_at=None):
        if del_type.startswith('biz_'):
            self.biz_central.delete_row_data(del_id, del_type[4:])
        else:
            obj = eval(del_type.title().replace("_", ""))
            self.db_session.query(obj).filter(getattr(obj, '{0}_id'.format(del_type)) == del_id).delete()
            self.db_session.flush()
            self.db_session.commit()
        return self.info_refresh(item_no, max_create_at=max_create_at, refresh_type=del_type)

    def modify_row_data(self, item_no, modify_id, modify_type, modify_data, max_create_at=None):
        if modify_type.startswith('biz_'):
            self.biz_central.modify_row_data(modify_id, modify_type[4:], modify_data)
        else:
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

    def run_task_by_id(self, task_id, max_create_at=None, item_no=None):
        ret = super(RepayBaseService, self).run_task_by_id(task_id)
        if max_create_at is not None:
            return self.info_refresh(item_no, max_create_at=max_create_at, refresh_type="task")
        return ret

    def run_msg_by_id(self, msg_id, max_create_at=None, item_no=None):
        ret = super(RepayBaseService, self).run_msg_by_id(msg_id)
        if max_create_at is not None:
            return self.info_refresh(item_no, max_create_at=max_create_at, refresh_type='msg')
        return ret

    def reverse_item_no(self, item_no, serial_no, max_create_at=None):
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
        order_info = self.db_session.query(WithholdOrder).filter(WithholdOrder.withhold_order_serial_no == serial_no,
                                                                 WithholdOrder.withhold_order_reference_no == item_no
                                                                 ).first()
        if not order_info:
            raise ValueError('withhold not found !')
        withhold_info = self.db_session.query(Withhold).filter(Withhold.withhold_serial_no == serial_no).first()
        req_data['data']['serial_no'] = withhold_info.withhold_channel_key
        resp = Http.http_post(self.reverse_url, req_data)
        if max_create_at is not None:
            info_ret = self.info_refresh(item_no, max_create_at=max_create_at, refresh_type='withhold')
            info_ret['request'] = req_data
            info_ret['response'] = resp
            info_ret['request_url'] = self.refresh_url
            return info_ret
        return dict(zip(('request', 'response', 'request_url'), (req_data, self.refresh_url, resp)))

    def set_asset_tran_status(self, period, item_no, status='finish'):
        if not period or not item_no:
            raise ValueError('period or item_no can not be none!')
        if status not in ('finish', 'nofinish'):
            raise ValueError('status error, only finish, nofinish!')
        item_no_x = self.get_no_loan(item_no)
        asset = self.db_session.query(Asset).filter(Asset.asset_item_no == item_no).first()
        if item_no_x:
            asset_x = self.db_session.query(Asset).filter(Asset.asset_item_no == item_no_x).first()
            asset_x.asset_status = 'repay'
            asset_x.asset_actual_grant_at = '1000-01-01 00:00:00'
            asset_x.asset_balance_amount = asset_x.asset_repaid_amount = 0
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

    def get_lock_info(self, item_no):
        item_no_x = self.get_no_loan(item_no)
        auth_lock = self.db_session.query(AssetOperationAuth).filter(
            AssetOperationAuth.asset_operation_auth_asset_item_no.in_((item_no, item_no_x))).all()
        auth_lock = list(map(lambda x: x.to_spec_dict, auth_lock))
        detail_lock = self.db_session.query(WithholdAssetDetailLock).filter(
            WithholdAssetDetailLock.withhold_asset_detail_lock_asset_item_no.in_((item_no, item_no_x))).all()
        detail_lock = list(map(lambda x: x.to_spec_dict, detail_lock))
        return dict(zip(('auth_lock', 'detail_lock'), (auth_lock, detail_lock)))

    @time_print
    def run_msg_by_order_no(self, order_no, sendmsg_type, excepts={"code": 0}):
        msg = self.db_session.query(SendMsg).filter(SendMsg.sendmsg_order_no == order_no,
                                                    SendMsg.sendmsg_status == 'open',
                                                    SendMsg.sendmsg_type == sendmsg_type).order_by(
            desc(SendMsg.sendmsg_create_at)).first()
        if msg:
            return self.run_msg_by_id(msg.sendmsg_id)

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
                                    repay_card, item_no_priority=12, item_no_rights_priority=5,
                                    item_no_x_priority=1, coupon_num=None, coupon_amount=None, order_no='',
                                    verify_code='', verify_seq=''):
        # card_info = self.get_active_card_info('item_no_1634196466', repay_card)
        if repay_card == 3:
            card_info = self.get_active_card_info('B2021102108114492056', 1)
        else:
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
    def get_task(self, task_order_no, max_create_at):
        task_list = self.db_session.query(Task).filter(
            Task.task_order_no.in_(task_order_no),
            Task.task_id >= max_create_at).order_by(desc(Task.task_id)).all()
        task_list = list(map(lambda x: x.to_spec_dict, task_list))
        return {'task': task_list}

    @time_print
    def get_msg(self, task_order_no, max_create_at):
        msg_list = self.db_session.query(SendMsg).filter(
            SendMsg.sendmsg_order_no.in_(task_order_no),
            SendMsg.sendmsg_id >= max_create_at).order_by(desc(SendMsg.sendmsg_id)).all()
        msg_list = list(map(lambda x: x.to_spec_dict, msg_list))
        return {'msg': msg_list}

    @time_print
    def info_refresh(self, item_no, max_create_at=None, refresh_type=None):
        asset = self.get_asset(item_no)
        max_create_at = self.get_date(is_str=True, days=-3)
        request_no, serial_no, id_num, item_no_tuple, withhold_order = \
            self.get_withhold_key_info(item_no, max_create_at=max_create_at)
        channel = asset['asset'][0]['loan_channel']
        task_order_no = tuple(list(request_no) + list(serial_no) + list(id_num) + list(item_no_tuple)
                              + [channel])
        ret = {}
        if refresh_type in ('task', 'msg'):
            ret = getattr(self, 'get_{0}'.format(refresh_type))(task_order_no, max_create_at)
        elif refresh_type == 'biz_task':
            ret = self.biz_central.get_task(task_order_no, channel, max_create_at)
        elif refresh_type == 'biz_msg':
            ret = self.biz_central.get_msg(item_no, max_create_at)
        elif refresh_type in ('withhold', 'withhold_detail', 'card_bind'):
            ret = getattr(self, 'get_{0}'.format(refresh_type))(serial_no, max_create_at)
        elif refresh_type == 'withhold_order':
            ret = {'withhold_order': withhold_order}
        elif refresh_type == 'withhold_request':
            ret = self.get_withhold_request(request_no, max_create_at)
        elif refresh_type == 'asset_tran':
            ret = getattr(self, 'get_{0}'.format(refresh_type))(item_no)
        elif refresh_type in ('biz_capital', 'biz_capital_tran', 'biz_capital_notify'):
            ret = getattr(self.biz_central, 'get_{0}'.format(refresh_type[4:]))(item_no)
        elif refresh_type == 'biz_capital_settlement_detail':
            ret = self.biz_central.get_capital_settlement_detail(channel)
        elif refresh_type in ('auth_lock', 'detail_lock'):
            ret = self.get_lock_info(item_no)
        ret.update(asset)
        return ret

    def get_repay_card_by_item_no(self, item_no):
        sql = "select card_acc_id_num_encrypt, card_acc_num_encrypt, card_acc_tel_encrypt, card_acc_name_encrypt " \
              "from card join card_asset on card_no = card_asset_card_no where " \
              "card_asset_asset_item_no='{0}'and card_asset_type = 'repay'".format(item_no)
        id_num_info = self.db_session.execute(sql)
        return id_num_info[0] if id_num_info else ''

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
        asset['repay_card'] = four_ele['card_acc_num_encrypt']
        asset['item_x'] = self.get_no_loan(item_no)
        return {'asset': [asset]}

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

    def get_auto_asset(self, channel, period, days=0):
        asset_list = AutoAsset.query.filter(AutoAsset.asset_period == period,
                                            AutoAsset.asset_channel == channel,
                                            AutoAsset.asset_days == days,
                                            AutoAsset.asset_env == self.env,
                                            AutoAsset.asset_country == self.country,
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
            return '该资产已经存在'
        asset = AutoAsset()
        asset.asset_create_at = self.get_date(fmt="%Y-%m-%d", is_str=True)
        asset.asset_channel = repay_asset.asset_loan_channel if repay_asset is not None else\
            grant_asset.asset_loan_channel
        asset.asset_descript = ''
        asset.asset_name = name
        asset.asset_period = repay_asset.asset_period_count if repay_asset is not None else \
            grant_asset.asset_loan_channel
        asset.asset_env = self.env
        asset.asset_type = source_type
        asset.asset_country = self.country
        asset.asset_source_type = 1
        asset.asset_days = int(repay_asset.asset_product_category)
        db.session.add(asset)
        db.session.flush()
        return self.get_auto_asset(repay_asset.asset_loan_channel, repay_asset.asset_period_count,
                                   days=int(repay_asset.asset_product_category))

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
            self.run_msg_by_order_no(asset_x, 'assetFoxSync')
        self.run_task_by_type_and_order_no('AssetAccountChangeNotify', item_no)
        self.run_msg_by_order_no(item_no, 'AssetChangeNotifyMQ')
        self.run_msg_by_order_no(item_no, 'assetFoxSync')
        return [request_data, request_x_data] if asset_x else [request_data], self.refresh_url, [resp, resp_x] \
            if asset_x else [resp]

    def run_task_by_type_and_order_no(self, task_type, order_no):
        task_list = self.db_session.query(Task).filter(Task.task_type == task_type,
                                                       Task.task_order_no == order_no,
                                                       Task.task_status == 'open').all()
        for task in task_list:
            self.run_task_by_id(task.task_id)

    @time_print
    def sync_plan_to_bc(self, item_no):
        now = self.get_date(is_str=True, fmt='%Y-%m-%d')
        self.run_xxl_job('syncAssetToBiz', param={'assetItemNo': [item_no]})
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

    @time_print
    def change_asset(self, item_no, item_no_rights, advance_day, advance_month, interval_day=30):
        item_no_tuple = tuple(item_no.split(',')) if ',' in item_no else (item_no,)
        for index, item in enumerate(item_no_tuple):

            item_no_x = self.get_no_loan(item)
            item_tuple = tuple([x for x in [item, item_no_x, item_no_rights] if x])
            asset_list = self.db_session.query(Asset).filter(Asset.asset_item_no.in_(item_tuple)).all()
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
        self.refresh_late_fee(item_no)
        self.refresh_late_fee(item_no_rights)
        self.sync_plan_to_bc(item_no)
        return "修改完成"


TIMEZONE = {
    'mex': 'Mexico/General',
    'tha': 'Asia/Bangkok',
    'phl': 'Asia/Shanghai',
    'ind': 'Asia/Kolkata'
}


class OverseaRepayService(RepayBaseService):
    def __init__(self, country, env, run_env, check_req=False, return_req=False):
        super(OverseaRepayService, self).__init__(country, env, run_env, check_req, return_req)
        self.encrypt_url = 'http://47.101.30.198:8081/encrypt/'
        self.capital_asset_success_url = self.repay_host + '/capital-asset/grant'

    def get_repay_card_by_item_no(self, item_no):
        sql = "select card_acc_id_num_encrypt, card_acc_num_encrypt, card_acc_tel_encrypt, " \
              "card_borrower_uuid as card_acc_name_encrypt " \
              "from card join card_asset on card_no = card_asset_card_no where " \
              "card_asset_asset_item_no='{0}'and card_asset_type = 'repay'".format(item_no)
        id_num_info = self.db_session.execute(sql)
        return id_num_info[0] if id_num_info else ''

    def get_four_element(self):
        four_element = super(OverseaRepayService, self).get_four_element()
        response = {
            "code": 0,
            "message": "success",
            "data": {
                "bank_account": four_element["data"]["bank_code"],
                "card_num": four_element["data"]["bank_code"],
                "mobile": four_element["data"]["phone_number"],
                "user_name": "Craltonliu",
                "id_number": four_element["data"]["id_number"],
                "address": "Floor 8 TaiPingYang Building TianFuSanGai Chengdu,Sichuan,China",
                "email": four_element["data"]["phone_number"] + "@qq.com",
                "upi": four_element["data"]["phone_number"] + "@upi"
            }
        }
        data = [{"type": 1, "plain": response["data"]["mobile"]},
                {"type": 2, "plain": response["data"]["id_number"]},
                {"type": 3, "plain": response["data"]["card_num"]},
                {"type": 3, "plain": response["data"]["upi"]},
                {"type": 4, "plain": response["data"]["user_name"]},
                {"type": 5, "plain": response["data"]["email"]},
                {"type": 6, "plain": response["data"]["address"]}]
        resp = Http.http_post(url=self.encrypt_url, req_data=data)
        response["data"]["mobile_encrypt"] = resp["data"][0]["hash"]
        response["data"]["id_number_encrypt"] = resp["data"][1]["hash"]
        response["data"]["card_num_encrypt"] = resp["data"][2]["hash"]
        response["data"]["upi_encrypt"] = resp["data"][3]["hash"]
        response["data"]["user_name_encrypt"] = resp["data"][4]["hash"]
        response["data"]["email_encrypt"] = resp["data"][5]["hash"]
        response["data"]["address_encrypt"] = resp["data"][6]["hash"]
        response["data"]["bank_account_encrypt"] = resp["data"][2]["hash"]
        return response

    def auto_loan(self, channel, period, days, amount, source_type, joint_debt_item = ''
                  , from_app='phi011', withdraw_type='online'):
        element = self.get_four_element()
        if joint_debt_item:
            joint_debt_asset = self.db_session.query(Asset).filter(Asset.asset_item_no == joint_debt_item).first()
            if joint_debt_asset:
                raise ValueError('not fount the joint_debt_asset')
            joint_debt_asset = self.get_repay_card_by_item_no(joint_debt_asset)
            element["data"]["id_number_encrypt"] = joint_debt_asset['card_acc_id_num_encrypt']
            element["data"]["card_num_encrypt"] = joint_debt_asset['card_acc_num_encrypt']
            element["data"]["bank_account_encrypt"] = joint_debt_asset['card_acc_num_encrypt']
            element["data"]["mobile_encrypt"] = joint_debt_asset['card_acc_tel_encrypt']
            element["data"]["user_name_encrypt"] = joint_debt_asset['card_borrower_uuid']

        asset_info, old_asset, item_no = self.grant.asset_import(channel, period, days, "day", amount, self.country,
                                                                 from_app, source_type, element, withdraw_type)
        print('item_no:', item_no)
        x_item_no = ''
        import_asset_info = self.grant.asset_import_success(asset_info)
        withdraw_success_data = self.grant.get_withdraw_success_data(item_no, old_asset, x_item_no, asset_info, element)
        self.grant.asset_withdraw_success(withdraw_success_data)
        capital_data = self.grant.get_capital_asset_data(item_no)
        self.grant.capital_asset_success(capital_data)
        # 判断是否有小单
        if x_item_no:
            self.noloan_to_success(x_item_no)
        self.add_asset(item_no, 0)
        return item_no, x_item_no

    @time_print
    def sync_plan_to_bc(self, item_no):
        self.run_xxl_job('manualSyncAsset', param={"assetItemNo": [item_no]})
        self.run_task_by_order_no(item_no, 'AssetAccountChangeNotify')
        self.run_msg_by_order_no(item_no, 'AssetChangeNotifyMQ')