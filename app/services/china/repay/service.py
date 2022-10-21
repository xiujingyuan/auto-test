import copy
import importlib
import json
import time
from datetime import datetime
from decimal import Decimal

from app.common.http_util import Http, FORM_HEADER
from app.model.Model import BackendKeyValue
from app.services.repay import RepayBaseService
from app.services.china.biz_central.service import ChinaBizCentralService
from app.services.china.grant.service import ChinaGrantService
from app.services.china.repay import query_withhold
from app.services.china.repay.Model import Asset, AssetExtend, Task, WithholdOrder, AssetTran, \
    SendMsg, Withhold, Card, CardAsset, \
    WithholdRequest, WithholdDetail, Individual, IndividualAsset


class ChinaRepayService(RepayBaseService):
    def __init__(self, env, run_env, mock_name, check_req=False, return_req=False):
        self.repay_host = "http://repay{0}.k8s-ingress-nginx.kuainiujinke.com".format(env)
        super(ChinaRepayService, self).__init__('china', env, run_env, mock_name, check_req, return_req)
        self.grant = ChinaGrantService(env, run_env, mock_name, check_req, return_req)
        self.biz_central = ChinaBizCentralService(env, run_env, mock_name, check_req, return_req)

    def operate_action(self, item_no, extend, op_type, table_name, run_date):
        req = {'max_create_at': extend['create_at'] if hasattr(extend, 'create_at') else None,
                'item_no': item_no,
               'refresh_type': table_name
               }
        if op_type == 'reverse_item_no':
            req['serial_no'] = extend['serial_no']
        elif op_type in ("run_task_by_id", "run_msg_by_id"):
            req[op_type.split("_")[1] + '_id'] = extend['id']
        elif op_type in ('run_biz_task', 'run_biz_msg'):
            req['re_run'] = True
            req['re_date'] = run_date
            req[op_type.split("_")[-1] + '_id'] = extend['id']
        elif op_type == "del_row_data":
            req['del_id'] = extend['id']
        elif op_type.startswith('repay_callback_'):
            req['serial_no'] = extend['serial_no']
            req['status'] = 3 if op_type.endswith('fail') else 2
            op_type = 'repay_callback'
        return getattr(self, op_type)(**req)

    def calc_qinnong_early_settlement(self, item_no):
        param = {
            'project_num': item_no,
            "project_type": "paydayloan"
        }
        req = Http.http_get(self.bc_query_asset_url, req_data=param, headers=FORM_HEADER)
        total_amount, decrease_amount, repaid_amount = 0, 0, 0
        for fee_type in req['data'].keys():
            for _, value in req['data'][fee_type].items():
                total_amount += value['amount']
                repaid_amount += value['repaid_amount']
                decrease_amount += value['advance_repay_decrease_amount']
        return total_amount - decrease_amount - repaid_amount

    def auto_loan(self, channel, period, amount, source_type, from_system_name='香蕉', days=0, joint_debt_item=''):
        """
        自动放款
        :param channel:
        :param period:
        :param amount:
        :param source_type:
        :param from_system_name:
        :param joint_debt_item:
        :param days:
        :return:
        """
        self.log.log_info("rbiz_loan_tool_auto_import...env=%s, channel_name=%s" % (self.env, channel))
        element = self.get_debt_item_card(joint_debt_item)
        # item_no 大单, x_item_no 小单, x_rights 权益单
        # item_no, x_item_no, x_rights = '20201630050959854539', '', ''
        item_no, x_item_no, x_rights, source_type, x_source_type, x_right, from_system = \
            self.grant.get_asset_item_info(channel, source_type, from_system_name)
        # 大单
        asset_info, old_asset = self.grant.asset_import(item_no, channel, element, period, amount, source_type,
                                                        from_system_name, from_system, x_item_no)
        import_asset_info = self.grant.asset_import_success(asset_info)
        withdraw_success_data = self.grant.get_withdraw_success_data(item_no, old_asset, x_item_no, asset_info)
        self.grant.asset_withdraw_success(withdraw_success_data)
        self.run_msg_by_type_and_order_no(item_no, 'AssetWithdrawSuccess', timeout=1)
        capital_data = self.grant.get_capital_asset_data(item_no)
        self.grant.capital_asset_success(capital_data)

        # 小单
        try:
            x_list = (x_source_type, x_right)
            for index, x_asset in enumerate((x_item_no, x_rights)):
                if x_asset:
                    no_asset_info, no_old_asset = self.grant.asset_no_loan_import(asset_info, import_asset_info, item_no,
                                                                                  x_asset, x_list[index])
                    self.grant.asset_import_success(no_asset_info)
                    withdraw_success_data_no = self.grant.get_withdraw_success_data(x_asset, no_old_asset, item_no,
                                                                                    no_asset_info)
                    self.grant.asset_withdraw_success(withdraw_success_data_no)
                    self.run_msg_by_type_and_order_no(x_asset, 'AssetWithdrawSuccess')
        except Exception as e:
            print(e)
            print('小单放款失败')
        self.add_asset(item_no, 0)
        return item_no, x_item_no

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

    @staticmethod
    def get_mock_obj(project, channel, asset, asset_extend, at_list, period_start, period_end):
        meta_class = importlib.import_module('app.services.capital_service.{0}'.format(channel))
        capital_mock = getattr(meta_class, channel.replace("_", "").title() + 'Mock')(project, asset, asset_extend,
                                                                                      at_list, period_start, period_end)
        return capital_mock

    def set_trail_mock(self, item_no, period_start, period_end, channel, status, principal_over=False,
                       interest_type='less'):
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
        asset, asset_extend, at_list = self.get_asset_info_record(item_no, period_start, period_end)
        capital_mock = self.get_mock_obj(self.mock_name, channel, asset, asset_extend, at_list, period_start, period_end)
        return capital_mock.repay_trail_mock(status, principal_over=principal_over, interest_type=interest_type)

    def get_asset_info_record(self, item_no, period_start,  period_end):
        asset = self.db_session.query(Asset).filter(Asset.asset_item_no == item_no).first()
        period_end = period_end if period_end is not None else asset.asset_period_count
        at_list = self.db_session.query(AssetTran).filter(
            AssetTran.asset_tran_period >= period_start,
            AssetTran.asset_tran_period <= period_end,
            AssetTran.asset_tran_asset_item_no == item_no).all()
        asset_extend = self.db_session.query(AssetExtend).filter(AssetExtend.asset_extend_asset_item_no == item_no,
                                                                 AssetExtend.asset_extend_type == 'trade_no').first()
        return asset, asset_extend, at_list

    def repay_query_interface(self, item_no, period_start, period_end, channel, success_type='PART'):
        """
        设置微神马试算金额
        :param item_no:资产编号
        :param period_start: 还款开始期次
        :param period_end: 还款到期期次
        :param channel: 资方
        :param success_type: PART
        :return: 无返回
        """
        asset, asset_extend, at_list = self.get_asset_info_record(item_no, period_start, period_end)
        capital_mock = self.get_mock_obj(self.mock_name, channel, asset, asset_extend, at_list, period_start, period_end)
        withhold = self.db_session.query(Withhold) \
            .join(WithholdOrder, WithholdOrder.withhold_order_request_no == Withhold.withhold_request_no) \
            .filter(WithholdOrder.withhold_order_reference_no == item_no,
                    Withhold.withhold_channel == channel,
                    Withhold.withhold_status.in_(('process', 'ready'))).first()

        withhold_detail = self.db_session.query(WithholdDetail).filter(
            WithholdDetail.withhold_detail_serial_no == withhold.withhold_serial_no).all()

        return capital_mock.repay_apply_query_mock(withhold, withhold_detail, success_type=success_type)

    def repay_plan_interface(self, item_no, channel):
        """
        设置微神马试算金额
        :param item_no:资产编号
        :param channel: 资方
        :return: 无返回
        """
        asset, asset_extend, at_list = self.get_asset_info_record(item_no, 1, None)
        capital_mock = self.get_mock_obj(self.mock_name, channel, asset, asset_extend, at_list, 1, None)
        return capital_mock.repay_plan_mock()

    def card_bind_query(self, item_no, period_start, period_end, channel, success_type='PART'):
        """
        设置微神马试算金额
        :param item_no:资产编号
        :param period_start: 还款开始期次
        :param period_end: 还款到期期次
        :param channel: 资方
        :param success_type: PART
        :return: 无返回
        """
        asset, asset_extend, at_list = self.get_asset_info_record(item_no, period_start, period_end)
        capital_mock = self.get_mock_obj(self.mock_name, channel, asset, asset_extend, at_list, period_start,
                                         period_end)
        withhold = self.db_session.query(Withhold) \
            .join(WithholdOrder, WithholdOrder.withhold_order_request_no == Withhold.withhold_request_no) \
            .filter(WithholdOrder.withhold_order_reference_no == item_no,
                    Withhold.withhold_channel == channel,
                    Withhold.withhold_status.in_(('process', 'ready'))).first()
        return capital_mock.card_bind_query_mock(withhold, success_type=success_type)

    def msg_send(self, item_no, period_start, period_end, channel, success_type='PART'):
        """
        设置微神马试算金额
        :param item_no:资产编号
        :param period_start: 还款开始期次
        :param period_end: 还款到期期次
        :param channel: 资方
        :param success_type: PART
        :return: 无返回
        """
        asset, asset_extend, at_list = self.get_asset_info_record(item_no, period_start, period_end)
        capital_mock = self.get_mock_obj(self.mock_name, channel, asset, asset_extend, at_list, period_start,
                                         period_end)
        backend_config = BackendKeyValue.query.filter(
            BackendKeyValue.backend_key == 'send_msg_code_config').first()
        backend_info = json.loads(backend_config.backend_value)[channel]
        return capital_mock.msg_send_mock(backend_info, success_type=success_type)

    def fix_id_num(self, item_no):
        individual = self.db_session.query(Individual.individual_id_num_encrypt, Individual.individual_name_encrypt,
                                           Individual.individual_tel_encrypt).join(IndividualAsset,
                                                                                   Individual.individual_no ==
                                                                                   IndividualAsset.individual_asset_individual_no
                                                                                   ).filter(
            IndividualAsset.individual_asset_asset_item_no == item_no).first()
        card = self.db_session.query(Card).join(CardAsset, Card.card_no == CardAsset.card_asset_card_no).filter(
                CardAsset.card_asset_asset_item_no == item_no
            ).first()
        card.card_acc_id_num_encrypt = individual.individual_id_num_encrypt
        card.card_acc_name_encrypt = individual.individual_name_encrypt
        card.card_acc_tel_encrypt = individual.individual_tel_encrypt
        self.db_session.add(card)
        self.db_session.commit()

    def add_and_update_holiday(self, date_time, status):
        return self.biz_central.add_and_update_holiday(date_time, status)

    def add_buyback(self, item_no, channel, period_start):
        super(ChinaRepayService, self).add_buyback(item_no, channel, period_start)
        return self.biz_central.add_buyback(item_no, period_start)

    def remove_buyback(self, item_no, channel):
        super(ChinaRepayService, self).remove_buyback(item_no, channel)
        return self.biz_central.remove_buyback(item_no, channel)

    def set_asset_tran_status(self, period, item_no, refresh_type=None, status='finish'):
        self.biz_central.set_capital_tran_status(item_no, period, operate_type='compensate')
        return super(ChinaRepayService, self).set_asset_tran_status(period, item_no, refresh_type, status=status)

    @query_withhold
    def active_repay(self, item_no, item_no_rights='', repay_card=1, amount=0, x_amount=0, rights_amount=0,
                     verify_code='', verify_seq=None, agree=False, protocol=False,
                     period_start=None, period_end=None, repay_card_num=None, bank_code='中国银行'):
        """
        主动还款
        :param item_no:
        :param item_no_rights:
        :param repay_card:
        :param amount:
        :param x_amount:
        :param rights_amount:
        :param verify_code:
        :param verify_seq:
        :param agree:
        :param protocol:
        :param period_start:
        :param period_end:
        :param bank_code:
        :return:
        """
        asset_tran = self.db_session.query(AssetTran).filter(AssetTran.asset_tran_asset_item_no == item_no).all()
        max_period = asset_tran[-1].asset_tran_period
        is_overdue = False if self.cal_days(self.get_date(), asset_tran[-1].asset_tran_due_at) > 0 else True
        item_no_x = self.get_no_loan(item_no) if item_no else ''
        if item_no_rights:
            rights_info = self.db_session.query(AssetExtend).filter(
                AssetExtend.asset_extend_asset_item_no == item_no_rights,
                AssetExtend.asset_extend_type == 'ref_order_type',
                AssetExtend.asset_extend_val == 'lieyin').first()
            if not rights_info:
                raise ValueError('The item {0} is not rights asset!'.format(item_no_rights))
        item_no_rights = self.get_right_item(item_no, item_no_x) if not item_no_rights else item_no_rights
        if not item_no and not item_no_rights:
            raise ValueError('need item_no or item_no_rights one is not null!')
        amount = self.__get_repay_amount__(amount, item_no, period_start, period_end, max_period, is_overdue)
        x_amount = self.__get_repay_amount__(x_amount, item_no_x, period_start, period_end, max_period, is_overdue)
        rights_amount = self.__get_repay_amount__(rights_amount, item_no_rights, period_start, period_end, max_period,
                                                  is_overdue)
        if amount == 0 and x_amount == 0 and rights_amount == 0:
            return "当前已结清", "", []
        request_data = self.__get_active_request_data__(item_no, item_no_x, item_no_rights, amount, x_amount,
                                                        rights_amount, repay_card, bank_code, verify_code=verify_code,
                                                        verify_seq=verify_seq, repay_card_num=repay_card_num)
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
            # agree_request_data['data']['verify_seq'] = verify_seq if protocol else 'error_test'
            agree_request_data['data']['verify_seq'] = 'error_test'
            time.sleep(2)
            agree_resp = Http.http_post(self.active_repay_url, agree_request_data)
            # 执行协议签约任务
            request_data = [request_data, agree_request_data]
            resp = [resp, agree_resp]
        return request_data, self.active_repay_url, resp

    def copy_asset(self, item_no, asset_import, capital_import, capital_data, withdraw_success, grant_msg, source_type):
        is_run = True
        for index, task in enumerate((asset_import, capital_import, withdraw_success)):
            if index == 2:
                is_run = False
            if task:
                task_id = self.biz_central.add_central_task(task, is_run)

        if capital_data:
            self.grant.capital_asset_success(capital_data)

        self.grant.add_msg(grant_msg)
        self.grant.asset_withdraw_success(json.loads(grant_msg['sendmsg_content'])['body'])
        self.biz_central.run_central_task_by_task_id(task_id)
        asset = self.check_item_exist(item_no)
        if asset.asset_loan_channel != 'noloan':
            return self.add_asset(item_no, source_type)
        return {}

    def get_withdraw_success_info(self, item_no, get_type='body'):
        msg = self.db_session.query(SendMsg).filter(SendMsg.sendmsg_order_no == item_no,
                                                    SendMsg.sendmsg_type == 'AssetWithdrawSuccess').first()
        return json.loads(msg.sendmsg_content)['body'] if get_type == 'body' else msg.to_dict

    def get_exist_asset_request(self, item_no):
        biz_task = self.biz_central.get_loan_asset_task(item_no)
        is_noloan = True if self.get_no_loan(item_no) else False
        grant_msg = self.grant.get_withdraw_success_info_from_db(item_no, get_type='msg')
        grant_task = self.grant.get_withdraw_success_info_task(item_no)
        capital_data = []
        if grant_msg is None:
            grant_msg = self.get_withdraw_success_info(item_no, get_type='msg')
            capital_data = self.grant.get_capital_asset_data(item_no)
        return dict(zip(('biz_task', 'grant_msg', 'is_noloan', 'capital_data'),
                        (biz_task, grant_msg, is_noloan, capital_data)))

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
        serial_no_list = []
        for task in task_list:
            self.run_task_by_id(task.task_id)
            serial_no = json.loads(task.task_request_data)['data']['rechargeSerialNo']
            serial_no_list.append(serial_no)

        for serial_no in list(set(serial_no_list)):
            while True:
                withhold_task = self.db_session.query(Task).filter(Task.task_type == 'withhold_order_sync',
                                                                   Task.task_order_no == serial_no).first()
                if withhold_task:
                    self.run_task_by_id(withhold_task.task_id)
                    break
        return req_data, self.decrease_url, repay_ret

    def offline_recharge_repay(self, item_no, amount, serial_no, period):
        req_data, offline_recharge_url, recharge_ret = self.offline_recharge(item_no, amount, serial_no)
        if recharge_ret['code'] == 0:
            offline_req, offline_repay_url, repay_ret = self.offline_repay(item_no, serial_no, period)
        else:
            offline_req, offline_repay_url, repay_ret = '', '', '线下还款失败'
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

    def repay_callback(self, serial_no, status, back_amount=0, refresh_type=None, max_create_at=None, item_no=None):
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
        if refresh_type is not None:
            return self.info_refresh(item_no, refresh_type=refresh_type, max_create_at=max_create_at)
        return req_data, self.pay_svr_callback_url, resp

    def run_callback_task_and_msg(self, serial_no, repay_status):
        withhold_order = self.db_session.query(WithholdOrder).filter(
            WithholdOrder.withhold_order_serial_no == serial_no).first()
        id_num_encrypt = self.get_repay_card_by_item_no(
            withhold_order.withhold_order_reference_no)['card_acc_id_num_encrypt']
        request_no = withhold_order.withhold_order_request_no
        self.run_task_by_type_and_order_no('withhold_callback_process', withhold_order.withhold_order_reference_no)
        if repay_status == 2:
            # 跑充值还款任务
            self.run_task_by_type_and_order_no('assetWithholdOrderRecharge', serial_no)
            self.run_task_by_type_and_order_no('AssetAccountChangeNotify', withhold_order.withhold_order_reference_no)
            self.run_msg_by_type_and_order_no(id_num_encrypt, 'account_change_tran_repay')
        self.run_task_by_type_and_order_no('withhold_order_sync', serial_no)
        self.run_task_by_type_and_order_no('execute_combine_withhold', request_no)
        self.run_msg_by_type_and_order_no(serial_no, 'WithholdResultImport')

    def run_msg_by_type_and_order_no(self, order_no, sendmsg_type, timeout=5):
        num = 0
        while True:
            msg_list = self.db_session.query(SendMsg).filter(SendMsg.sendmsg_type == sendmsg_type,
                                                             SendMsg.sendmsg_order_no == order_no).all()
            if msg_list:
                for msg in msg_list:
                    self.run_msg_by_id(msg.sendmsg_id)
                break
            time.sleep(1)
            num += 1
            if num > timeout:
                raise ValueError('not found the msg with order_no:{0}, type:{1}'.format(order_no, sendmsg_type))

    def run_task_by_order_no(self, order_no, task_type):
        for item_order in order_no:
            task = self.db_session.query(Task).filter(Task.task_order_no == item_order,
                                                      Task.task_type == task_type).first()
            if task:
                self.run_task_by_id(task.task_id)

    # def run_biz_task(self, task_id, run_date, re_run, max_create_at=None, item_no=None):
    #     ret = self.biz_central.run_central_task_by_task_id(task_id, run_date, re_run)
    #     if max_create_at is not None:
    #         return self.info_refresh(item_no, max_create_at=max_create_at, refresh_type='biz_task')
    #     return ret

    # def run_biz_msg(self, msg_id, max_create_at=None, item_no=None):
    #     ret = self.biz_central.run_central_msg_by_msg_id(msg_id)
    #     if max_create_at is not None:
    #         return self.info_refresh(item_no, max_create_at=max_create_at, refresh_type='biz_msg')
    #     return ret
    #
    # def run_biz_xxl_job(self, job_type, run_date, param):
    #     return self.biz_central.run_xxl_job(job_type, run_date, param)

    def run_crm_task_msg_by_item_no(self, item_no):
        item_no_x = self.get_no_loan(item_no)
        item_no_x_info = self.db_session.query(Asset).filter(Asset.asset_item_no == item_no_x).first()
        item_no_x_status = item_no_x_info.asset_status if item_no_x_info else ''
        item_list = (item_no, item_no_x) if item_no_x_status == 'repay' else (item_no,)
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
        asset_tran = self.db_session.query(AssetTran).filter(AssetTran.asset_tran_asset_item_no == item_no).all()
        max_period = asset_tran[-1].asset_tran_period
        is_overdue = False if self.cal_days(self.get_date(), asset_tran[-1].asset_tran_due_at) > 0 else True
        if amount == 0 and period_start is not None and period_end is not None:
            amount = self.__get_repay_amount__(amount, item_no, period_start, period_end, max_period, is_overdue)
        req_key = self.__create_req_key__(item_no, prefix='FOX')
        card_info = self.get_active_card_info(item_no, 1, '')
        fox_active_data = {
            "busi_key": "20190731061116179",
            "data": {
                "amount": amount,
                "asset_item_no": item_no,
                "asset_period": None,
                "customer_bank_card_encrypt": card_info['card_acc_num_encrypt'],
                "customer_bank_code": "CCB",
                "customer_mobile_encrypt": card_info['card_acc_tel_encrypt'],
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
        """
        自动批扣还款
        :param item_no:
        :return:
        """
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
