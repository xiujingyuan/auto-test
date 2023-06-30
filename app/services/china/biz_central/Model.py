# coding: utf-8
from flask_sqlalchemy import SQLAlchemy

from app.common.db_util import BaseToDict

db = SQLAlchemy()


class Asset(db.Model, BaseToDict):
    __tablename__ = 'asset'
    __table_args__ = (
        db.Index('idx_asset_loan_channel_owner', 'asset_loan_channel', 'asset_owner'),
        db.Index('idx_asset_type_sub_type', 'asset_type', 'asset_sub_type')
    )

    asset_id = db.Column(db.Integer, primary_key=True)
    asset_item_no = db.Column(db.String(64), nullable=False, unique=True, info='资产编号，业务主键')
    asset_type = db.Column(db.String(60), nullable=False, info='资产类型，paydayloan')
    asset_name = db.Column(db.String(64), nullable=False, server_default=db.FetchedValue(), info='资产别名')
    asset_period_type = db.Column(db.Enum('month', 'quarter', 'day'), nullable=False, server_default=db.FetchedValue(), info='期次类型：day(天),month(月),quarter(季度,无数据)')
    asset_period_count = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), info='总期数')
    asset_period_days = db.Column(db.Integer, server_default=db.FetchedValue(), info='每期天数。期次类型为day时有效，其余期次类型为0')
    asset_create_at = db.Column(db.DateTime, nullable=False, index=True, server_default=db.FetchedValue(), info='创建时间')
    asset_sign_at = db.Column(db.DateTime, nullable=False, index=True, server_default=db.FetchedValue(), info='签约时间')
    asset_grant_at = db.Column(db.DateTime, nullable=False, index=True, server_default=db.FetchedValue(), info='预计放款时间')
    asset_due_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='最大到期日')
    asset_first_payat = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='第一次还款日')
    asset_payoff_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='尝清时间')
    asset_repayment_type = db.Column(db.Enum('end', 'equal', 'acpi', 'ipcl', 'rtlataio', 'other', 'biapp', 'averagecapital'), nullable=False, server_default=db.FetchedValue(), info='还款类型：end(提前一月付息，到期还本);equal(等本等息);acpi(等额本息);ipcl(提前付息，到期还本); rtlataio(到期一次性还本付息);biapp(按月付息、到期还本); averagecapital(等额本金);other(外部导入资产，还款计划表都是外部导入的)')
    asset_contract_no = db.Column(db.String(64), nullable=False, server_default=db.FetchedValue(), info='合同编号，作废')
    asset_fee_rate = db.Column(db.Numeric(10, 6), nullable=False, server_default=db.FetchedValue(), info='服务费费率')
    asset_interest_rate = db.Column(db.Numeric(10, 3), nullable=False, server_default=db.FetchedValue(), info='利息费率')
    asset_secure_rate = db.Column(db.Numeric(10, 3), nullable=False, server_default=db.FetchedValue(), info='保证金比例')
    asset_secure_amount = db.Column(db.Numeric(10, 2), nullable=False, server_default=db.FetchedValue(), info='保证金(元)')
    asset_update_at = db.Column(db.DateTime, nullable=False, index=True, server_default=db.FetchedValue(), info='最后更新时间')
    asset_card_id = db.Column(db.Integer, nullable=False, index=True, server_default=db.FetchedValue(), info='收款银行卡id')
    asset_manage_rate = db.Column(db.Numeric(10, 6), nullable=False, server_default=db.FetchedValue(), info='管理费比例')
    asset_channel_id = db.Column(db.Integer, nullable=False, index=True, info='资产推荐渠道编号，作废')
    asset_district_id = db.Column(db.SmallInteger, nullable=False, index=True, info='借款人行政区划id')
    asset_withhold_rate = db.Column(db.Numeric(10, 3), nullable=False, server_default=db.FetchedValue(), info='推荐渠道服务费率')
    asset_multi_period = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), info='是否分期')
    asset_from_system = db.Column(db.String(50), nullable=False, server_default=db.FetchedValue(), info='资产来源系统')
    asset_is_extension = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), info='资产是否展期：0(未展期)，1(已展期),以作废')
    asset_actual_grant_at = db.Column(db.DateTime, index=True, info='实际放款时间')
    asset_is_white_list = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), info='医美资产是否白名单：0(非白名单)，1(白名单)')
    asset_status = db.Column(db.Enum('sign', 'sale', 'repay', 'payoff', 'late', 'lateoff', 'void', 'writeoff'), nullable=False, server_default=db.FetchedValue(), info='状态：sign(等待签约)，sale(销售中), repay(还款中),payoff(已结清-正常结清),late(坏账中),lateoff(已清算-坏账清算),void(作废),writeoff(注销,放款成功之后取消,无费用)')
    asset_principal_amount = db.Column(db.Numeric(10, 2), nullable=False, server_default=db.FetchedValue(), info='合同本金(元)')
    asset_granted_principal_amount = db.Column(db.Numeric(10, 2), nullable=False, server_default=db.FetchedValue(), info='实际放款金额(元)')
    asset_repaid_principal_amount = db.Column(db.Numeric(10, 2), nullable=False, server_default=db.FetchedValue(), info='已还本金(元)')
    asset_interest_amount = db.Column(db.Numeric(10, 2), nullable=False, server_default=db.FetchedValue(), info='利息(元)')
    asset_repaid_interest_amount = db.Column(db.Numeric(10, 2), nullable=False, server_default=db.FetchedValue(), info='已还利息(元)')
    asset_secure_amount_f = db.Column(db.BigInteger, nullable=False, server_default=db.FetchedValue(), info='保证金(分)')
    asset_principal_amount_f = db.Column(db.BigInteger, nullable=False, server_default=db.FetchedValue(), info='合同本金(分)')
    asset_interest_amount_f = db.Column(db.BigInteger, nullable=False, server_default=db.FetchedValue(), info='利息(分)')
    asset_repaid_interest_amount_f = db.Column(db.BigInteger, nullable=False, server_default=db.FetchedValue(), info='已还利息(分)')
    asset_granted_principal_amount_f = db.Column(db.BigInteger, nullable=False, server_default=db.FetchedValue(), info='实际放款本金(分)')
    asset_repaid_principal_amount_f = db.Column(db.BigInteger, nullable=False, server_default=db.FetchedValue(), info='已还本金(分)')
    asset_sub_type = db.Column(db.String(50), nullable=False, server_default=db.FetchedValue(), info='资产子类型:multiple(多期贷)')
    asset_loan_channel = db.Column(db.String(32), nullable=False, server_default=db.FetchedValue(), info='资金方')
    asset_cmdb_product_number = db.Column(db.String(50), info='费率编号')
    asset_from_system_name = db.Column(db.String(10), nullable=False, server_default=db.FetchedValue(), info='App名称')
    asset_owner = db.Column(db.String(24), nullable=False, server_default=db.FetchedValue(), info='资产归属方')
    asset_version = db.Column(db.BigInteger)
    asset_actual_payoff_at = db.Column(db.DateTime, nullable=False, index=True, server_default=db.FetchedValue(), info='实际尝清时间')
    asset_late_amount = db.Column(db.Numeric(20, 2), nullable=False, server_default=db.FetchedValue(), info='罚息金额(元)')
    asset_repaid_fee_amount = db.Column(db.Numeric(20, 2), nullable=False, server_default=db.FetchedValue(), info='已还服务费(元)')
    asset_repaid_late_amount = db.Column(db.Numeric(20, 2), nullable=False, server_default=db.FetchedValue(), info='已还罚息(元)')
    asset_decrease_fee_amount = db.Column(db.Numeric(20, 2), nullable=False, server_default=db.FetchedValue(), info='减免服务费(元)')
    asset_decrease_late_amount = db.Column(db.Numeric(20, 2), nullable=False, server_default=db.FetchedValue(), info='减免罚息(元)')
    asset_effect_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='合同生效日，起息日')
    asset_fee_amount = db.Column(db.Numeric(20, 2), nullable=False, server_default=db.FetchedValue(), info='服务费(元)')
    asset_from_app = db.Column(db.String(100), nullable=False, server_default=db.FetchedValue(), info='马甲包字段')
    asset_repayment_app = db.Column(db.String(10), nullable=False, server_default=db.FetchedValue(), info='资产还款APP名称')



class AssetTran(db.Model, BaseToDict):
    __tablename__ = 'asset_tran'
    __table_args__ = (
        db.Index('unique_item_no_type_period', 'asset_tran_asset_item_no', 'asset_tran_period', 'asset_tran_type'),
        db.Index('idx_asset_tran_status_due_at', 'asset_tran_status', 'asset_tran_due_at')
    )

    asset_tran_id = db.Column(db.Integer, primary_key=True, info='表主键')
    asset_tran_asset_item_no = db.Column(db.String(48), nullable=False, server_default=db.FetchedValue(), info='项目编号,关联asset')
    asset_tran_category = db.Column(db.String(32), nullable=False, info='交易类型：grant:放款, interest:利息, principal:本金, fee:费')
    asset_tran_type = db.Column(db.String(32), nullable=False, info='交易类型：grant:放款,repayinterest：偿还利息,repayprincipal，偿还本金,services：技术服务费,manage:管理费.')
    asset_tran_description = db.Column(db.String(64), nullable=False, info='交易类型中文描述')
    asset_tran_amount = db.Column(db.BigInteger, nullable=False, server_default=db.FetchedValue(), info='实际需要交易的金额 =repaidAmt+balanceAmt')
    asset_tran_decrease_amount = db.Column(db.BigInteger, nullable=False, server_default=db.FetchedValue(), info='减免金额')
    asset_tran_repaid_amount = db.Column(db.BigInteger, nullable=False, server_default=db.FetchedValue(), info='已还金额(分)')
    asset_tran_balance_amount = db.Column(db.BigInteger, nullable=False, server_default=db.FetchedValue(), info='剩余还款金额 ')
    asset_tran_total_amount = db.Column(db.BigInteger, nullable=False, server_default=db.FetchedValue(), info='总金额：包含了 实际还款金额+减免金额=tranAmt+decrease')
    asset_tran_status = db.Column(db.Enum('finish', 'nofinish'), nullable=False, info='状态')
    asset_tran_due_at = db.Column(db.DateTime, nullable=False, index=True, info='预期还款时间')
    asset_tran_finish_at = db.Column(db.DateTime, nullable=False, index=True, info='完成时间')
    asset_tran_period = db.Column(db.Integer, nullable=False, info='期次')
    asset_tran_late_status = db.Column(db.String(20), nullable=False, server_default=db.FetchedValue(), info='逾期状态')
    asset_tran_remark = db.Column(db.String(2048), nullable=False, server_default=db.FetchedValue())
    asset_tran_trade_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='交易时间')
    asset_tran_create_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())
    asset_tran_update_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())



class CapitalAsset(db.Model, BaseToDict):
    __tablename__ = 'capital_asset'
    __table_args__ = (
        db.Index('idx_capital_asset_item_no_type', 'capital_asset_item_no', 'capital_asset_type'),
        db.Index('idx_capital_asset_item_no_channel', 'capital_asset_item_no', 'capital_asset_channel')
    )

    capital_asset_id = db.Column(db.Integer, primary_key=True)
    capital_asset_type = db.Column(db.Enum('package', 'asset'), nullable=False, server_default=db.FetchedValue(), info='资产类型')
    capital_asset_item_no = db.Column(db.String(64), nullable=False, server_default=db.FetchedValue(), info='资产编号')
    capital_asset_holding_days = db.Column(db.Integer, server_default=db.FetchedValue(), info='资产持有天数')
    capital_asset_channel = db.Column(db.String(64), nullable=False, server_default=db.FetchedValue(), info='资金方')
    capital_asset_status = db.Column(db.Enum('sign', 'sale', 'repay', 'payoff'), nullable=False, server_default=db.FetchedValue(), info='状态：sign:签约中，sale，销售中 repay，还款中  payoff，已结清(正常结清)')
    capital_asset_push_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='资产推送到资金方的时间')
    capital_asset_confirm_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='资金方确认资产时间')
    capital_asset_granted_at = db.Column(db.DateTime, nullable=False, index=True, server_default=db.FetchedValue(), info='资金方放款（卖出）时间')
    capital_asset_origin_amount = db.Column(db.BigInteger, nullable=False, server_default=db.FetchedValue(), info='申请金额')
    capital_asset_confirm_amount = db.Column(db.BigInteger, nullable=False, server_default=db.FetchedValue(), info='确认金额')
    capital_asset_granted_amount = db.Column(db.BigInteger, nullable=False, server_default=db.FetchedValue(), info='放款金额')
    capital_asset_create_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='创建时间')
    capital_asset_update_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='更新时间')
    capital_asset_period_count = db.Column(db.Integer, server_default=db.FetchedValue(), info='总期数')
    capital_asset_period_type = db.Column(db.Enum('day', 'month'), nullable=False, server_default=db.FetchedValue(), info='该期周期单位')
    capital_asset_period_term = db.Column(db.SmallInteger, nullable=False, server_default=db.FetchedValue(), info='该期周期长度')
    capital_asset_version = db.Column(db.BigInteger, server_default=db.FetchedValue())



class CapitalNotify(db.Model, BaseToDict):
    __tablename__ = 'capital_notify'

    capital_notify_id = db.Column(db.BigInteger, primary_key=True)
    capital_notify_push_serial = db.Column(db.String(64), nullable=False, index=True)
    capital_notify_asset_item_no = db.Column(db.String(64), nullable=False, index=True, info='资产编号')
    capital_notify_period_start = db.Column(db.Integer, nullable=False, info='还款起始期次')
    capital_notify_period_end = db.Column(db.Integer, nullable=False, info='还款结束期次')
    capital_notify_channel = db.Column(db.String(32), nullable=False, info='放款渠道')
    capital_notify_withhold_serial_no = db.Column(db.String(50), nullable=False, index=True, server_default=db.FetchedValue(), info='执行代扣流水号')
    capital_notify_status = db.Column(db.Enum('open', 'process', 'success', 'fail', 'cancel', 'ready'), nullable=False, server_default=db.FetchedValue(), info='推送状态:')
    capital_notify_req_data = db.Column(db.Text, info='请求消息体内容')
    capital_notify_res_data = db.Column(db.Text, info='接口返回结果内容')
    capital_notify_plan_at = db.Column(db.DateTime, nullable=False, index=True, server_default=db.FetchedValue(), info='计划发送时间')
    capital_notify_type = db.Column(db.String(32), nullable=False, info='overdue：逾期推送,repay：还款推送,payoff:偿清通知')
    capital_notify_to_system = db.Column(db.String(64), nullable=False)
    capital_notify_capital_receive_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='资方接收推送成功时间')
    capital_notify_create_at = db.Column(db.DateTime, nullable=False, index=True, server_default=db.FetchedValue(), info='创建时间')
    capital_notify_update_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='更新时间')


class CapitalSettlementDetail(db.Model, BaseToDict):
    __tablename__ = 'capital_settlement_detail'
    __table_args__ = (
        db.Index('uniq_item_no_channel_period', 'channel', 'asset_item_no', 'period'),
    )

    id = db.Column(db.BigInteger, primary_key=True)
    channel = db.Column(db.String(32), nullable=False, server_default=db.FetchedValue(), info='资方')
    asset_granted_principal_amount = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(),
                                               info='放款金额')
    contract_start_date = db.Column(db.DateTime, info='合同开始日期')
    contract_end_date = db.Column(db.DateTime, info='合同结束日期')
    repay_date = db.Column(db.DateTime, index=True, info='银行还款日期')
    repay_principal = db.Column(db.BigInteger, nullable=False, server_default=db.FetchedValue(), info='银行还款本金')
    repay_interest = db.Column(db.BigInteger, nullable=False, server_default=db.FetchedValue(), info='银行还款利息')
    repay_total_amount = db.Column(db.BigInteger, nullable=False, server_default=db.FetchedValue(), info='还款合计')
    repay_technical_service = db.Column(db.BigInteger, info='技术服务费')
    repay_after_loan_manage = db.Column(db.BigInteger, info='贷后管理费')
    repay_reserve = db.Column(db.BigInteger, info='风险保障金')
    repay_consult = db.Column(db.BigInteger, info='咨询服务费')
    repay_service = db.Column(db.BigInteger, info='服务费')
    repay_guarantee = db.Column(db.BigInteger, info='担保方费')
    repay_lateinterest = db.Column(db.BigInteger, info='罚息')
    asset_item_no = db.Column(db.String(64), nullable=False, index=True, info='资产编号')
    period = db.Column(db.Integer, nullable=False, info='期次')
    type = db.Column(db.String(32), nullable=False, server_default=db.FetchedValue(), info='提前结清类型')
    capital_tran_process_status = db.Column(db.String(32), server_default=db.FetchedValue())
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())
    updated_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())



class CapitalTransaction(db.Model, BaseToDict):
    __tablename__ = 'capital_transaction'
    __table_args__ = (
        db.Index('idx_capital_tran_channel_type_finish_at', 'capital_transaction_channel', 'capital_transaction_type', 'capital_transaction_expect_finished_at'),
        db.Index('idx_capital_transaction_item_no_period', 'capital_transaction_asset_item_no', 'capital_transaction_period')
    )

    capital_transaction_id = db.Column(db.Integer, primary_key=True)
    capital_transaction_asset_id = db.Column(db.Integer, nullable=False, index=True, server_default=db.FetchedValue(), info='capital_asset表主键ID')
    capital_transaction_channel = db.Column(db.String(64), nullable=False, server_default=db.FetchedValue(), info='资金方')
    capital_transaction_grant_id = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), info='资方放款（卖出）记录ID')
    capital_transaction_grant_type = db.Column(db.Enum('cp_sell', 'direct'), server_default=db.FetchedValue(), info='放款类型，cp_sell-债转，direct-直投')
    capital_transaction_type = db.Column(db.String(50), nullable=False, server_default=db.FetchedValue(), info='principal 本金, interest 利息, factoring 保理, service 平台服务费, interest_subsidy 贴息,service_subsidy 贴补服务费')
    capital_transaction_amount = db.Column(db.BigInteger, nullable=False, server_default=db.FetchedValue(), info='金额')
    capital_transaction_repaid_amount = db.Column(db.BigInteger, nullable=False, server_default=db.FetchedValue(), info='已还金额')
    capital_transaction_rate = db.Column(db.Numeric(10, 3), nullable=False, server_default=db.FetchedValue(), info='费率')
    capital_transaction_holding_days = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), info='持有天数')
    capital_transaction_year_days = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), info='年天')
    capital_transaction_expect_finished_at = db.Column(db.Date, nullable=False, index=True, server_default=db.FetchedValue(), info='预计完成时间')
    capital_transaction_expect_operate_at = db.Column(db.DateTime, nullable=False, index=True, server_default=db.FetchedValue(), info='预计结算时间')
    capital_transaction_user_repay_at = db.Column(db.DateTime, nullable=False, index=True, server_default=db.FetchedValue(), info='用户还款时间')
    capital_transaction_actual_operate_at = db.Column(db.DateTime, nullable=False, index=True, server_default=db.FetchedValue(), info='实际结算时间')
    capital_transaction_status = db.Column(db.Enum('unfinished', 'finished'), nullable=False, server_default=db.FetchedValue(), info='unfinished 未完成,finished 完成')
    capital_transaction_is_advance = db.Column(db.Enum('Y', 'N'), nullable=False, server_default=db.FetchedValue(), info='是否提前还款')
    capital_transaction_advance_at = db.Column(db.DateTime, nullable=False, index=True, server_default=db.FetchedValue(), info='提前还款/回购时间')
    capital_transaction_order_id = db.Column(db.Integer, nullable=False, index=True, server_default=db.FetchedValue(), info='资金方结算订单id')
    capital_transaction_operation_type = db.Column(db.String(50), server_default=db.FetchedValue(), info='操作类型 grant-放款  buyback-回购   advance-提前还款  normal-正常还款 overdue-逾期还款')
    capital_transaction_period = db.Column(db.Integer, server_default=db.FetchedValue(), info='期数')
    capital_transaction_withhold_result_channel = db.Column(db.String(50), nullable=False, server_default=db.FetchedValue(), info='代扣渠道')
    capital_transaction_create_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='创建时间')
    capital_transaction_update_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='更新时间')
    capital_transaction_push_success_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='资方时间')
    capital_transaction_process_status = db.Column(db.String(32), server_default=db.FetchedValue(), info='状态：ready,process,fail,success')
    capital_transaction_origin_amount = db.Column(db.BigInteger, nullable=False, server_default=db.FetchedValue(), info='原始金额')
    capital_transaction_asset_item_no = db.Column(db.String(64), nullable=False, server_default=db.FetchedValue())



class CentralSendMsg(db.Model, BaseToDict):
    __tablename__ = 'central_sendmsg'
    __table_args__ = (
        db.Index('idx_sendmsg_priority_type', 'sendmsg_priority', 'sendmsg_type'),
        db.Index('idx_sendmsg_nextRun_status_priority', 'sendmsg_status', 'sendmsg_priority', 'sendmsg_next_run_at')
    )

    sendmsg_id = db.Column(db.BigInteger, primary_key=True)
    sendmsg_order_no = db.Column(db.String(64), nullable=False, index=True, server_default=db.FetchedValue(), info='消息业务编号')
    sendmsg_type = db.Column(db.String(45), nullable=False, info='消息具体类型')
    sendmsg_content = db.Column(db.String, info='消息内容')
    sendmsg_memo = db.Column(db.String(2048), nullable=False, server_default=db.FetchedValue(), info='备注')
    sendmsg_tosystem = db.Column(db.String(64), nullable=False, server_default=db.FetchedValue(), info='msg发送的系统')
    sendmsg_status = db.Column(db.Enum('open', 'running', 'error', 'terminated', 'close'), nullable=False, info='消息状态')
    sendmsg_next_run_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='下次发送时间')
    sendmsg_create_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='消息创建时间')
    sendmsg_update_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='更新时间')
    sendmsg_version = db.Column(db.SmallInteger, nullable=False, server_default=db.FetchedValue(), info='消息版本')
    sendmsg_priority = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), info='消息优先级')
    sendmsg_retrytimes = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), info='消息重试次数')
    sendmsg_response_data = db.Column(db.Text)



class CentralSynctask(db.Model, BaseToDict):
    __tablename__ = 'central_synctask'
    __table_args__ = (
        db.Index('idx_synctask_key_type_sys', 'synctask_key', 'synctask_type', 'synctask_from_system'),
    )

    synctask_id = db.Column(db.BigInteger, primary_key=True)
    synctask_type = db.Column(db.String(50), info='任务类型')
    synctask_key = db.Column(db.String(50), info='任务键值')
    synctask_from_system = db.Column(db.String(50), info='任务来源系统')
    synctask_request_data = db.Column(db.String, info='任务数据，Json格式')
    synctask_response_data = db.Column(db.Text, info='任务执行完车后，返回结果数据，Json格式')
    synctask_memo = db.Column(db.Text, info='任务执行中出现异常时,纪录异常日志')
    synctask_status = db.Column(db.Enum('open', 'running', 'terminated', 'close', 'error'), nullable=False, server_default=db.FetchedValue(), info='任务状态，初始状态Open， 执行中为runing, 错误为error，执行完成为close,错误次数达上限为terminated')
    synctask_create_at = db.Column(db.DateTime, nullable=False, index=True, server_default=db.FetchedValue())
    synctask_update_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())
    synctask_retrytimes = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue())
    synctask_order_no = db.Column(db.String(64), nullable=False, index=True, server_default=db.FetchedValue(), info='业务主键')
    synctask_last_run_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='最后执行时间')


class CentralTask(db.Model, BaseToDict):
    __tablename__ = 'central_task'
    __table_args__ = (
        db.Index('Idx_task_status_priority_run', 'task_status', 'task_priority', 'task_next_run_at'),
    )

    task_id = db.Column(db.BigInteger, primary_key=True)
    task_type = db.Column(db.String(45), nullable=False, info='任务类型')
    task_order_no = db.Column(db.String(64), nullable=False, index=True)
    task_key = db.Column(db.String(64), nullable=False, server_default=db.FetchedValue(), info='任务key')
    task_memo = db.Column(db.Text, info='任务备注')
    task_status = db.Column(db.Enum('open', 'running', 'error', 'terminated', 'close'), nullable=False, info='任务状态')
    task_version = db.Column(db.SmallInteger, nullable=False, server_default=db.FetchedValue(), info='版本号')
    task_priority = db.Column(db.SmallInteger, nullable=False, server_default=db.FetchedValue(), info='任务优先级')
    task_next_run_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='下次运行时间')
    task_create_at = db.Column(db.DateTime, nullable=False, index=True, server_default=db.FetchedValue(), info='创建时间')
    task_update_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='更新时间')
    task_request_data = db.Column(db.String, info='任务请求数据')
    task_response_data = db.Column(db.Text, info='任务返回数据')
    task_retrytimes = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue())



class Holiday(db.Model, BaseToDict):
    __tablename__ = 'holiday'

    holiday_id = db.Column(db.Integer, primary_key=True, info='主键')
    holiday_date = db.Column(db.DateTime, nullable=False, index=True, info='时间')
    holiday_status = db.Column(db.Integer, nullable=False, info='状体(0-工作，1-休息)')
    holiday_create_at = db.Column(db.DateTime, nullable=False, index=True, server_default=db.FetchedValue(), info='创建时间')
    holiday_update_at = db.Column(db.DateTime, nullable=False, index=True, server_default=db.FetchedValue(), info='更新时间')



class WithholdHistory(db.Model, BaseToDict):
    __tablename__ = 'withhold_history'
    __table_args__ = (
        db.Index('idx_withhold_result_channel_finish_at', 'withhold_result_channel', 'withhold_result_finish_at'),
    )

    withhold_history_id = db.Column(db.Integer, primary_key=True, info='主键')
    withhold_result_id = db.Column(db.Integer, nullable=False, index=True, info='代扣主键')
    withhold_result_asset_id = db.Column(db.Integer, nullable=False, index=True, info='资产ID')
    withhold_result_asset_item_no = db.Column(db.String(64), nullable=False, index=True, info='资产编号')
    withhold_result_asset_type = db.Column(db.String(60), nullable=False, info='资产类型')
    withhold_result_asset_period = db.Column(db.Integer, nullable=False, info='资产期数')
    withhold_result_amount = db.Column(db.BigInteger, nullable=False, info='实际代扣金额：单位分')
    withhold_result_user_name = db.Column(db.String(255), info='用户名')
    withhold_result_user_phone = db.Column(db.String(45), info='用户手机号')
    withhold_result_user_id_card = db.Column(db.String(45), info='用户身份证号')
    withhold_result_user_bank_card = db.Column(db.String(45), info='用户银行卡号')
    withhold_result_type = db.Column(db.Enum('auto', 'manual', 'active'), nullable=False, info='类型: auto-自动代扣，manual-手动代扣，active-自主还款')
    withhold_result_status = db.Column(db.Enum('success'), nullable=False, info='代扣状态')
    withhold_result_channel = db.Column(db.String(50), nullable=False, info='代扣渠道')
    withhold_result_serial_no = db.Column(db.String(255), nullable=False, index=True, info='订单号')
    withhold_result_create_at = db.Column(db.DateTime, nullable=False, index=True, server_default=db.FetchedValue(), info='创建时间')
    withhold_result_channel_key = db.Column(db.String(50), index=True, server_default=db.FetchedValue(), info='交易流水号')
    withhold_result_channel_fee = db.Column(db.BigInteger, server_default=db.FetchedValue(), info='通道手续费')
    withhold_result_finish_at = db.Column(db.DateTime, nullable=False, index=True, server_default=db.FetchedValue(), info='完成时间')
    withhold_history_sync_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='更新时间')
    withhold_result_user_name_encrypt = db.Column(db.String(128), nullable=False, server_default=db.FetchedValue(), info='用户名加密')
    withhold_result_user_phone_encrypt = db.Column(db.String(128), nullable=False, server_default=db.FetchedValue(), info='用户手机号加密')
    withhold_result_user_id_card_encrypt = db.Column(db.String(128), nullable=False, server_default=db.FetchedValue(), info='用户身份证号加密')
    withhold_result_user_bank_card_encrypt = db.Column(db.String(128), nullable=False, server_default=db.FetchedValue(), info='用户银行卡号加密')


class CapitalRepayTrial(db.Model, BaseToDict):
    __tablename__ = 'capital_repay_trial'

    capital_repay_trial_id = db.Column(db.BigInteger, primary_key=True)
    capital_repay_trial_item_no = db.Column(db.String(64), nullable=False, index=True, info='资产编号')
    capital_repay_trial_period = db.Column(db.SmallInteger, nullable=False, info='期次')
    capital_repay_trial_type = db.Column(db.String(32), nullable=False, info='试算类型：提前还款、提前结清等')
    capital_repay_trial_amount = db.Column(db.Integer, nullable=False)
    capital_repay_trial_amount_type = db.Column(db.String(32), nullable=False, info='本金、利息等')
    capital_repay_trial_date = db.Column(db.Date, nullable=False, index=True)
    capital_repay_trial_create_at = db.Column(db.DateTime, nullable=False, index=True)
    capital_repay_trial_update_at = db.Column(db.DateTime, nullable=False)
    capital_repay_trial_status = db.Column(db.Enum('unfinished', 'finished'), nullable=False, server_default=db.FetchedValue(), info='试算状态')
    capital_repay_trial_req_no = db.Column(db.String(128), info='试算请求编号')


class WithholdResult(db.Model, BaseToDict):
    __tablename__ = 'withhold_result'
    __table_args__ = (
        db.Index('idx_unique_withhold_serial_no_item_no', 'withhold_result_serial_no', 'withhold_result_asset_item_no'),
        db.Index('idx_withhold_result_channel_owner', 'withhold_result_channel', 'withhold_result_owner'),
        db.Index('idx_withhold_result_finish_at_status', 'withhold_result_finish_at', 'withhold_result_status'),
        db.Index('withhold_result_create_at_asset_id_index', 'withhold_result_create_at', 'withhold_result_asset_id', 'withhold_result_user_id_card'),
        db.Index('withhold_result_status_create_INDEX', 'withhold_result_status', 'withhold_result_create_at')
    )

    withhold_result_id = db.Column(db.Integer, primary_key=True, info='主键')
    withhold_result_asset_id = db.Column(db.Integer, nullable=False, index=True, info='资产ID')
    withhold_result_asset_item_no = db.Column(db.String(64), nullable=False, index=True, info='资产编号')
    withhold_result_asset_type = db.Column(db.String(60), nullable=False, info='资产类型')
    withhold_result_asset_period = db.Column(db.Integer, nullable=False, info='资产期数')
    withhold_result_amount = db.Column(db.Numeric(15, 2), nullable=False, server_default=db.FetchedValue(), info='实际代扣金额：单位分')
    withhold_result_user_name = db.Column(db.String(255), index=True, info='用户名')
    withhold_result_user_phone = db.Column(db.String(45), info='用户手机号')
    withhold_result_user_id_card = db.Column(db.String(45), info='用户身份证号')
    withhold_result_user_bank_card = db.Column(db.String(45), info='用户银行卡号')
    withhold_result_user_bank_card_code = db.Column(db.String(50), nullable=False, info='用户银行卡别')
    withhold_result_type = db.Column(db.Enum('auto', 'manual', 'active'), nullable=False, server_default=db.FetchedValue(), info='类型: auto-自动代扣，manual-手动代扣，active-自主还款')
    withhold_result_status = db.Column(db.Enum('ready', 'success', 'process', 'fail', 'cancel'), nullable=False, server_default=db.FetchedValue(), info='代扣状态')
    withhold_result_channel = db.Column(db.String(50), nullable=False, server_default=db.FetchedValue(), info='代扣渠道')
    withhold_result_serial_no = db.Column(db.String(255), nullable=False, info='订单号')
    withhold_result_comment = db.Column(db.String(255), nullable=False, server_default=db.FetchedValue(), info='备注')
    withhold_result_custom_code = db.Column(db.String(45), nullable=False, server_default=db.FetchedValue(), info='代扣自定义编码')
    withhold_result_request_data = db.Column(db.Text, info='请求内容')
    withhold_result_response_data = db.Column(db.Text, info='返回内容')
    withhold_result_creator = db.Column(db.String(255), nullable=False, info='创建者')
    withhold_result_operator = db.Column(db.String(255), nullable=False, server_default=db.FetchedValue(), info='执行者')
    withhold_result_run_times = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), info='执行次数')
    withhold_result_execute_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='执行时间')
    withhold_result_create_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='创建时间')
    withhold_result_update_at = db.Column(db.DateTime, nullable=False, index=True, server_default=db.FetchedValue(), info='更新时间')
    withhold_result_channel_key = db.Column(db.String(50), index=True, server_default=db.FetchedValue(), info='交易流水号')
    withhold_result_channel_fee = db.Column(db.BigInteger, server_default=db.FetchedValue(), info='通道手续费')
    withhold_result_finish_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='完成时间')
    withhold_result_error_code = db.Column(db.String(32), index=True, server_default=db.FetchedValue(), info='错误代码')
    withhold_result_rbiz_process = db.Column(db.Integer, server_default=db.FetchedValue(), info='是否在rbiz处理')
    withhold_result_owner = db.Column(db.String(24), nullable=False, server_default=db.FetchedValue(), info='所有者')
    withhold_result_user_name_encrypt = db.Column(db.String(128), nullable=False, server_default=db.FetchedValue(), info='用户名加密')
    withhold_result_user_phone_encrypt = db.Column(db.String(128), nullable=False, index=True, server_default=db.FetchedValue(), info='用户手机号加密')
    withhold_result_user_id_card_encrypt = db.Column(db.String(128), nullable=False, index=True, server_default=db.FetchedValue(), info='用户身份证号加密')
    withhold_result_user_bank_card_encrypt = db.Column(db.String(128), nullable=False, index=True, server_default=db.FetchedValue(), info='用户银行卡号加密')
    withhold_result_channel_message = db.Column(db.String(128), nullable=False, server_default=db.FetchedValue())
    withhold_result_capital_receive_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='资方接收时间')
