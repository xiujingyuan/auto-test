import json
import random
from app import db
from sqlalchemy import desc

from app.model.Model import AutoAsset
from app.services import time_print
from app.services.china import get_trace
from app.services.grant import GrantBaseService
from app.common.http_util import Http
from app.services.china.biz_central.service import ChinaBizCentralService
from app.services.china.grant import FROM_SYSTEM_DICT, CHANNEL_SOURCE_TYPE_DICT
from app.services.china.grant.Model import Asset, Task, Sendmsg, AssetExtend, \
    AssetTran, CapitalAsset, AssetLoanRecord, CapitalTransaction, CapitalAccount, RouterCapitalPlan, Synctask, \
    AssetAttachment, CapitalAccountAction
from app.services.china.grant.ContractModel import Task as ContractTask, Contract, Contract2023

BANK_MAP = {"中国银行": "BOC",
                    "工商银行": "ICBC",
                    "招商银行": "CMB",
                    "建设银行": "CCB",
                    "民生银行": "CMBC"}


class ChinaGrantService(GrantBaseService):
    RPC_DICT = {
        'lanzhouhaoyue': 'lanzhouhaoyue',
        'weipin_zhongwei': 'weipin',
        'zhongyuan_zunhao': 'zhongyuan',
        'jinmeixin_hanchen': 'hanchen',
        'lanzhou_haoyue_qinjia': 'qinjia'
    }

    def __init__(self, env, run_env, mock_name, check_req=False, return_req=False):
        self.grant_host = "https://biz-gateway-proxy.k8s-ingress-nginx.kuainiujinke.com/grant{0}".format(env)
        self.contract_host = "https://biz-gateway-proxy.k8s-ingress-nginx.kuainiujinke.com/contract{0}".format(env)
        self.repay_host = "https://biz-gateway-proxy.k8s-ingress-nginx.kuainiujinke.com/repay{0}".format(env)
        self.cmdb_host = 'https://biz-gateway-proxy.k8s-ingress-nginx.kuainiujinke.com/biz-cmdb1' \
                         '/v6/rate/standard-calculate'
        super(ChinaGrantService, self).__init__('china', env, run_env, mock_name, check_req, return_req)
        self.biz_central = ChinaBizCentralService(env, run_env, mock_name, check_req, return_req)
        self.task_url = self.grant_host + '/task/run?orderNo={0}'
        self.account_query_url = self.grant_host + '/account/register-query'
        self.account_register_url = self.grant_host + '/account/register-account'
        self.contract_task_url = self.contract_host + '/task/run?orderNo={0}'
        self.contract_msg_url = self.contract_host + '/msg/run?orderNo={0}'
        self.run_contract_task_id_url = self.contract_host + '/task/run?taskId={0}'
        self.run_contract_msg_id_url = self.contract_host + '/msg/run?msgId={0}'
        self.msg_url = self.grant_host + '/msg/run?orderNo={0}'
        self.seq = ''

    def is_mock(self, channel):
        value = self.nacos.get_config('rpc_clients.properties', group='SYSTEM')
        key_name = f'rpc.client.{self.RPC_DICT[channel]}.serviceUrl' \
            if channel in self.RPC_DICT else 'rpc.client.bizGateway.serviceUrl'
        for v in value['content'].split('\n')[::-1]:
            if v.startswith(key_name):
                v_value = v.split('=')[-1]
                if v_value != 'http://biz-gateway-api.k8s-ingress-nginx.kuainiujinke.com':
                    return False
        return True

    def modify_diff(self, channel, item_no):
        task = self.db_session.query(Task).filter(Task.task_order_no == item_no,
                                                  Task.task_type == 'CapitalRepayPlanQuery').first()
        message = json.loads(task.task_response_data)['message']
        diff_str = message.split('[{')[1].split('}]')[0].split(',')
        diff_str_interest = int(diff_str[0].split("=")[1])
        diff_str_service = int(diff_str[1].split("=")[1])
        diff = abs(diff_str_interest + diff_str_service)
        json_path_dict = {
            '$.workflow.props.CapitalRepayPlanProps.allowance_check_range.min_value': -diff,
            '$.workflow.props.CapitalRepayPlanProps.allowance_check_range.max_value': diff,
        }
        return self.nacos.update_config_by_json_path(f'gbiz_capital_{channel}', json_path_dict)

    def modify_diff_dueat(self, channel):
        json_path_dict = {
            '$.task_config_map.CapitalRepayPlanQuery.execute.allow_diff_due_at': True,
            '$.task_config_map.CapitalRepayPlanQuery.execute.allow_diff_effect_at': False,
        }
        return self.nacos.update_config_by_json_path(f'gbiz_capital_{channel}', json_path_dict)

    def modify_capital_plan(self, channel):
        return self.update_route_capital_plan(channel)

    @time_print
    def info_refresh(self, item_no, max_create_at=None, refresh_type=None):
        ret = getattr(self, 'get_{0}'.format(refresh_type))(item_no)
        ret.update(self.asset)
        return ret

    def add_msg(self, msg):
        new_msg = Sendmsg()
        for key, value in msg.items():
            if key != 'sendmsg_id':
                setattr(new_msg, key, value)
        new_msg.sendmsg_next_run_at = self.get_date(is_str=True)
        new_msg.sendmsg_status = 'open'
        self.db_session.add(new_msg)
        self.db_session.flush()
        self.db_session.commit()
        self.run_msg_by_id(new_msg.sendmsg_id)

    def add_sync_task(self, task):
        exist_sync_task = self.db_session.query(Synctask).filter(Synctask.synctask_order_no == task['synctask_order_no']).first()
        if exist_sync_task is None:
            new_task = Synctask()
            for key, value in task.items():
                if key != 'synctask_id':
                    setattr(new_task, key, value)
            self.db_session.add(new_task)
            self.db_session.flush()
            self.db_session.commit()
            # self.run_task_by_id(new_task.task_id)

    def get_apr36_total_amount(self, principal_amount, period_count):
        return self.get_total_amount(principal_amount, period_count, 36, "equal")

    def get_irr36_total_amount(self, principal_amount, period_count):
        return self.get_total_amount(principal_amount, period_count, 36, "acpi")

    def delete_row_data(self, del_id, del_type):
        obj = eval(del_type.title().replace("_", ""))
        self.db_session.query(obj).filter(getattr(obj, 'id') == del_id).delete()
        self.db_session.flush()
        self.db_session.commit()

    def info_refresh(self, item_no, max_create_at=None, refresh_type=None):
        refresh_type = refresh_type[6:] if refresh_type.startswith("grant_") else refresh_type
        return getattr(self, 'get_{0}'.format(refresh_type))(item_no)

    def capital_manual_grant(self, channel, count, amount, app, source_type, bank_code, extend):
        req = {
            "env": self.env,
            "country": self.country,
            "environment": self.run_env,
            "channel": channel,
            "amount": amount,
            "count": count,
            'bank_code': bank_code,
            "app": app,
            "source_type": source_type,
            "extend": extend
        }
        url = 'https://biz-gateway-proxy.k8s-ingress-nginx.kuainiujinke.com/framework-test/capital-manual-grant'
        # url = 'http://127.0.0.1:5208/capital-manual-grant'
        ret = Http.http_post(url, req)
        if ret['code'] == 0:
            item_no = ret['data']['item_no']
            task = self.get_task_info(item_no)[0]
            asset_info = json.loads(task.task_request_data)['data']
            element = ret['data']['element']
            self.insert_router_record(item_no, channel, amount, count, element, asset_info)
            self.update_route_capital_plan(channel)
            self.run_task_by_task_order_no(item_no)
            self.prepare_attachment(channel, item_no)
            self.add_asset(item_no, source_type=2, extend=element)
        return ret

    def register_after(self, item_no, account_action, account_phone, account_code):
        url = 'https://biz-gateway-proxy.k8s-ingress-nginx.kuainiujinke.com/framework-test/register-after'
        # url = 'http://127.0.0.1:5208/register-after'
        asset = db.session.query(AutoAsset).filter(AutoAsset.asset_name == item_no,
                                                   AutoAsset.asset_env == self.env,
                                                   AutoAsset.asset_type == 2).first()
        four_element = json.loads(asset.asset_extend)
        account_phone = account_phone if account_phone else '18683783691'

        if account_phone:
            four_element['data']['phone_number'] = account_phone
            phone_number_encrypt = four_element['data'].pop('phone_number_encrypt')
            four_element['data']['phone_number_encrypt'] = self.encrypt_data('mobile', account_phone)
        req = {
            'item_no': item_no,
            'four_element': four_element,
            'account_code': account_code,
            'account_action': account_action,
            'env': self.env,
            'channel': asset.asset_channel
        }

        if account_action == 'CheckSmsVerifyCode':
            sms_seq = self.db_session.query(CapitalAccountAction).filter(
                CapitalAccountAction.capital_account_action_item_no == item_no,
                CapitalAccountAction.capital_account_action_type == 'GetSmsVerifyCode').first()
            req['sms_seq'] = sms_seq if sms_seq is None else sms_seq.capital_account_action_seq

        ret = Http.http_post(url, req)

        if account_action == 'CheckSmsVerifyCode':
            account = self.db_session.query(CapitalAccount).filter(
                CapitalAccount.capital_account_item_no == item_no,
                CapitalAccount.capital_account_mobile_encrypt == self.encrypt_data('mobile', account_phone)
            ).first()
            account.capital_account_mobile_encrypt = phone_number_encrypt
            self.db_session.add(account)
            self.db_session.commit()

        return ret

    def run_contract_task_by_id(self, task_id, excepts={'code': 0}):
        # self.update_task_next_run_at_forward_by_task_id(task_id)
        ret = Http.http_get(self.run_contract_task_id_url.format(task_id))
        ret = ret[0] if isinstance(ret, list) else ret
        if not isinstance(ret, dict):
            raise ValueError(ret)
        elif not ret["code"] == 0:
            raise ValueError("run task error, {0}".format(ret['message']))
        return ret

    def update_task_next_run_at_forward_by_order_no(self, order_no):
        clean_task = self.db_session.query(Task).filter(Task.task_order_no == order_no).all()
        if not clean_task:
            raise ValueError("not found the clean_task info with clean_task'id: {0}".format(order_no))
        for task in clean_task:
            task.task_next_run_at = self.get_date(minutes=1)
            self.db_session.add(task)
        self.db_session.commit()

    def update_contract_task_next_run_at_forward_by_order_no(self, order_no):
        clean_task = self.db_session_contract.query(ContractTask).filter(ContractTask.task_order_no == order_no).all()
        if not clean_task:
            raise ValueError("not found the clean_task info with clean_task'id: {0}".format(order_no))
        for task in clean_task:
            task.task_next_run_at = self.get_date(minutes=1)
            self.db_session_contract.add(task)
        self.db_session_contract.commit()

    def run_task_by_task_order_no(self, item_no):
        self.update_task_next_run_at_forward_by_order_no(item_no)
        url = self.task_url.format(item_no)
        ret = Http.http_get(url)
        return ret

    def run_contract_task_by_task_order_no(self, item_no):
        self.update_contract_task_next_run_at_forward_by_order_no(item_no)
        url = self.contract_task_url.format(item_no)
        ret = Http.http_get(url)
        return ret

    @get_trace
    def operate_action(self, item_no, extend, op_type, table_name, run_date, creator):
        table_name = table_name[6:] if table_name.startswith('grant_') else table_name
        extend_name = '{0}_create_at'.format(table_name)
        max_create_at = extend[extend_name] if extend_name in extend else None
        max_create_at = extend['create_at'] if max_create_at is None else None
        real_req = {}
        if op_type in ('run_task_by_task_order_no', 'run_contract_task_by_task_order_no'):
            real_req['order_no'] = item_no
        elif op_type in ('run_task_by_id', 'run_contract_task_by_id'):
            real_req['task_id'] = extend['id']
        elif op_type in ('run_msg_by_id', 'run_contract_msg_by_id'):
            real_req['msg_id'] = extend['id']
        if op_type == "del_row_data":
            real_req['del_id'] = extend['id']
            real_req['item_no'] = item_no
            real_req['refresh_type'] = table_name
            real_req['max_create_at'] = max_create_at
        ret = getattr(self, op_type)(**real_req)
        if max_create_at is not None:
            return self.info_refresh(item_no, max_create_at, refresh_type=table_name)
        return ret

    def get_grant_info(self, item_no):
        ret = {}
        ret.update(self.get_task(item_no))
        ret.update(self.get_sendmsg(item_no))
        ret.update(self.get_asset_loan_record(item_no))
        return ret

    def get_contract_task(self, item_no):
        task = self.db_session_contract.query(ContractTask).filter(ContractTask.task_order_no == item_no).order_by(
            desc(ContractTask.task_id)).all()
        return {'contract_task': list(map(lambda x: x.to_spec_dict, task))}

    def get_task(self, item_no):
        task = self.get_task_info(item_no)
        return {'grant_task': list(map(lambda x: x.to_spec_dict_obj([Task.task_request_data, Task.task_response_data]), task))}

    def get_synctask(self, item_no):
        sync_task = self.db_session.query(Synctask).filter(
            Synctask.synctask_order_no == item_no).order_by(desc(Synctask.synctask_id)).all()
        return {'grant_synctask': list(map(lambda x: x.to_spec_dict_obj(
            [Synctask.synctask_request_data, Synctask.synctask_response_data]), sync_task))}

    def get_task_info(self, item_no):
        task = self.db_session.query(Task).filter(Task.task_order_no == item_no).order_by(desc(Task.task_id)).all()
        return task

    def get_router_capital_plan(self, item_no):
        router_capital_plan = self.db_session.query(RouterCapitalPlan).order_by(
            desc(RouterCapitalPlan.router_capital_plan_date)).all()
        return {'router_capital_plan': list(map(lambda x: x.to_spec_dict, router_capital_plan))}

    def update_route_capital_plan(self, channel):
        router_capital_plan = self.db_session.query(RouterCapitalPlan).filter(
            RouterCapitalPlan.router_capital_plan_label.like(f'{channel}%')).order_by(
            desc(RouterCapitalPlan.router_capital_plan_date)).first()
        if router_capital_plan is None:
            pass
        if self.cal_days(router_capital_plan.router_capital_plan_date, self.get_date()) != 0:
            router_capital_plan.router_capital_plan_date = self.get_date(fmt='%Y-%m-%d')
            self.db_session.add(router_capital_plan)
            self.db_session.commit()
        if router_capital_plan.router_capital_plan_amount < 100000000:
            router_capital_plan.router_capital_plan_amount = 100000000
            self.db_session.add(router_capital_plan)
            self.db_session.commit()

    def get_capital_account(self, item_no):
        capital_account = self.db_session.query(CapitalAccount).filter(CapitalAccount.capital_account_item_no == item_no).all()
        return {'capital_account': list(map(lambda x: x.to_spec_dict, capital_account))}

    def get_asset_tran(self, item_no):
        asset_tran = self.db_session.query(AssetTran).filter(AssetTran.asset_tran_asset_item_no == item_no).all()
        return {'asset_tran': list(map(lambda x: x.to_spec_dict, asset_tran))}

    def get_sendmsg(self, item_no):
        msg = self.db_session.query(Sendmsg).filter(Sendmsg.sendmsg_order_no == item_no).order_by(
            desc(Sendmsg.sendmsg_id)).all()
        return {'grant_sendmsg': list(map(lambda x: x.to_spec_dict_obj([Sendmsg.sendmsg_content,
                                                                        Sendmsg.sendmsg_response_data,
                                                                        Sendmsg.sendmsg_memo]), msg))}

    def add_contract(self, item, channel, attachment_type, attachment_name, attachment_url):
        now = self.get_date(is_str=True)
        contract = Contract2023()
        contract.contract_create_at = self.get_date()
        contract.contract_asset_item_no = item
        contract.contract_type = attachment_type
        contract.contract_type_text = attachment_name
        contract.contract_url = attachment_url
        contract.contract_status = 'SUCCESS'
        contract.contract_from_system = 'strawberry'
        contract.contract_code = self.get_random_str()
        contract.contract_apply_id = f'{item}-30300-1611906119811'
        contract.contract_flow_key = 'tpl2007301443234707AE'
        contract.contract_ref_item_no = item
        contract.contract_sign_at = now
        contract.contract_update_at = now
        contract.contract_sign_opportunity = 'AssetImport'
        contract.contract_provider = 'YUN'
        contract.contract_subject = '如皋智萃'
        contract.contract_channel = channel
        contract.contract_version = 1
        self.db_session_contract.add(contract)
        self.db_session_contract.commit()

    def add_attachment(self, item_no, attachment_type, attachment_name, attachment_url):
        attachment = AssetAttachment()
        attachment.asset_attachment_asset_item_no = item_no
        attachment.asset_attachment_type = attachment_type
        attachment.asset_attachment_contract_code = self.get_random_str()
        attachment.asset_attachment_type_text = attachment_name
        attachment.asset_attachment_url = attachment_url
        attachment.asset_attachment_status = 1
        attachment.asset_attachment_from_system = 'contract'
        self.db_session.add(attachment)
        self.db_session.commit()

    def prepare_attachment(self, channel, item_no):
        key_value = self.get_key_value('attachment')
        if channel not in key_value:
            return
        for attachment_type, attachment_name, attachment_url in key_value[channel]:
            self.add_contract(item_no, channel, attachment_type, attachment_name, attachment_url)
            # 云信全互还是读的gbiz附件表
            if channel == "yunxin_quanhu":
                self.add_attachment(item_no, attachment_type, attachment_name, attachment_url)

    def get_asset_loan_record(self, item_no):
        asset_loan_record = self.db_session.query(AssetLoanRecord).filter(
            AssetLoanRecord.asset_loan_record_asset_item_no == item_no).order_by(
            desc(AssetLoanRecord.asset_loan_record_id)).all()
        return {'asset_loan_record': list(map(lambda x: x.to_spec_dict, asset_loan_record))}

    def get_total_amount(self, principal_amount, period_count, interest_rate, repay_type):
        """
        标准还款计划计算
        :param principal_amount:
        :param period_count:
        :param interest_rate:
        :param repay_type: acpi / equal
        :return:
        """
        cmdb_tran = self.cmdb_standard_calc_v5(principal_amount, period_count, interest_rate, repay_type)
        total_interest = 0
        for item in cmdb_tran['data']['calculate_result']['interest']:
            total_interest += item['amount']
        total_amount = principal_amount + total_interest
        return total_amount

    def cmdb_standard_calc_v5(self, principal_amount, period_count, interest_rate, repay_type,
                              interest_year_type="360per_year", month_clear_day="D+0", clear_day="D+0", sign_date=None):
        req = {
            "type": "CalculateStandardRepayPlan",
            "key": "calculate_${key}",
            "from_system": "bc",
            "data": {
                "sign_date": self.get_date(fmt="%Y-%m-%d", is_str=True),
                "principal_amount": principal_amount,
                "period_count": period_count,
                "period_type": "month",
                "period_term": 1,
                "interest_rate": interest_rate,
                "repay_type": repay_type,
                "interest_year_type": interest_year_type,
                "month_clear_day": month_clear_day,
                "clear_day": clear_day
            }
        }
        resp = Http.http_post(self.cmdb_host, req)
        return resp

    def calc_noloan_amount(self, loan_asset_info, noloan_source_type):
        """
        计算小单金额
        # APR融担小单金额 = APR36总额 - 大单总额
        # IRR融担小单金额 = IRR36总额 - 大单总额
        # IRR权益小单金额 = APR36总额 - IRR36总额
        :param loan_asset_info:
        :param noloan_source_type:
        :return:
        """

        loan_principal_amount = loan_asset_info["data"]["asset"]["amount"] * 100
        loan_period_count = loan_asset_info["data"]["asset"]["period_count"]
        loan_channel = loan_asset_info["data"]["asset"]["loan_channel"]
        req_data = {
            "channel": loan_channel,
            "grant_date": "",
            "period_count": loan_period_count,
            "principal": loan_principal_amount
        }
        ret = Http.http_post('http://framework-test.k8s-ingress-nginx.kuainiujinke.com/gbiz-calc-noloan-amount',
                             req_data)
        rongdan = ret['data']['apr融担小单金额']
        lieyin = ret['data']['irr权益小单金额']
        rongdan_irr = ret['data']['irr融担小单金额']
        noloan_amount_dict = dict(zip(("rongdan", "rongdan_irr", "lieyin"),
                                      (rongdan, rongdan_irr, lieyin)))
        return noloan_amount_dict[noloan_source_type] / 100

    @staticmethod
    def get_from_system_and_ref(from_system_name, source_type):
        from_system = FROM_SYSTEM_DICT[from_system_name] if from_system_name in FROM_SYSTEM_DICT else "dsq"
        source_type = "real36" if from_system_name == "火龙果" else source_type
        return from_system, source_type

    def set_asset_asset_info(self, asset_info, item_no, count, channel, amount, source_type, from_system_name,
                             ref_order_no, sub_order_type):
        asset_info['data']['asset']['item_no'] = item_no
        asset_info['data']['asset']['name'] = "tn" + item_no
        asset_info['data']['asset']['period_type'] = "month"
        asset_info['data']['asset']['period_count'] = count
        asset_info['data']['asset']['period_day'] = 0
        asset_info['data']['asset']['amount'] = amount
        asset_info['data']['asset']['grant_at'] = self.get_date(is_str=True)
        asset_info['data']['asset']['loan_channel'] = channel
        asset_info['data']['asset']['source_type'] = source_type
        asset_info['data']['asset']['from_app'] = from_system_name
        asset_info['data']['asset']['source_number'] = ref_order_no
        asset_info['data']['asset']['sub_order_type'] = sub_order_type

    @staticmethod
    def set_asset_repay_card(asset_info, element, bank_code='ICBC'):
        asset_info['data']['repay_card']['username_encrypt'] = element['data']['user_name_encrypt']
        asset_info['data']['repay_card']['phone_encrypt'] = element['data']['phone_number_encrypt']
        asset_info['data']['repay_card']['account_num_encrypt'] = element['data']['bank_code_encrypt']
        asset_info['data']['repay_card']['individual_idnum_encrypt'] = element['data']['id_number_encrypt']
        asset_info['data']['repay_card']['credentials_num_encrypt'] = element['data']['id_number_encrypt']
        asset_info['data']['repay_card']['bank_code'] = bank_code

    @staticmethod
    def set_asset_receive_card(asset_info, element, bank_code='ICBC'):
        asset_info['data']['receive_card']['owner_name_encrypt'] = element['data']['user_name_encrypt']
        asset_info['data']['receive_card']['account_name_encrypt'] = element['data']['user_name_encrypt']
        asset_info['data']['receive_card']['phone_encrypt'] = element['data']['phone_number_encrypt']
        asset_info['data']['receive_card']['owner_id_encrypt'] = element['data']['id_number_encrypt']
        asset_info['data']['receive_card']['num_encrypt'] = element['data']['bank_code_encrypt']
        asset_info['data']['receive_card']['bank_code'] = bank_code

    @staticmethod
    def set_asset_borrower(asset_info, element):
        asset_info['data']['borrower']['name_encrypt'] = element['data']['user_name_encrypt']
        asset_info['data']['borrower']['tel_encrypt'] = element['data']['phone_number_encrypt']
        asset_info['data']['borrower']['idnum_encrypt'] = element['data']['id_number_encrypt']
        asset_info['data']['borrower']['residence'] = "陕西省白水县北塬乡潘村二社"
        asset_info['data']['borrower']['workplace'] = "山东省胶州市铺集镇吴家庄村45号"
        asset_info['data']['borrower']['id_addr'] = "甘肃省天水市秦州区岷玉路罗玉小区市31幢3单元501室"
        asset_info['data']['borrower']['idnum_cert_office'] = "安陆市公安局"

    @staticmethod
    def set_asset_repayer(asset_info, element):
        asset_info['data']['repayer']['name_encrypt'] = element['data']['user_name_encrypt']
        asset_info['data']['repayer']['tel_encrypt'] = element['data']['phone_number_encrypt']
        asset_info['data']['repayer']['idnum_encrypt'] = element['data']['id_number_encrypt']
        asset_info['data']['repayer']['residence'] = "陕西省白水县北塬乡潘村二社"
        asset_info['data']['repayer']['workplace'] = "山东省胶州市铺集镇吴家庄村45号"
        asset_info['data']['repayer']['id_addr'] = "甘肃省天水市秦州区岷玉路罗玉小区市31幢3单元501室"
        asset_info['data']['repayer']['idnum_cert_office'] = "安陆市公安局"

    def get_no_loan(self, item_no):
        asset_extend = self.db_session.query(AssetExtend).filter(
            AssetExtend.asset_extend_asset_item_no == item_no).first()
        if not asset_extend:
            raise ValueError('not found the asset extend info!')
        return asset_extend.asset_extend_ref_order_no

    def copy_asset(self, item_no):
        asset = self.db_session.queyr(Asset).filter(Asset.asset_item_no == item_no).first()
        asset_tran = self.db_session.queyr(AssetTran).filter(AssetTran.asset_tran_asset_item_no == item_no).all()
        task = self.db_session.queyr(Task).filter(Task.task_order_no == item_no).all()
        msg = self.db_session.queyr(Sendmsg).filter(Sendmsg.sendmsg_order_no == item_no).all()
        asset_loan_record = self.db_session.queyr(AssetLoanRecord).filter(AssetLoanRecord.asset_loan_record_asset_item_no == item_no).all()
        capital_asset = self.db_session.queyr(CapitalAsset).filter(CapitalAsset.capital_asset_item_no == item_no).first()
        capital_tran = self.db_session.queyr(CapitalTransaction).filter(CapitalTransaction.capital_transaction_item_no == item_no).all()
        return None

    def get_asset_item_info(self, channel, source_type, from_system_name, item_no=None):
        item_no = item_no if item_no else self.create_item_no()
        source_type_list = CHANNEL_SOURCE_TYPE_DICT[channel] if channel in CHANNEL_SOURCE_TYPE_DICT \
            else CHANNEL_SOURCE_TYPE_DICT['yixin_hengrun']
        filter_source = list(filter(lambda x: x[0] == source_type, source_type_list))
        if not filter_source:
            raise ValueError('the channel {0} is not match the source type {1}'.format(channel, source_type))
        source_type, x_source_type, x_right = random.choice(filter_source)
        from_system, source_type = self.get_from_system_and_ref(from_system_name, source_type)
        x_source_type = '' if source_type == 'real36' else x_source_type
        x_right = '' if source_type == 'real36' else x_right
        x_order_no = '{0}_right'.format(item_no) if x_right else ''
        ref_order_no = '{0}_noloan'.format(item_no) if x_source_type else ''
        return item_no, ref_order_no, x_order_no, source_type, x_source_type, x_right, from_system

    def manual_asset_import(self, channel, source_type, from_system_name, element, count, amount, item_name,
                            back_code, grant_way=2):

        item_no, x_item_no, x_rights, source_type, x_source_type, x_right, from_system = \
            self.get_asset_item_info(channel, source_type, from_system_name)
        element = self.get_four_element() if element == 1 else element
        item_no = item_no if item_name == 1 else item_name
        ref_order_no = '{0}_noloan'.format(item_no)
        from_system = FROM_SYSTEM_DICT[from_system_name]
        back_code = BANK_MAP[back_code]
        asset_info, _ = self.asset_import(item_no, channel, element, count, amount, source_type,
                                          from_system_name, from_system, ref_order_no, back_code=back_code)
        self.asset_import_success(asset_info)
        if grant_way == 2:
            self.open_account(element, back_code, item_no, channel)
        self.add_asset(item_no, grant_way)

    def apply_can_loan(self, item_no):
        task = self.db_session.query(Task).filter(Task.task_order_no == item_no,
                                                  Task.task_type == 'ApplyCanLoan').first()
        task.task_status = 'open'
        task.task_next_run_at = self.get_date(is_str=True)
        self.db_session.add(task)
        asset_loan_record = self.db_session.query(AssetLoanRecord).filter(
            AssetLoanRecord.asset_loan_record_asset_item_no == item_no).first()
        asset_loan_record.asset_loan_record_status = 0
        self.db_session.add(asset_loan_record)
        self.db_session.commit()

    def open_account(self, element, bank_code, item_no, channel):
        ret = self.account_query(element, bank_code, item_no, channel)
        self.account_register(ret, channel, item_no, element, bank_code)

    def account_register(self, ret, channel, item_no, element, bank_code):
        if ret['code'] == 0 and ret['data']['status'] in (2, 4):
            # 未开户
            actions = ret['data']['steps'][0]['actions'] if 'steps' in ret['data'] else ret['data']['actions']
            for act in actions:
                if act['status'] != 0:
                    param = {
                        "from_system": "strawberry",
                        "key": self.__create_req_key__(item_no, prefix=act['action_type']),
                        "type": act['action_type'],
                        "data": {
                            "channel": channel,
                            "step_type": "PROTOCOL",
                            "interaction_type": "SMS",
                            "action_type": act['action_type'],
                            "way": channel,
                            "item_no": item_no,
                            "mobile_encrypt": element['data']['phone_number_encrypt'],
                            "id_num_encrypt": element['data']['id_number_encrypt'],
                            "username_encrypt": element['data']['user_name_encrypt'],
                            "card_num_encrypt": element['data']['bank_code_encrypt'],
                            "extend": {
                                "code": "134679",
                                "seq": self.seq,
                                "bank_code": bank_code
                            }
                        }
                    }
                    act_ret = Http.http_post(self.account_register_url, param)
                    if act_ret['code'] != 0:
                        raise ValueError('开户失败, {0}'.format(json.dumps(act_ret)))
                    elif act['action_type'] == 'GetSmsVerifyCode':
                        for action in act_ret['data']['actions']:
                            if action['action_type'] == 'GetSmsVerifyCode':
                                self.seq = action['extra_data']['seq']
                                break
                    return self.account_register(act_ret, channel, item_no, element, bank_code)

    def account_query(self, element, bank_code, item_no, channel):
        param = {
            "from_system": "DSQ",
            "key": self.__create_req_key__(item_no, prefix='AccountQuery'),
            "type": "AccountRegisterQuery",
            "data": {
                "channel": channel,
                "mobile_encrypt": element['data']['phone_number_encrypt'],
                "id_num_encrypt": element['data']['id_number_encrypt'],
                "username_encrypt": element['data']['user_name_encrypt'],
                "card_num_encrypt": element['data']['bank_code_encrypt'],
                "item_no": item_no,
                "extend": {
                    "bank_code": bank_code
                }
            }
        }
        ret = Http.http_post(self.account_query_url, param)
        print(ret)
        return ret

    def add_asset(self, name, source_type, extend=None):
        grant_asset = self.check_item_exist(name)
        if grant_asset is None:
            return '没有该资产'
        exist_asset = AutoAsset.query.filter(AutoAsset.asset_name == name, AutoAsset.asset_env == self.env).first()
        if exist_asset:
            return '该资产已经存在'
        asset = AutoAsset()
        asset.asset_create_at = self.get_date(fmt="%Y-%m-%d", is_str=True)
        asset.asset_channel = grant_asset.asset_loan_channel
        asset.asset_descript = ''
        asset.asset_extend = json.dumps(extend, ensure_ascii=False) if extend is not None else ''
        asset.asset_name = name
        asset.asset_period = grant_asset.asset_period_count
        asset.asset_env = self.env
        asset.asset_type = source_type
        asset.asset_country = self.country
        asset.asset_source_type = 1
        asset.asset_days = int(grant_asset.asset_product_category)
        db.session.add(asset)
        db.session.flush()

    def asset_import(self, item_no, channel, element, count, amount, source_type, from_system_name, from_system,
                     ref_order_no, borrower_extend_district=None, sub_order_type='', route_uuid=None, back_code='ICBC',
                     insert_router_record=True):
        asset_info, old_asset = self.get_asset_info_from_db(channel)
        asset_info['key'] = "_".join((item_no, channel))
        asset_info['from_system'] = from_system
        asset_info['data']['route_uuid'] = route_uuid
        if asset_info['data']['borrower_extend']:
            asset_info['data']['borrower_extend']['address_district_code'] = borrower_extend_district
        self.set_asset_asset_info(asset_info, item_no, count, channel, amount, source_type, from_system_name,
                                  ref_order_no, sub_order_type)
        self.set_asset_receive_card(asset_info, element, back_code)
        self.set_asset_repay_card(asset_info, element, back_code)
        self.set_asset_borrower(asset_info, element)
        self.set_asset_repayer(asset_info, element)

        if insert_router_record:
            self.insert_router_record(item_no, channel, amount, count, element, asset_info,
                                      sub_order_type=sub_order_type)
        capital_plan = self.db_session.query(RouterCapitalPlan).filter(
            RouterCapitalPlan.router_capital_plan_label.like('{0}%'.format(channel))).order_by(
                desc(RouterCapitalPlan.router_capital_plan_date)).first()
        now = self.get_date(fmt="%Y-%m-%d", is_str=True)
        if capital_plan is not None and not str(capital_plan.router_capital_plan_date) == now:
            capital_plan.router_capital_plan_date = now
            self.db_session.add(capital_plan)
            self.db_session.commit()
        return asset_info, old_asset

    def capital_asset_success(self, capital_asset):
        Http.http_post(self.repay_capital_asset_import_url, capital_asset)
        resp = Http.http_post(self.biz_central.capital_asset_import_url, capital_asset)
        self.biz_central.run_central_task_by_task_id(resp['data'])


