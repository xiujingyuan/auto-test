# coding: utf-8
from flask_sqlalchemy import SQLAlchemy

from app.common.db_util import BaseToDict

db = SQLAlchemy()


class CleanCapitalSettlementPending(db.Model, BaseToDict):
    __tablename__ = 'clean_capital_settlement_pending'
    __table_args__ = (
        db.Index('idx_clean_capital_settlement_pending_asset_item_no_period', 'asset_item_no', 'period'),
    )

    id = db.Column(db.BigInteger, primary_key=True)
    tran_id = db.Column(db.BigInteger, nullable=False, index=True, info='clean_capital_tran 的id')
    asset_loan_channel = db.Column(db.String(64), nullable=False, server_default=db.FetchedValue(), info='资金方')
    asset_item_no = db.Column(db.String(64), nullable=False, info='资产编号')
    period = db.Column(db.Integer, nullable=False, info='还款期次')
    repay_type = db.Column(db.String(64), nullable=False, info='还款方式，normal:正常， advance:提前还款， early_settlement:提前结清， compensate:代偿,buyback:回购')
    amount_type = db.Column(db.String(64), nullable=False, info='金额类型：本金 - principle, 利息 - interest, 担保费 - guarantee，咨询服务费 - consult，风险保障金 - reserve')
    settlement_amount = db.Column(db.BigInteger, nullable=False, info='结算给资方金额')
    deal_amount = db.Column(db.BigInteger, nullable=False, server_default=db.FetchedValue(), info='处理金额')
    comment = db.Column(db.String(600), nullable=False, server_default=db.FetchedValue(), info='描述/备注')
    status = db.Column(db.String(48), nullable=False, server_default=db.FetchedValue(), info='状态：new-新建，process-处理中，success-已处理，fail-处理失败，需要手动处理')
    expect_finish_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='期望完成时间,到期日')
    expect_operate_at = db.Column(db.DateTime, nullable=False, index=True, info='预计结算日期')
    create_at = db.Column(db.DateTime, nullable=False, index=True, server_default=db.FetchedValue(), info='创建时间')
    update_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='更新时间')


class CleanClearingTrans(db.Model, BaseToDict):
    __tablename__ = 'clean_clearing_trans'
    __table_args__ = (
        db.Index('idx_clean_clearing_trans_status_and_create_at', 'status', 'create_at'),
        db.Index('idx_clean_clearing_trans_status_create_at', 'create_at', 'status'),
        db.Index('uk_clean_clearing_trans_final_no_amount_type_serial_no', 'final_no', 'amount_type', 'withhold_serial_no')
    )

    id = db.Column(db.Integer, primary_key=True, info='主键')
    final_no = db.Column(db.String(64), server_default=db.FetchedValue(), info='唯一键')
    item_no = db.Column(db.String(64), nullable=False, index=True, info='编号')
    loan_channel = db.Column(db.String(64), nullable=False, server_default=db.FetchedValue(), info='资金方, 放款渠道')
    period = db.Column(db.Integer, nullable=False, info='还款期次')
    trans_type = db.Column(db.String(32), nullable=False, info='还款类型：repay_before_compensate-代偿前还款，repay_after_compensate-代偿后还款，compensate-代偿')
    repay_type = db.Column(db.String(64), nullable=False, server_default=db.FetchedValue(), info='还款方式，normal:正常， advance:提前还款， early_settlement:提前结清， compensate:代偿,buyback:回购')
    owner = db.Column(db.String(24), nullable=False, server_default=db.FetchedValue(), info='资产所有权者(KN-快牛、STB)')
    rule_number = db.Column(db.String(50), nullable=False, server_default=db.FetchedValue(), info='费率编号')
    amount_type = db.Column(db.String(64), nullable=False, info='金额类型：本金 - principle, 利息 - interest, 信审费 - audit, 技术服务费 - technical_service, 代偿拨备金 - compensation_allowance, 保理费 - factoring, 平台服务费 - merchant_service, 钱牛牛贴息 - pay_interest, 风险管理费 - risk_manage，风控服务费 - risk_control_service')
    amount = db.Column(db.BigInteger, nullable=False, info='交易金额')
    transfer_out = db.Column(db.String(128), nullable=False, info='转出方')
    transfer_in = db.Column(db.String(128), nullable=False, info='转入方')
    transfer_out_channel_code = db.Column(db.String(128), nullable=False, info='转出方存管账号')
    transfer_in_channel_code = db.Column(db.String(128), nullable=False, info='转入方存管账号')
    is_need_settlement = db.Column(db.Enum('N', 'Y'), nullable=False, info='是否需要结算，Y-需要，N-不需要结算')
    can_settlement = db.Column(db.Enum('N', 'Y'), nullable=False, server_default=db.FetchedValue(), info='能否结算，Y-能结算，N-不能结算')
    status = db.Column(db.String(16), nullable=False, server_default=db.FetchedValue(), info='状态：new-未结算，process-结算中，finished-已结算')
    comment = db.Column(db.Text, info='备注')
    deposit = db.Column(db.String(32), nullable=False, server_default=db.FetchedValue(), info='存管系统  jining:济宁腾桥存管,miyang:济宁觅杨存管,tengqiao:恒丰腾桥存管')
    expect_finish_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='期望完成时间')
    actual_finish_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='实际完成时间')
    expect_settlement_at = db.Column(db.DateTime, nullable=False, index=True, server_default=db.FetchedValue(), info='预计结算时间')
    settlement_at = db.Column(db.DateTime, nullable=False, index=True, server_default=db.FetchedValue(), info='实际结算时间')
    clean_settlement_id = db.Column(db.Integer, index=True, info='结算表id')
    create_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='创建时间')
    update_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='更新时间')
    batch_no = db.Column(db.String(128), nullable=False, index=True, server_default=db.FetchedValue(), info='批次号')
    withhold_serial_no = db.Column(db.String(255), nullable=False, server_default=db.FetchedValue(), info='代扣序列号唯一键，订单号')


class CleanTask(db.Model, BaseToDict):
    __tablename__ = 'clean_task'
    __table_args__ = (
        db.Index('Idx_taskrun_at_status_priority', 'task_status', 'task_priority', 'task_next_run_at'),
    )

    task_id = db.Column(db.Integer, primary_key=True)
    task_order_no = db.Column(db.String(100), nullable=False, index=True, server_default=db.FetchedValue())
    task_type = db.Column(db.String(45), nullable=False)
    task_request_data = db.Column(db.Text, nullable=False)
    task_response_data = db.Column(db.Text, nullable=False)
    task_memo = db.Column(db.String(2048), nullable=False, server_default=db.FetchedValue())
    task_status = db.Column(db.Enum('open', 'running', 'error', 'terminated', 'close'), nullable=False)
    task_next_run_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())
    task_create_at = db.Column(db.DateTime, nullable=False, index=True, server_default=db.FetchedValue())
    task_update_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())
    task_version = db.Column(db.SmallInteger, nullable=False, server_default=db.FetchedValue())
    task_priority = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue())
    task_retrytimes = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue())
