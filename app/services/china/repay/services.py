import copy
import json
import time

from functools import reduce
from sqlalchemy import desc
from app import db
from app.common.http_util import Http, FORM_HEADER
from app.common.tools import get_date
from app.model.Model import AutoAsset
from app.services import RepayBaseService
from app.services.china.biz_central.services import ChinaBizCentralService
from app.services.china.grant.services import ChinaGrantService
from app.services.china.repay import query_withhold, modify_return, time_print
from app.services.china.repay.Model import Asset, AssetExtend, Task, WithholdOrder, AssetTran, \
    SendMsg, Withhold, CapitalAsset, CapitalTransaction, Card, CardAsset, AssetOperationAuth, WithholdAssetDetailLock, \
    WithholdRequest, WithholdDetail, CardBind


class ChinaRepayService(RepayBaseService):
    def __init__(self, env, run_env, check_req=False, return_req=False):
        super(ChinaRepayService, self).__init__('china', 'repay', env, run_env, check_req, return_req)
        self.grant_host = "http://grant{0}.k8s-ingress-nginx.kuainiujinke.com".format(env)
        self.repay_host = "http://repay{0}.k8s-ingress-nginx.kuainiujinke.com".format(env)
        self.biz_host = "http://biz-central-{0}.k8s-ingress-nginx.kuainiujinke.com".format(env)
        self.grant = ChinaGrantService(env, run_env, check_req, return_req)
        self.biz_central = ChinaBizCentralService(env, run_env, check_req, return_req)

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
        import_asset_info = self.grant.asset_import_success(asset_info)
        withdraw_success_data = self.grant.get_withdraw_success_data(item_no, old_asset, x_item_no, asset_info)
        self.grant.asset_withdraw_success(withdraw_success_data)
        self.run_msg_by_type_and_order_no(item_no, 'AssetWithdrawSuccess', timeout=60)
        capital_data = self.grant.get_capital_asset_data(item_no)
        self.grant.capital_asset_success(capital_data)

        # 小单
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

    def get_asset_tran_balance_amount_by_period(self, item_no, period_start, period_end):
        asset_tran_list = self.db_session.query(AssetTran).filter(AssetTran.asset_tran_asset_item_no == item_no,
                                                                  AssetTran.asset_tran_period >= period_start,
                                                                  AssetTran.asset_tran_period <= period_end).all()
        return reduce(lambda x, y: x + y.asset_tran_balance_amount, asset_tran_list, 0)

    def set_asset_tran_status(self, period, item_no, status='finish'):
        if not period or not item_no:
            raise ValueError('period or item_no can not be none!')
        if status not in ('finish', 'nofinish'):
            raise ValueError('status error, only finish, nofinish!')
        item_no_x = self.get_no_loan(item_no)
        asset = self.db_session.query(Asset).filter(Asset.asset_item_no == item_no).first()
        if item_no_x:
            asset_x = self.db_session.query(Asset).filter(Asset.asset_item_no == item_no_x).first()
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
            tran_item.asset_tran_finish_at = get_date() if item_status == 'finish' else '1000-01-01'

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
        self.db_session.commit()

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
        at_list = self.db_session.query(AssetTran).filter(
            AssetTran.asset_tran_period >= period_start,
            AssetTran.asset_tran_period <= period_end,
            AssetTran.asset_tran_asset_item_no == item_no,
            AssetTran.asset_tran_type.in_(('repayprincipal', 'repayinterest'))).all()
        principal_amount = 0
        interest_amount = 0
        for at in at_list:
            if at.asset_tran_type == 'repayprincipal':
                principal_amount += at.asset_tran_total_amount
            elif at.asset_tran_period == period_start:
                interest_amount = at.asset_tran_total_amount
        if principal_over:
            principal_amount = principal_amount - 1
        if interest_type == 'less':
            interest_amount = interest_amount - 1
        elif interest_type == 'more':
            interest_amount = interest_amount + 1
        return self.easy_mock.update_trail_amount(channel, principal_amount, interest_amount, status)

    @staticmethod
    def _sum_amount_(amount_type, amount_list):
        return sum([x.asset_tran_repaid_amount for x in amount_list if x.asset_tran_category == amount_type])

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

    # def get_biz_capital_info(self, item_no):
    #     ret = {}
    #     biz_capital_detail = self.biz_central.get_capital_detail(item_no)
    #     biz_capital = self.biz_central.get_capital(item_no)
    #     biz_capital_tran = self.biz_central.get_capital_tran(item_no)
    #     biz_capital_notify = self.biz_central.get_capital_notify(item_no)
    #     ret.update(biz_capital_detail)
    #     ret.update(biz_capital)
    #     ret.update(biz_capital_tran)
    #     ret.update(biz_capital_notify)
    #     return ret

    def add_and_update_holiday(self, date_time, status):
        return self.biz_central.add_and_update_holiday(date_time, status)

    @time_print
    def run_msg_by_order_no(self, order_no, sendmsg_type, excepts={"code": 0}):
        msg = self.db_session.query(SendMsg).filter(SendMsg.sendmsg_order_no == order_no,
                                                    SendMsg.sendmsg_status == 'open',
                                                    SendMsg.sendmsg_type == sendmsg_type).order_by(
            desc(SendMsg.sendmsg_create_at)).first()
        if msg:
            return self.run_msg_by_id(msg.sendmsg_id)

    @query_withhold
    def active_repay(self, item_no, item_no_rights='', repay_card=1, amount=0, x_amount=0, rights_amount=0,
                     verify_code='', verify_seq=None, agree=False, protocol=False,
                     period_start=None, period_end=None):
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
        if not item_no and not item_no_rights:
            raise ValueError('need item_no or item_no_rights one is not null!')
        amount = self.__get_repay_amount__(amount, item_no, period_start, period_end, max_period, is_overdue)
        x_amount = self.__get_repay_amount__(x_amount, item_no_x, period_start, period_end, max_period, is_overdue)
        rights_amount = self.__get_repay_amount__(rights_amount, item_no_rights, period_start, period_end, max_period,
                                                  is_overdue)
        if amount == 0 and x_amount == 0 and rights_amount == 0:
            return "当前已结清", "", []
        request_data = self.__get_active_request_data__(item_no, item_no_x, item_no_rights, amount, x_amount,
                                                        rights_amount, repay_card, verify_code=verify_code,
                                                        verify_seq=verify_seq)
        print(json.dumps(request_data))
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
            agree_resp = Http.http_post(self.active_repay_url, agree_request_data)
            # 执行协议签约任务
            request_data = [request_data, agree_request_data]
            resp = [resp, agree_resp]
        return request_data, self.active_repay_url, resp

    def __early_settlement_need_decrease__(self, item_no):
        asset = self.db_session.query(Asset).filter(Asset.asset_item_no == item_no).first()
        ret = False
        if asset is None:
            return ret
        config_content = self.nacos.get_config_content('repay_{0}_config'.format(asset.asset_loan_channel))
        if asset.asset_loan_channel in ('qinnong', 'qinnong_jieyi'):
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
            # "card_num_encrypt": "enc_03_3697830581502478336_772",
            # "id_num_encrypt": "enc_02_3697732689936779264_273",
            # "username_encrypt": "enc_04_3622670_423",
            # "mobile_encrypt": "enc_01_3697732693258668032_713",
        # active_request_data['data']['card_num_encrypt'] = 'enc_03_3697830581502478336_772'
        # active_request_data['data']['card_user_id_encrypt'] = 'enc_02_3697732689936779264_273'
        # active_request_data['data']['card_user_name_encrypt'] = 'enc_04_3622670_423'
        # active_request_data['data']['card_user_phone_encrypt'] = 'enc_01_3697732693258668032_713'
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
        if repay_card in (1, 3, 0):
            card_element = ('card_acc_num_encrypt', 'card_acc_id_num_encrypt', 'card_acc_name_encrypt',
                            'card_acc_tel_encrypt')
        elif repay_card == 2:
            card_element = ('bank_code_encrypt', 'id_number_encrypt', 'user_name_encrypt', 'phone_number_encrypt')
        return dict(zip(repay_key, card_element))

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

    def get_repay_card_by_item_no(self, item_no):
        sql = "select card_acc_id_num_encrypt, card_acc_num_encrypt, card_acc_tel_encrypt, card_acc_name_encrypt " \
              "from card join card_asset on card_no = card_asset_card_no where " \
              "card_asset_asset_item_no='{0}'and card_asset_type = 'repay'".format(item_no)
        id_num_info = self.db_session.execute(sql)
        return id_num_info[0] if id_num_info else ''

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
        card_bind_list = self.db_session.query(CardBind).filter(
            CardBind.card_bind_serial_no.in_(withhold_serial_no),
            CardBind.card_bind_create_at >= max_create_at).all()
        return card_bind_list

    @modify_return
    def get_withhold_detail(self, withhold_serial_no, max_create_at):
        withhold_detail_list = self.db_session.query(WithholdDetail).filter(
            WithholdDetail.withhold_detail_serial_no.in_(withhold_serial_no),
            WithholdDetail.withhold_detail_create_at >= max_create_at).all()
        return withhold_detail_list

    def get_withhold_info(self, item_no, max_create_at, request_no=None, req_key=None):
        """

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

    def check_item_exist(self, item_no):
        asset = self.db_session.query(Asset).filter(Asset.asset_item_no == item_no).first()
        return asset

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
        asset.asset_source_type = 1
        db.session.add(asset)
        db.session.flush()
        return self.get_auto_asset(repay_asset.asset_loan_channel, repay_asset.asset_period_count)

    def get_auto_asset(self, channel, period):
        asset_list = AutoAsset.query.filter(AutoAsset.asset_period == period,
                                            AutoAsset.asset_channel == channel,
                                            AutoAsset.asset_env == self.env,
                                            AutoAsset.asset_create_at >= self.get_date(is_str=True, days=-7)) \
            .order_by(desc(AutoAsset.asset_id)).all()
        asset_list = list(map(lambda x: x.to_spec_dict, asset_list))
        ret = {'assets': asset_list}
        if asset_list:
            ret_info = self.get_asset_info(asset_list[0]['name'])
            ret.update(ret_info)
        return ret

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
        capital_data = []
        if grant_msg is None:
            grant_msg = self.get_withdraw_success_info(item_no, get_type='msg')
            capital_data = self.grant.get_capital_asset_data(item_no)
        return dict(zip(('biz_task', 'grant_msg', 'is_noloan', 'capital_data'),
                        (biz_task, grant_msg, is_noloan, capital_data)))

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
            self.run_task_by_type_and_order_no('AssetAccountChangeNotify', asset_x)
        self.run_task_by_type_and_order_no('AssetAccountChangeNotify', item_no)
        return [request_data, request_x_data] if asset_x else [request_data], self.refresh_url, [resp, resp_x] \
            if asset_x else [resp]

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

    def offline_recharge_repay(self, item_no, amount, serial_no, period):
        req_data, offline_recharge_url, recharge_ret = self.offline_recharge(item_no, amount, serial_no)
        if recharge_ret['code'] == 0:
            offline_req, offline_repay_url, repay_ret = self.offline_repay(item_no, serial_no, period)
        else:
            offline_req, offline_repay_url, repay_ret = '', '', '线下还款失败'
        return dict(zip(('offline_recharge', 'offline_repay'), ([req_data, offline_recharge_url, recharge_ret],
                                                                [offline_req, offline_repay_url, repay_ret])))

    def run_task_by_id(self, task_id, max_create_at=None, item_no=None):
        ret = super(ChinaRepayService, self).run_task_by_id(task_id)
        if max_create_at is not None:
            return self.info_refresh(item_no, max_create_at=max_create_at, refresh_type="task")
        return ret

    def run_msg_by_id(self, msg_id, max_create_at=None, item_no=None):
        ret = super(ChinaRepayService, self).run_msg_by_id(msg_id)
        if max_create_at is not None:
            return self.info_refresh(item_no, max_create_at=max_create_at, refresh_type='msg')
        return ret

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

    def repay_callback(self, serial_no, status, refresh_type=None, max_create_at=None, item_no=None):
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

    def run_task_by_type_and_order_no(self, task_type, order_no):
        task_list = self.db_session.query(Task).filter(Task.task_type == task_type,
                                                       Task.task_order_no == order_no,
                                                       Task.task_status == 'open').all()
        for task in task_list:
            self.run_task_by_id(task.task_id)

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

    def run_biz_task(self, task_id, run_date, re_run, max_create_at=None, item_no=None):
        ret = self.biz_central.run_central_task_by_task_id(task_id, run_date, re_run)
        if max_create_at is not None:
            return self.info_refresh(item_no, max_create_at=max_create_at, refresh_type='biz_task')
        return ret

    def run_biz_msg(self, msg_id, max_create_at=None, item_no=None):
        ret = self.biz_central.run_central_msg_by_msg_id(msg_id)
        if max_create_at is not None:
            return self.info_refresh(item_no, max_create_at=max_create_at, refresh_type='biz_msg')
        return ret

    def run_biz_xxl_job(self, job_type, run_date):
        return self.biz_central.run_xxl_job(job_type, run_date)

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
