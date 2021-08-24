# coding: utf-8
from flask_sqlalchemy import SQLAlchemy
from app.common.db_util import BaseToDict

db = SQLAlchemy()


class Account(db.Model, BaseToDict):
    __tablename__ = 'account'
    __table_args__ = (
        db.Index('idx_individual_no_owner', 'account_user_id_num', 'account_owner'),
        db.Index('uk_acc_idnum_encrypt', 'account_user_id_num_encrypt', 'account_owner')
    )

    account_id = db.Column(db.BigInteger, primary_key=True, info='账户ID')
    account_no = db.Column(db.String(20), nullable=False, unique=True, info='账户业务主键')
    account_user_id_num = db.Column(db.String(32), nullable=False, server_default=db.FetchedValue(), info='账户用户身份证号')
    account_balance_amount = db.Column(db.BigInteger, nullable=False, server_default=db.FetchedValue(), info='账户余额')
    account_summary = db.Column(db.String(256), nullable=False, server_default=db.FetchedValue(), info='账户摘要，通过account_no, account_user_id_num, balance_amount, update_at 做md5 操作，更新的时候 必须带在where条件中，避免同时更新写脏数据的问题，相当于版本号')
    account_create_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='账户创建时间')
    account_update_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='账户更新时间')
    account_owner = db.Column(db.String(24), nullable=False, server_default=db.FetchedValue(), info='账户拥有方：KN是快牛')
    account_user_id_num_encrypt = db.Column(db.String(128), nullable=False, server_default=db.FetchedValue(), info='身份证密文')



class AccountRecharge(db.Model, BaseToDict):
    __tablename__ = 'account_recharge'

    account_recharge_id = db.Column(db.BigInteger, primary_key=True)
    account_recharge_account_no = db.Column(db.String(64), nullable=False, index=True, info='账户编码')
    account_recharge_source_type = db.Column(db.Enum('withhold', 'singleToMultiple', 'offline', 'coupon', 'provision'), nullable=False, server_default=db.FetchedValue(), info='数据来源：withhold(代扣)、singleToMultiple(单转多)、offline(线下)、coupon(优惠券)、provision(拨备垫资充值)')
    account_recharge_serial_no = db.Column(db.String(64), nullable=False, unique=True, server_default=db.FetchedValue(), info='充值流水号，代扣 使用代扣流水号，其他没有由系统生成')
    account_recharge_trade_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='交易时间，如果是代扣则是代扣完成时间，如果是线下交易，则是线下交易时间时间,如果没有 则是 当前时间')
    account_recharge_amount = db.Column(db.BigInteger, nullable=False, server_default=db.FetchedValue(), info='充值金额，默认0')
    account_recharge_create_at = db.Column(db.DateTime, nullable=False, index=True, server_default=db.FetchedValue(), info='创建时间')
    account_recharge_update_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='更新时间')



class AccountRechargeLog(db.Model, BaseToDict):
    __tablename__ = 'account_recharge_log'

    account_recharge_log_id = db.Column(db.Integer, primary_key=True, info='自增长ID 主键')
    account_recharge_log_recharge_serial_no = db.Column(db.String(64), nullable=False, index=True, info='充值交易业务编号')
    account_recharge_log_account_no = db.Column(db.String(64), nullable=False, index=True, info='账户业务主键')
    account_recharge_log_operate_type = db.Column(db.Enum('withhold_recharge', 'refund', 'offline_recharge', 'coupon_recharge', 'provision_recharge'), nullable=False, info='操作分类:充值、还款等,对应biz atran的atran_type')
    account_recharge_log_card_num = db.Column(db.String(32), nullable=False, server_default=db.FetchedValue(), info='充值银行卡号')
    account_recharge_log_amount_beginning = db.Column(db.BigInteger, nullable=False, server_default=db.FetchedValue(), info='账户变化日志期初值')
    account_recharge_log_amount = db.Column(db.BigInteger, nullable=False, server_default=db.FetchedValue(), info='账户变化日志发生值')
    account_recharge_log_amount_ending = db.Column(db.BigInteger, nullable=False, server_default=db.FetchedValue(), info='账户变化期末值')
    account_recharge_log_late = db.Column(db.Enum('normal', 'late', 'latefinish'), nullable=False, info='资金操作延迟：normal：正常操作；late：操作迟于实际动作；latefinish：操作延迟已经处理')
    account_recharge_log_comment = db.Column(db.String(600), nullable=False, server_default=db.FetchedValue(), info='描述/备注')
    account_recharge_log_operator_id = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), info='操作人员')
    account_recharge_log_operator_name = db.Column(db.String(50), nullable=False, server_default=db.FetchedValue())
    account_recharge_log_create_at = db.Column(db.DateTime, nullable=False, index=True, server_default=db.FetchedValue())
    account_recharge_log_update_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())
    account_recharge_log_card_num_encrypt = db.Column(db.String(128), nullable=False, server_default=db.FetchedValue(), info='充值银行卡号 密文')



class AccountRepay(db.Model, BaseToDict):
    __tablename__ = 'account_repay'
    __table_args__ = (
        db.Index('idx_acc_order_type_serial_no_tran_no', 'account_repay_tran_no', 'account_repay_recharge_serial_no', 'account_repay_order_type'),
    )

    account_repay_id = db.Column(db.BigInteger, primary_key=True)
    account_repay_no = db.Column(db.String(64), nullable=False, unique=True, info='还款编号')
    account_repay_account_no = db.Column(db.String(64), nullable=False, index=True, info='账户编号')
    account_repay_recharge_serial_no = db.Column(db.String(64), nullable=False, index=True, info='充值订单号')
    account_repay_order_type = db.Column(db.Enum('asset', 'combo_order', 'trade_order', 'account'), nullable=False, server_default=db.FetchedValue(), info='还款订单数据类型：asset资产还款，combo_order 期缴订单,trade_order 订单等')
    account_repay_order_no = db.Column(db.String(64), nullable=False, info='资产编号/期缴订单编号/交易订单编号')
    account_repay_tran_no = db.Column(db.String(64), nullable=False, info='data_type对应的业务主键，如asset对应的asset_tran_no，combo_order对应combo_order_tran_no, trade_order对应trade_no')
    account_repay_amount = db.Column(db.BigInteger, nullable=False, server_default=db.FetchedValue(), info='还款金额')
    account_repay_create_at = db.Column(db.DateTime, nullable=False, index=True, server_default=db.FetchedValue(), info='创建时间')
    account_repay_update_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='更新时间')



class AccountRepayLog(db.Model, BaseToDict):
    __tablename__ = 'account_repay_log'

    account_repay_log_id = db.Column(db.BigInteger, primary_key=True)
    account_repay_log_repay_no = db.Column(db.String(64), nullable=False, index=True, server_default=db.FetchedValue(), info='账户还款记录业务主键')
    account_repay_log_account_no = db.Column(db.String(64), nullable=False, index=True, server_default=db.FetchedValue(), info='账户业务主键')
    account_repay_log_operate_type = db.Column(db.Enum('withhold_repay', 'repay_inverse', 'refund', 'decrease_fee', 'account_fix_amt', 'provision_repay'), nullable=False, info='操作类型，还款、逆操作等,operate_category子类')
    account_repay_log_amount_beginning = db.Column(db.BigInteger, nullable=False, server_default=db.FetchedValue(), info='期初金额')
    account_repay_log_amount = db.Column(db.BigInteger, nullable=False, server_default=db.FetchedValue(), info='发生金额')
    account_repay_log_amount_ending = db.Column(db.BigInteger, nullable=False, server_default=db.FetchedValue(), info='期末金额')
    account_repay_log_order_type = db.Column(db.Enum('asset', 'combo_order', 'trade_order', 'account'), nullable=False)
    account_repay_log_order_no = db.Column(db.String(64), nullable=False, index=True, info='订单编号，如果是资产，则是资产编号')
    account_repay_log_order_period = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), info='期次')
    account_repay_log_tran_type = db.Column(db.String(64), nullable=False, server_default=db.FetchedValue(), info='订单类型：asset_tran对应的类型或者其他订单类型,比如:’repayinterest’：偿还利息,’repayprincipal’，偿还本金,‘services’：技术服务费,manage:管理费；')
    account_repay_log_tran_no = db.Column(db.String(64), nullable=False, index=True, server_default=db.FetchedValue(), info='order_type对应的业务主键，如asset_tran对应的asset_tran_no')
    account_repay_log_late = db.Column(db.Enum('normal', 'late', 'latefinish'), nullable=False, info='资金操作延迟：normal：正常操作；late：操作迟于实际动作；latefinish：操作延迟已经处理')
    account_repay_log_comment = db.Column(db.String(600), nullable=False, server_default=db.FetchedValue(), info='描述/备注')
    account_repay_log_operator_id = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), info='操作者，如果没有则是0')
    account_repay_log_operator_name = db.Column(db.String(32), nullable=False, server_default=db.FetchedValue(), info='操作者名称：如果没有则是系统')
    account_repay_log_create_at = db.Column(db.DateTime, nullable=False, index=True, server_default=db.FetchedValue(), info='创建时间')
    account_repay_log_update_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='更新时间')



class Arbitration(db.Model, BaseToDict):
    __tablename__ = 'arbitration'

    arbitration_id = db.Column(db.BigInteger, primary_key=True, info='主键id')
    arbitration_asset_item_no = db.Column(db.String(64), nullable=False, unique=True, info='项目编号')
    arbitration_amount = db.Column(db.BigInteger, nullable=False, server_default=db.FetchedValue(), info='仲裁应还金额')
    arbitration_repaid_amount = db.Column(db.BigInteger, nullable=False, server_default=db.FetchedValue(), info='已还金额')
    arbitration_status = db.Column(db.Enum('nofinish', 'finish'), nullable=False, server_default=db.FetchedValue(), info='仲裁状态')
    arbitration_from_system = db.Column(db.String(255), nullable=False, info='仲裁数据来源')
    arbitration_user_id_num = db.Column(db.String(20), nullable=False, index=True, server_default=db.FetchedValue(), info='仲裁人员身份证号')
    arbitration_user_name = db.Column(db.String(20), nullable=False, server_default=db.FetchedValue(), info='仲裁用户姓名')
    arbitration_create_at = db.Column(db.DateTime, nullable=False, index=True, server_default=db.FetchedValue())
    arbitration_update_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())
    arbitration_user_id_num_encrypt = db.Column(db.String(32), nullable=False, index=True, server_default=db.FetchedValue(), info='身份证 密文字段')
    arbitration_user_name_encrypt = db.Column(db.String(32), nullable=False, server_default=db.FetchedValue(), info='仲裁用户姓名 密文字段')



class Asset(db.Model, BaseToDict):
    __tablename__ = 'asset'

    asset_id = db.Column(db.Integer, primary_key=True, info='资产行号，单表主键')
    asset_no = db.Column(db.String(20), nullable=False, server_default=db.FetchedValue(), info='资产主键')
    asset_item_no = db.Column(db.String(48), nullable=False, unique=True, server_default=db.FetchedValue(), info='项目编号，有一系列规则，用来标识某个项目，可以从项目编号里看到很多信息')
    asset_type = db.Column(db.String(32), nullable=False, server_default=db.FetchedValue(), info='资产类型')
    asset_sub_type = db.Column(db.String(32), nullable=False, server_default=db.FetchedValue())
    asset_period_type = db.Column(db.Enum('month', 'day'), nullable=False, server_default=db.FetchedValue(), info='还款周期类型')
    asset_period_count = db.Column(db.SmallInteger, nullable=False, server_default=db.FetchedValue(), info='还款总期数')
    asset_product_category = db.Column(db.String(16), nullable=False, server_default=db.FetchedValue(), info='资产类别名称：14天，30天，3个月，6个月')
    asset_cmdb_product_number = db.Column(db.String(48), nullable=False, server_default=db.FetchedValue(), info='资产产品在费率系统编号')
    asset_grant_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='放款时间')
    asset_effect_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='合同生效日')
    asset_actual_grant_at = db.Column(db.DateTime, nullable=False, index=True, server_default=db.FetchedValue(), info='实际放款日')
    asset_due_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='资产到期日')
    asset_payoff_at = db.Column(db.DateTime, nullable=False, index=True, server_default=db.FetchedValue(), info='偿清时间')
    asset_from_system = db.Column(db.String(24), nullable=False, server_default=db.FetchedValue())
    asset_status = db.Column(db.Enum('sign', 'sale', 'repay', 'payoff', 'void', 'writeoff', 'late', 'lateoff'), nullable=False, server_default=db.FetchedValue(), info='资产状态')
    asset_principal_amount = db.Column(db.BigInteger, nullable=False, server_default=db.FetchedValue(), info='合同本金(不包含减免)')
    asset_granted_principal_amount = db.Column(db.BigInteger, nullable=False, server_default=db.FetchedValue(), info='实际放款本金')
    asset_decrease_principal_amount = db.Column(db.BigInteger, nullable=False, server_default=db.FetchedValue(), info='本金减免')
    asset_loan_channel = db.Column(db.String(32), nullable=False, server_default=db.FetchedValue(), info='放款渠道')
    asset_alias_name = db.Column(db.String(64), nullable=False, server_default=db.FetchedValue(), info='资产名称')
    asset_interest_amount = db.Column(db.BigInteger, nullable=False, server_default=db.FetchedValue(), info='利息总金额(不包括减免)')
    asset_decrease_interest_amount = db.Column(db.BigInteger, nullable=False, server_default=db.FetchedValue(), info='利息减免金额')
    asset_fee_amount = db.Column(db.BigInteger, nullable=False, server_default=db.FetchedValue(), info='费总金额(不包括减免)')
    asset_decrease_fee_amount = db.Column(db.BigInteger, nullable=False, server_default=db.FetchedValue(), info='费用减免金额')
    asset_balance_amount = db.Column(db.BigInteger, nullable=False, server_default=db.FetchedValue(), info='剩余未偿还总金额(分）包括：本，息，费(=principal_amt+interest_amount+fee_amount-repaid)')
    asset_repaid_amount = db.Column(db.BigInteger, nullable=False, server_default=db.FetchedValue(), info='已偿还总金额(已还本息费)')
    asset_total_amount = db.Column(db.BigInteger, nullable=False, server_default=db.FetchedValue(), info='本息费总额(=principal_amount+decrease+interest_amount+decrease+fee_amount+decrease)。')
    asset_interest_rate = db.Column(db.Numeric(10, 3), nullable=False, server_default=db.FetchedValue(), info='利率')
    asset_create_at = db.Column(db.DateTime, nullable=False, index=True, server_default=db.FetchedValue(), info='创建时间')
    asset_rbiz_create_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='rbiz创建时间')
    asset_update_at = db.Column(db.DateTime, nullable=False, index=True, server_default=db.FetchedValue())
    asset_rbiz_update_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='rbiz更新时间')
    asset_last_sync_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='资产上次同步时间')
    asset_channel_id = db.Column(db.Integer, server_default=db.FetchedValue(), info='渠道id')
    asset_from_system_name = db.Column(db.String(24), nullable=False, server_default=db.FetchedValue(), info='资产来源系统名称')
    asset_owner = db.Column(db.String(24), nullable=False, server_default=db.FetchedValue(), info='资产所有权者')
    asset_actual_payoff_at = db.Column(db.DateTime, index=True, server_default=db.FetchedValue(), info='实际结清时间')
    asset_late_amount = db.Column(db.BigInteger, server_default=db.FetchedValue(), info='包含所有的逾期费用')
    asset_due_bill_no = db.Column(db.String(50), index=True, server_default=db.FetchedValue(), info='资方合同编号')
    asset_repaid_principal_amount = db.Column(db.BigInteger, server_default=db.FetchedValue(), info='已还本金金额')
    asset_repaid_interest_amount = db.Column(db.BigInteger, server_default=db.FetchedValue(), info='已还利息金额')
    asset_repaid_fee_amount = db.Column(db.BigInteger, server_default=db.FetchedValue(), info='已还费用金额')
    asset_repaid_late_amount = db.Column(db.BigInteger, server_default=db.FetchedValue(), info='已还逾期费用金额')
    asset_decrease_late_amount = db.Column(db.BigInteger, server_default=db.FetchedValue(), info='减免费用金额')
    asset_from_app = db.Column(db.String(30), nullable=False, server_default=db.FetchedValue(), info='马甲包')
    asset_repayment_app = db.Column(db.String(10), nullable=False, server_default=db.FetchedValue())
    asset_last_late_at = db.Column(db.DateTime, server_default=db.FetchedValue(), info='最新刷新罚息时间')
    asset_full_late_flag = db.Column(db.Enum('yes', 'no'), server_default=db.FetchedValue(), info='是否为最大罚息')



class AssetExtend(db.Model, BaseToDict):
    __tablename__ = 'asset_extend'

    asset_extend_id = db.Column(db.Integer, primary_key=True)
    asset_extend_asset_no = db.Column(db.String(20), nullable=False, server_default=db.FetchedValue(), info='资产主建')
    asset_extend_asset_item_no = db.Column(db.String(48), nullable=False, index=True, server_default=db.FetchedValue(), info='项目编号,关联asset')
    asset_extend_type = db.Column(db.String(20), nullable=False, server_default=db.FetchedValue(), info='扩展类型：district_id ：资产行正区化id; charge_type：计费类型，0-砍头息，1-后置收费；identifier：编号；trade_no：进件流水号；due_bill_no：借据号')
    asset_extend_val = db.Column(db.Text)
    asset_extend_create_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())
    asset_extend_update_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='更新时间')
    asset_extend_last_sync_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='上次同步时间')



class AssetFoxLog(db.Model, BaseToDict):
    __tablename__ = 'asset_fox_log'

    asset_fox_log_id = db.Column(db.BigInteger, primary_key=True)
    asset_fox_log_item_no = db.Column(db.String(48), nullable=False, unique=True, info='资产编号')
    asset_fox_log_sync_count = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), info='同步次数')
    asset_fox_log_create_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='推送fox创建时间')
    asset_fox_log_last_sync_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='上次同步时间')



class AssetFoxLogDetail(db.Model, BaseToDict):
    __tablename__ = 'asset_fox_log_detail'

    asset_fox_log_detail_id = db.Column(db.BigInteger, primary_key=True)
    asset_fox_log_detail_item_no = db.Column(db.String(48), nullable=False, index=True, info='资产编号')
    asset_fox_log_detail_action_type = db.Column(db.String(255), info='同步类型')
    asset_fox_log_detail_create_at = db.Column(db.DateTime, nullable=False, index=True, server_default=db.FetchedValue())



class AssetLateFeeRefreshLog(db.Model, BaseToDict):
    __tablename__ = 'asset_late_fee_refresh_log'

    asset_late_fee_refresh_log_id = db.Column(db.BigInteger, primary_key=True)
    asset_late_fee_refresh_log_asset_item_no = db.Column(db.String(48), nullable=False, unique=True, info='Asset id')
    asset_late_fee_refresh_log_refresh_times = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), info='刷新次数')
    asset_late_fee_refresh_log_create_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())
    asset_late_fee_refresh_log_update_at = db.Column(db.DateTime, nullable=False, index=True, server_default=db.FetchedValue())
    asset_late_fee_refresh_log_item_type = db.Column(db.String(32), nullable=False, server_default=db.FetchedValue(), info='类型：asset-资产，combo_order-第三单')



class AssetOperationAuth(db.Model, BaseToDict):
    __tablename__ = 'asset_operation_auth'
    __table_args__ = (
        db.Index('ITEMNO_PERIOD_ACTION', 'asset_operation_auth_asset_item_no', 'asset_operation_auth_period', 'asset_operation_auth_action'),
    )

    asset_operation_auth_id = db.Column(db.BigInteger, primary_key=True)
    asset_operation_auth_asset_item_no = db.Column(db.String(100))
    asset_operation_auth_period = db.Column(db.Integer, nullable=False, info='期数')
    asset_operation_auth_action = db.Column(db.Enum('withhold', 'other', 'withholdAuto', 'createWithholdAutoTask'), nullable=False, info='操作类型')
    asset_operation_auth_create_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())
    asset_operation_auth_update_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())
    asset_operation_auth_owner = db.Column(db.String(32), nullable=False, server_default=db.FetchedValue(), info='锁拥有者')



class AssetRepayAudit(db.Model, BaseToDict):
    __tablename__ = 'asset_repay_audit'

    ara_id = db.Column(db.Integer, primary_key=True, info='主键')
    ara_asset_item_no = db.Column(db.String(64), nullable=False, index=True, info='资产编号')
    ara_status = db.Column(db.Enum('new', 'approved', 'rejected'), nullable=False, server_default=db.FetchedValue(), info='审核状态')
    ara_principal_amount = db.Column(db.Numeric(15, 2), nullable=False, server_default=db.FetchedValue(), info='应还本金')
    ara_actual_principal_amount = db.Column(db.Numeric(15, 2), nullable=False, server_default=db.FetchedValue(), info='实还本金')
    ara_interest_amount = db.Column(db.Numeric(15, 2), nullable=False, server_default=db.FetchedValue(), info='应还款利息')
    ara_actual_interest_amount = db.Column(db.Numeric(15, 2), nullable=False, server_default=db.FetchedValue(), info='实还利息')
    ara_penalty_amount = db.Column(db.Numeric(15, 2), nullable=False, server_default=db.FetchedValue(), info='应还违约金')
    ara_actual_penalty_amount = db.Column(db.Numeric(15, 2), nullable=False, server_default=db.FetchedValue(), info='实还违约金')
    ara_late_service_amount = db.Column(db.Numeric(15, 2), nullable=False, server_default=db.FetchedValue(), info='应还逾期服务费')
    ara_actual_late_service_amount = db.Column(db.Numeric(15, 2), nullable=False, server_default=db.FetchedValue(), info='实还逾期服务费')
    ara_qsc_service_amount = db.Column(db.Numeric(15, 2), nullable=False, server_default=db.FetchedValue(), info='应还渠道服务费')
    ara_actual_qsc_service_amount = db.Column(db.Numeric(15, 2), nullable=False, server_default=db.FetchedValue(), info='实还渠道服务费')
    ara_late_manage_amount = db.Column(db.Numeric(15, 2), nullable=False, server_default=db.FetchedValue(), info='应还逾期管理费')
    ara_actual_late_manage_amount = db.Column(db.Numeric(15, 2), nullable=False, server_default=db.FetchedValue(), info='实还逾期管理费')
    ara_apply_comment = db.Column(db.String(255), nullable=False, server_default=db.FetchedValue(), info='申请备注')
    ara_review_comment = db.Column(db.String(255), nullable=False, server_default=db.FetchedValue(), info='审核备注')
    ara_applicant = db.Column(db.String(255), nullable=False, info='申请人')
    ara_reviewer = db.Column(db.String(255), nullable=False, server_default=db.FetchedValue(), info='审核人')
    ara_notify_flag = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), info='通知标志位，0为未通知，1为已通知')
    ara_create_at = db.Column(db.DateTime, nullable=False, index=True, server_default=db.FetchedValue(), info='创建时间')
    ara_update_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='更新时间')
    ara_service_amount = db.Column(db.Numeric(15, 2), nullable=False, server_default=db.FetchedValue(), info='应还服务费')
    ara_actual_service_amount = db.Column(db.Numeric(15, 2), nullable=False, server_default=db.FetchedValue(), info='实还服务费')
    ara_actual_repay_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='实际还款时间')



class AssetRepayRecord(db.Model, BaseToDict):
    __tablename__ = 'asset_repay_record'

    asset_repay_record_id = db.Column(db.Integer, primary_key=True, info='主键')
    asset_repay_record_asset_no = db.Column(db.String(20), nullable=False, server_default=db.FetchedValue(), info='资产主建')
    asset_repay_record_asset_item_no = db.Column(db.String(48), nullable=False, index=True, info='资产编号')
    asset_repay_record_period = db.Column(db.Integer, nullable=False, info='还款期数')
    asset_repay_record_status = db.Column(db.SmallInteger, nullable=False, server_default=db.FetchedValue(), info='还款状态：0-未完成，1-已完成')
    asset_repay_record_channel = db.Column(db.String(35), nullable=False, info='渠道')
    asset_repay_record_principal_amount = db.Column(db.BigInteger, nullable=False, info='本金,单位：分')
    asset_repay_record_repaid_principal_amount = db.Column(db.BigInteger, nullable=False, info='已还本金,单位：分')
    asset_repay_record_interest_amount = db.Column(db.BigInteger, nullable=False, info='利息,单位：分')
    asset_repay_record_repaid_interest_amount = db.Column(db.BigInteger, nullable=False, server_default=db.FetchedValue(), info='已还利息,单位：分')
    asset_repay_record_fee_amount = db.Column(db.BigInteger, nullable=False, info='服务费,单位：分')
    asset_repay_record_repaid_fee_amount = db.Column(db.BigInteger, nullable=False, server_default=db.FetchedValue(), info='已还服务费,单位：分')
    asset_repay_record_repay_date = db.Column(db.DateTime, nullable=False, index=True, info='预期还款日')
    asset_repay_record_fee_commission_amt = db.Column(db.BigInteger, nullable=False, server_default=db.FetchedValue(), info='费用分润金额（单位分）')
    asset_repay_record_principal_commission_amt = db.Column(db.BigInteger, nullable=False, server_default=db.FetchedValue(), info='本金分润金额（单位分')
    asset_repay_record_interest_commission_amt = db.Column(db.BigInteger, nullable=False, server_default=db.FetchedValue(), info='利息分润金额（单位分）')
    asset_repay_record_payoff_at = db.Column(db.DateTime, nullable=False, index=True, server_default=db.FetchedValue(), info='实际还款日')
    asset_repay_record_is_deleted = db.Column(db.SmallInteger, nullable=False, server_default=db.FetchedValue(), info='是否删除：0-未删除，1-已删除')
    asset_repay_record_is_advance = db.Column(db.SmallInteger, nullable=False, server_default=db.FetchedValue(), info='是否提前结清')
    asset_repay_record_create_at = db.Column(db.DateTime, nullable=False, index=True, server_default=db.FetchedValue(), info='创建时间')
    asset_repay_record_update_at = db.Column(db.DateTime, nullable=False, index=True, server_default=db.FetchedValue(), info='更新时间')
    asset_repay_record_is_raised = db.Column(db.SmallInteger, nullable=False, server_default=db.FetchedValue(), info='海南还款后是否归集：0-未归集，1-已归集')
    asset_repay_record_last_sync_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())



class AssetTran(db.Model, BaseToDict):
    __tablename__ = 'asset_tran'
    __table_args__ = (
        db.Index('unique_item_no_type_period', 'asset_tran_asset_item_no', 'asset_tran_period', 'asset_tran_type'),
        db.Index('idx_asset_tran_status_due_at', 'asset_tran_status', 'asset_tran_due_at')
    )

    asset_tran_id = db.Column(db.Integer, primary_key=True, info='表主键')
    asset_tran_no = db.Column(db.String(20), nullable=False, unique=True, info='还款计划主键')
    asset_tran_asset_no = db.Column(db.String(20), nullable=False, server_default=db.FetchedValue(), info='资产主建')
    asset_tran_asset_item_no = db.Column(db.String(48), nullable=False, server_default=db.FetchedValue(), info='项目编号,关联asset')
    asset_tran_category = db.Column(db.Enum('grant', 'principal', 'interest', 'fee', 'late'), nullable=False)
    asset_tran_type = db.Column(db.String(32), nullable=False, info="交易类型：\\n'grant’:放款\\n’repayinterest’：偿还利息\\n'repayprincipal’，偿还本金\\n‘services’：技术服务费\\nmanage:管理费.")
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
    asset_tran_repay_priority = db.Column(db.SmallInteger, nullable=False, info='还款顺序/优先级')
    asset_tran_trade_at = db.Column(db.DateTime, nullable=False, info='交易时间')
    asset_tran_create_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())
    asset_tran_rbiz_create_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='rbiz创建时间')
    asset_tran_update_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())
    asset_tran_rbiz_update_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='rbiz更新时间')
    asset_tran_last_sync_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='上次更新时间戳')


class AssetTranLog(db.Model, BaseToDict):
    __tablename__ = 'asset_tran_log'

    asset_tran_log_id = db.Column(db.BigInteger, primary_key=True)
    asset_tran_log_asset_item_no = db.Column(db.String(64), nullable=False, index=True, info='资产编号')
    asset_tran_log_asset_tran_no = db.Column(db.String(64), nullable=False, index=True, info='asset_tran 表对应的业务主键')
    asset_tran_log_ref_no = db.Column(db.String(64), nullable=False, index=True, server_default=db.FetchedValue(), info='引用字段的编号')
    asset_tran_log_operate_type = db.Column(db.Enum('withhold_repay', 'repay_inverse', 'refund', 'decrease_fee', 'refresh_fee', 'increase_fee', 'correct_late_fee', 'tran_settle', 'fix_status', 'provision_repay'), nullable=False)
    asset_tran_log_operate_flag = db.Column(db.String(20), nullable=False, info="操作类型：'normal','machine','human'")
    asset_tran_log_comment = db.Column(db.String(500), nullable=False, server_default=db.FetchedValue(), info='备注')
    asset_tran_log_from_system = db.Column(db.Enum('rbiz', 'biz', 'cmdb', 'fox', 'dsq', 'capital', 'crm'), nullable=False, info='来源')
    asset_tran_log_amount = db.Column(db.BigInteger, nullable=False, server_default=db.FetchedValue(), info='金额(分为单位)')
    asset_tran_log_operator_id = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), info='操作人')
    asset_tran_log_operator_name = db.Column(db.String(32), nullable=False, server_default=db.FetchedValue())
    asset_tran_log_create_at = db.Column(db.DateTime, nullable=False, index=True, server_default=db.FetchedValue())
    asset_tran_log_update_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())



class Buyback(db.Model, BaseToDict):
    __tablename__ = 'buyback'

    buyback_id = db.Column(db.BigInteger, primary_key=True)
    buyback_asset_item_no = db.Column(db.String(48), nullable=False, unique=True, info='资产编号')
    buyback_asset_period_count = db.Column(db.Integer, nullable=False, info='资产总期数')
    buyback_asset_loan_channel = db.Column(db.String(255), nullable=False, info='放款渠道')
    buyback_capital_serial_no = db.Column(db.String(255), nullable=False, server_default=db.FetchedValue(), info='资方回购时的序列号')
    buyback_start_date = db.Column(db.Date, nullable=False, index=True, info='回购开始日期')
    buyback_end_date = db.Column(db.Date, nullable=False, info='回购结束日期')
    buyback_hold_day = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), info='计息天数')
    buyback_notify_type = db.Column(db.String(255), nullable=False, server_default=db.FetchedValue(), info='回购通知方式：query 查询资方 notify 资方通知')
    buyback_min_period = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), info='回购最小期次')
    buyback_principal = db.Column(db.BigInteger, nullable=False, info='回购本金')
    buyback_interest = db.Column(db.BigInteger, nullable=False, server_default=db.FetchedValue(), info='回购利息')
    buyback_fee = db.Column(db.BigInteger, nullable=False, info='回购费用')
    buyback_create_at = db.Column(db.DateTime, nullable=False, index=True, server_default=db.FetchedValue(), info='创建时间')
    buyback_update_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='更新时间')



class BuybackTran(db.Model, BaseToDict):
    __tablename__ = 'buyback_tran'
    __table_args__ = (
        db.Index('idx_buyback_tran_item_no_period_type', 'buyback_tran_asset_item_no', 'buyback_tran_type', 'buyback_tran_period'),
    )

    buyback_tran_id = db.Column(db.BigInteger, primary_key=True)
    buyback_tran_asset_item_no = db.Column(db.String(48), nullable=False, info='资产编号')
    buyback_tran_period = db.Column(db.Integer, nullable=False, info='回购期次')
    buyback_tran_type = db.Column(db.String(32), nullable=False, info='回购还款计划类型')
    buyback_tran_amount = db.Column(db.BigInteger, nullable=False, server_default=db.FetchedValue(), info='回购还款计划金额')
    buyback_tran_due_at = db.Column(db.DateTime, nullable=False, info='还款计划预计完成时间')
    buyback_tran_create_at = db.Column(db.DateTime, nullable=False, index=True, server_default=db.FetchedValue())
    buyback_tran_update_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())


class CapitalAsset(db.Model, BaseToDict):
    __tablename__ = 'capital_asset'

    capital_asset_id = db.Column(db.BigInteger, primary_key=True)
    capital_asset_item_no = db.Column(db.String(48), nullable=False, unique=True, server_default=db.FetchedValue(), info='资产编号')
    capital_asset_channel = db.Column(db.String(32), nullable=False, server_default=db.FetchedValue(), info='资金方')
    capital_asset_period_count = db.Column(db.SmallInteger, nullable=False, server_default=db.FetchedValue(), info='总期数')
    capital_asset_period_term = db.Column(db.SmallInteger, nullable=False, server_default=db.FetchedValue(), info='周期长度')
    capital_asset_period_type = db.Column(db.Enum('day', 'month'), nullable=False, server_default=db.FetchedValue(), info='周期单位')
    capital_asset_push_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='进件时间')
    capital_asset_granted_at = db.Column(db.DateTime, nullable=False, index=True, server_default=db.FetchedValue(), info='资方起息时间')
    capital_asset_due_at = db.Column(db.DateTime, nullable=False, index=True, server_default=db.FetchedValue(), info='资产到期日')
    capital_asset_granted_amount = db.Column(db.BigInteger, nullable=False, server_default=db.FetchedValue(), info='放款金额')
    capital_asset_cmdb_no = db.Column(db.String(48), nullable=False, server_default=db.FetchedValue(), info='资产产品在费率系统编号')
    capital_asset_year_days = db.Column(db.SmallInteger, nullable=False, server_default=db.FetchedValue(), info='年化天数')
    capital_asset_create_at = db.Column(db.DateTime, nullable=False, index=True, server_default=db.FetchedValue(), info='创建时间')
    capital_asset_update_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='更新时间')
    capital_asset_status = db.Column(db.Enum('repay', 'payoff'), nullable=False, server_default=db.FetchedValue(), info='还款状态(repay:代还款, payoff:已偿清)')
    capital_asset_finish_at = db.Column(db.DateTime, nullable=False, index=True, server_default=db.FetchedValue(), info='偿清时间')
    capital_asset_version = db.Column(db.SmallInteger, nullable=False, server_default=db.FetchedValue(), info='版本号')



class CapitalConfig(db.Model, BaseToDict):
    __tablename__ = 'capital_config'

    capital_config_id = db.Column(db.Integer, primary_key=True, info='主键')
    capital_config_code = db.Column(db.String(32), nullable=False, unique=True, info='渠道code')
    capital_config_name = db.Column(db.String(32), nullable=False, info='渠道名称')
    capital_config_status = db.Column(db.Enum('valid', 'invalid'), nullable=False, server_default=db.FetchedValue(), info='状态：valid 有效：invalid无效')
    capital_config_open_channel = db.Column(db.Enum('Y', 'N'), nullable=False, server_default=db.FetchedValue(), info='是否启用该通道 y 启用，n 不启用')
    capital_config_create_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='创建时间')
    capital_config_update_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='更新时间')
    capital_config_need_split = db.Column(db.Enum('Y', 'N'), nullable=False, server_default=db.FetchedValue(), info='是否需要拆单，默认为n')



class CapitalNotify(db.Model, BaseToDict):
    __tablename__ = 'capital_notify'

    capital_notify_id = db.Column(db.BigInteger, primary_key=True)
    capital_notify_asset_item_no = db.Column(db.String(64), nullable=False, index=True, info='资产编号')
    capital_notify_period_start = db.Column(db.Integer, nullable=False, info='还款起始期次')
    capital_notify_period_end = db.Column(db.Integer, nullable=False, info='还款结束期次')
    capital_notify_loan_channel = db.Column(db.String(32), nullable=False, info='放款渠道')
    capital_notify_withhold_result_serial_no = db.Column(db.String(50), index=True, info='执行代扣流水号')
    capital_notify_status = db.Column(db.Enum('open', 'ready', 'process', 'success', 'fail'), nullable=False, server_default=db.FetchedValue(), info='推送状态:')
    capital_notify_push_info = db.Column(db.Text, info='推送信息-根据资金方通知需求，记录计算明细，便于通知失败排查问题')
    capital_notify_req_data = db.Column(db.Text, info='请求消息体内容')
    capital_notify_res_data = db.Column(db.Text, info='接口返回结果内容')
    capital_notify_create_at = db.Column(db.DateTime, nullable=False, index=True, server_default=db.FetchedValue(), info='创建时间')
    capital_notify_update_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='更新时间')
    capital_notify_plan_at = db.Column(db.DateTime, nullable=False, index=True, info='计划发送时间')
    capital_notify_res_msg = db.Column(db.Text)
    capital_notify_action_type = db.Column(db.Enum('overdue', 'repay', 'payoff', 'register'), nullable=False, info='overdue：逾期推送,repay：还款推送,payoff:偿清通知, register:还款计划上报')
    capital_notify_capital_receive_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='资方接收推送成功时间')



class CapitalReconLog(db.Model, BaseToDict):
    __tablename__ = 'capital_recon_log'

    capital_recon_log_id = db.Column(db.BigInteger, primary_key=True)
    capital_recon_log_asset_channel = db.Column(db.String(32), nullable=False, server_default=db.FetchedValue(), info='资金方编码')
    capital_recon_log_recon_start_at = db.Column(db.DateTime, nullable=False, index=True, server_default=db.FetchedValue(), info='对账开始时间')
    capital_recon_log_recon_end_at = db.Column(db.DateTime, nullable=False, index=True, server_default=db.FetchedValue(), info='对账结束时间')
    capital_recon_log_total_count = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), info='对账数据总量')
    capital_recon_log_total_repay_amount = db.Column(db.BigInteger, nullable=False, server_default=db.FetchedValue(), info='对账还款总金额')
    capital_recon_log_total_principal = db.Column(db.BigInteger, nullable=False, server_default=db.FetchedValue(), info='对账本金总额')
    capital_recon_log_total_interest = db.Column(db.BigInteger, nullable=False, server_default=db.FetchedValue(), info='对账利息总额')
    capital_recon_log_total_interest_split = db.Column(db.BigInteger, nullable=False, server_default=db.FetchedValue(), info='对账利息分账总额')
    capital_recon_log_req_data = db.Column(db.Text, nullable=False, info='对账请求的源数据')
    capital_recon_log_res_data = db.Column(db.String, nullable=False, info='对账返回的源数据')
    capital_recon_log_create_at = db.Column(db.DateTime, nullable=False, index=True, server_default=db.FetchedValue(), info='创建时间')
    capital_recon_log_update_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='更新时间')



class CapitalRepayTran(db.Model, BaseToDict):
    __tablename__ = 'capital_repay_tran'
    __table_args__ = (
        db.Index('un_capital_repay_tran_itemno_period', 'capital_repay_tran_asset_item_no', 'capital_repay_tran_asset_period'),
    )

    capital_repay_tran_id = db.Column(db.BigInteger, primary_key=True)
    capital_repay_tran_asset_channel = db.Column(db.String(32), nullable=False, server_default=db.FetchedValue(), info='资金方编码')
    capital_repay_tran_asset_item_no = db.Column(db.String(48), nullable=False, server_default=db.FetchedValue(), info='平台资产编号')
    capital_repay_tran_asset_period = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), info='还款期数')
    capital_repay_tran_order_no = db.Column(db.String(64), nullable=False, server_default=db.FetchedValue(), info='资金方订单ID')
    capital_repay_tran_serial_no = db.Column(db.String(64), nullable=False, server_default=db.FetchedValue(), info='资金方提供的还款流水')
    capital_repay_tran_repay_type = db.Column(db.Enum('advance', 'normal', 'compensate', 'buyback'), nullable=False, server_default=db.FetchedValue(), info='还款类型 advance-用户提前还款并且未回购，normal-用户到期日还款并且未回购，compensate-逾期由我方刚兑之后，buyback-回购')
    capital_repay_tran_amount = db.Column(db.BigInteger, nullable=False, server_default=db.FetchedValue(), info='还款金额')
    capital_repay_tran_principal = db.Column(db.BigInteger, nullable=False, server_default=db.FetchedValue(), info='还款本金')
    capital_repay_tran_interest = db.Column(db.BigInteger, nullable=False, server_default=db.FetchedValue(), info='还款利息')
    capital_repay_tran_interest_split = db.Column(db.BigInteger, nullable=False, server_default=db.FetchedValue(), info='还款利息分账')
    capital_repay_tran_id_card = db.Column(db.String(32), nullable=False, server_default=db.FetchedValue(), info='身份证')
    capital_repay_tran_bank_card = db.Column(db.String(32), nullable=False, server_default=db.FetchedValue(), info='银行卡')
    capital_repay_tran_real_name = db.Column(db.String(32), nullable=False, server_default=db.FetchedValue(), info='姓名')
    capital_repay_tran_phone = db.Column(db.String(32), nullable=False, server_default=db.FetchedValue(), info='手机')
    capital_repay_tran_repay_at = db.Column(db.DateTime, nullable=False, index=True, server_default=db.FetchedValue(), info='还款时间')
    capital_repay_tran_create_at = db.Column(db.DateTime, nullable=False, index=True, server_default=db.FetchedValue(), info='创建时间')
    capital_repay_tran_update_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='更新时间')
    capital_repay_tran_service = db.Column(db.BigInteger, nullable=False, server_default=db.FetchedValue(), info='还款服务费')
    capital_repay_tran_status = db.Column(db.Enum('ready', 'success', 'fail', 'process', 'cancel'), info=' 状态 ready :就绪 、process：处理中、fail：失败、success：成功')
    capital_repay_tran_id_card_encrypt = db.Column(db.String(32), nullable=False, server_default=db.FetchedValue(), info='身份证 密文')
    capital_repay_tran_bank_card_encrypt = db.Column(db.String(32), nullable=False, server_default=db.FetchedValue(), info='银行卡 密文')
    capital_repay_tran_real_name_encrypt = db.Column(db.String(32), nullable=False, server_default=db.FetchedValue(), info='姓名 密文')
    capital_repay_tran_phone_encrypt = db.Column(db.String(32), nullable=False, server_default=db.FetchedValue(), info='手机 密文')



class CapitalRoute(db.Model, BaseToDict):
    __tablename__ = 'capital_route'

    capital_route_id = db.Column(db.Integer, primary_key=True, info='主键')
    capital_route_config_code = db.Column(db.String(32), nullable=False, info='代扣渠道编码')
    capital_route_status = db.Column(db.Enum('valid', 'invalid'), nullable=False, server_default=db.FetchedValue(), info='状态  有效:valid 无效: invalid')
    capital_route_conditional = db.Column(db.String(32), nullable=False, info='条件code')
    capital_route_conditional_value = db.Column(db.Text, info='取值')
    capital_route_change_pay_server = db.Column(db.Enum('Y', 'N'), nullable=False, server_default=db.FetchedValue(), info='是否切换payserver')
    capital_route_express = db.Column(db.String(255), nullable=False, info='条件表达式')
    capital_route_create_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='创建时间')
    capital_route_update_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='更新时间')
    capital_route_index = db.Column(db.Integer, nullable=False, info='校验顺序')



class CapitalTransaction(db.Model, BaseToDict):
    __tablename__ = 'capital_transaction'
    __table_args__ = (
        db.Index('uniq_capital_transaction_item_no_period_type', 'capital_transaction_item_no', 'capital_transaction_period', 'capital_transaction_type'),
    )

    capital_transaction_id = db.Column(db.BigInteger, primary_key=True)
    capital_transaction_item_no = db.Column(db.String(48), nullable=False, server_default=db.FetchedValue(), info='资产编号')
    capital_transaction_period = db.Column(db.SmallInteger, nullable=False, server_default=db.FetchedValue(), info='期数')
    capital_transaction_period_term = db.Column(db.SmallInteger, nullable=False, server_default=db.FetchedValue(), info='该期周期长度')
    capital_transaction_period_type = db.Column(db.Enum('day', 'month'), nullable=False, server_default=db.FetchedValue(), info='该期周期单位')
    capital_transaction_type = db.Column(db.String(50), nullable=False, info='明细类型(principal:本金,interest:利息,our_service:我方服务费,service:资方服务费,factoring:保理,interest_subsidy:贴息,service_subsidy:贴补服务费, after_loan_manage:贷后管理费, guarantee:担保费, guarantee_service:担保服务费)')
    capital_transaction_amount = db.Column(db.BigInteger, nullable=False, server_default=db.FetchedValue(), info='金额')
    capital_transaction_rate = db.Column(db.Numeric(10, 8), nullable=False, server_default=db.FetchedValue(), info='费率/利率')
    capital_transaction_expect_finished_at = db.Column(db.DateTime, nullable=False, index=True, server_default=db.FetchedValue(), info='预计完成时间')
    capital_transaction_repayment_type = db.Column(db.Enum('acpi', 'averagecapital', 'rtlataio'), nullable=False, server_default=db.FetchedValue(), info='还款类型:acpi-等额本息;averagecapital-等额本金;rtlataio-到期一次性还本付息')
    capital_transaction_create_at = db.Column(db.DateTime, nullable=False, index=True, server_default=db.FetchedValue(), info='创建时间')
    capital_transaction_update_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='更新时间')
    capital_transaction_origin_amount = db.Column(db.BigInteger, nullable=False, server_default=db.FetchedValue(), info='原始金额')
    capital_transaction_user_repay_at = db.Column(db.DateTime, nullable=False, index=True, server_default=db.FetchedValue(), info='用户提前或正常还款未走资方通道而走我方通道的还款时间')
    capital_transaction_user_repay_channel = db.Column(db.String(50), nullable=False, server_default=db.FetchedValue(), info='代扣渠道 我方通道 qsq')
    capital_transaction_actual_finished_at = db.Column(db.DateTime, nullable=False, index=True, server_default=db.FetchedValue(), info='实际还资方时间')
    capital_transaction_operate_type = db.Column(db.Enum('grant', 'advance', 'normal', 'compensate', 'buyback'), nullable=False, server_default=db.FetchedValue(), info='grant-放款，advance-用户提前还款并且未回购，normal-用户到期日还款并且未回购，compensate-逾期由我方刚兑之后，buyback-回购')



class Card(db.Model, BaseToDict):
    __tablename__ = 'card'

    card_id = db.Column(db.BigInteger, primary_key=True)
    card_no = db.Column(db.String(20), nullable=False, index=True, info='业务主键，由系统自动生成')
    card_individual_no = db.Column(db.String(20), nullable=False, index=True, server_default=db.FetchedValue(), info='持有人业务主键号')
    card_acc_id_num = db.Column(db.String(32), index=True, info='账户身份证号码')
    card_acc_tel = db.Column(db.String(16), info='银行卡对应的电话号码')
    card_acc_num = db.Column(db.String(45), nullable=False, index=True, server_default=db.FetchedValue(), info='账户身份证号码')
    card_acc_name = db.Column(db.String(50))
    card_type = db.Column(db.String(255), server_default=db.FetchedValue(), info='账户类型：debit：借记卡；loan：贷记卡')
    card_category = db.Column(db.String(20), server_default=db.FetchedValue(), info='private->对私;public->对公')
    card_bank_name = db.Column(db.String(255), info='开户行')
    card_bank_branch_name = db.Column(db.String(255), info='支行名称')
    card_bank_code = db.Column(db.String(20), info='银行编码')
    card_individual_type = db.Column(db.String(255), server_default=db.FetchedValue(), info='持有人类型：individual：个人；enterprise：企业')
    card_status = db.Column(db.SmallInteger, nullable=False, server_default=db.FetchedValue(), info='1=>active,0=>inactive')
    card_create_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())
    card_update_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())
    card_acc_id_num_encrypt = db.Column(db.String(128), nullable=False, index=True, server_default=db.FetchedValue(), info='账户身份证号码 密文')
    card_acc_tel_encrypt = db.Column(db.String(128), nullable=False, server_default=db.FetchedValue(), info='银行卡对应的电话号码 密文')
    card_acc_num_encrypt = db.Column(db.String(128), nullable=False, unique=True, server_default=db.FetchedValue(), info='银行卡号 密文')
    card_acc_name_encrypt = db.Column(db.String(128), nullable=False, server_default=db.FetchedValue(), info='姓名 密文')



class CardAsset(db.Model, BaseToDict):
    __tablename__ = 'card_asset'
    __table_args__ = (
        db.Index('idx_card_asset_asset_item_no', 'card_asset_asset_item_no', 'card_asset_type', 'card_asset_status'),
    )

    card_asset_id = db.Column(db.BigInteger, primary_key=True)
    card_asset_type = db.Column(db.String(20), nullable=False, info='卡-资产类型：repay:还款卡，recieve:收款卡')
    card_asset_card_no = db.Column(db.String(20), nullable=False, index=True, info='卡编号 业务主键')
    card_asset_asset_no = db.Column(db.String(20), nullable=False, server_default=db.FetchedValue(), info='资产主建')
    card_asset_asset_item_no = db.Column(db.String(48), nullable=False, server_default=db.FetchedValue(), info='项目编号,关联asset')
    card_asset_status = db.Column(db.SmallInteger, nullable=False, info='1:有效,0:无效')
    card_asset_create_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='创建时间')
    card_asset_update_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='更新时间')



class CardBind(db.Model, BaseToDict):
    __tablename__ = 'card_bind'

    card_bind_id = db.Column(db.BigInteger, primary_key=True)
    card_bind_from_system = db.Column(db.String(10), nullable=False, info='绑卡发起系统')
    card_bind_card_num = db.Column(db.String(32), nullable=False, server_default=db.FetchedValue(), info='绑卡卡号')
    card_bind_serial_no = db.Column(db.String(50), nullable=False, index=True, server_default=db.FetchedValue(), info='绑卡序列号->对应代扣序列号')
    card_bind_channel = db.Column(db.String(32), nullable=False, server_default=db.FetchedValue(), info='绑卡通道')
    card_bind_status = db.Column(db.Enum('init', 'ready', 'process', 'success', 'fail'), nullable=False, server_default=db.FetchedValue(), info='绑定状态')
    card_bind_req_data = db.Column(db.Text)
    card_bind_res_data = db.Column(db.Text)
    card_bind_create_at = db.Column(db.DateTime, nullable=False, index=True, server_default=db.FetchedValue())
    card_bind_update_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())
    card_bind_comment = db.Column(db.String, info='绑卡备注')
    card_bind_card_num_encrypt = db.Column(db.String(32), nullable=False, index=True, server_default=db.FetchedValue(), info='绑卡卡号 密文字段')
    card_bind_protocol_no = db.Column(db.String(64), info='资方绑定成功的协议号')



class ComboOrder(db.Model, BaseToDict):
    __tablename__ = 'combo_order'

    combo_order_id = db.Column(db.Integer, primary_key=True, info='单表主键')
    combo_order_no = db.Column(db.String(48), nullable=False, unique=True, info='订单编号')
    combo_order_type = db.Column(db.String(48), nullable=False, info='订单类型')
    combo_order_ref_item_no = db.Column(db.String(48), nullable=False, index=True, info='资产编号')
    combo_order_from_system = db.Column(db.String(20), nullable=False, info='订单系统来源')
    combo_order_amount = db.Column(db.BigInteger, nullable=False, info='订单金额:分')
    combo_order_repaid_amount = db.Column(db.BigInteger, nullable=False, server_default=db.FetchedValue(), info='已还款金额:分')
    combo_order_finish_at = db.Column(db.DateTime, info='实际放款时间')
    combo_order_due_at = db.Column(db.DateTime, info='到期时间')
    combo_order_status = db.Column(db.Enum('sign', 'sale', 'repay', 'payoff', 'late', 'lateoff', 'void', 'writeoff'), nullable=False, server_default=db.FetchedValue(), info='状态：sign:签约中，sale，销售中  repay，还款中  payoff，已结清(正常结清)  late，坏账中  lateoff，已清算(坏账清算),void 作废,writeoff 注销')
    combo_order_create_at = db.Column(db.DateTime, nullable=False, index=True, server_default=db.FetchedValue(), info='创建时间')
    combo_order_update_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='更新时间')
    combo_order_cmdb_product_number = db.Column(db.String(50), nullable=False, info='费率系统产品编号')



class ComboOrderTran(db.Model, BaseToDict):
    __tablename__ = 'combo_order_tran'
    __table_args__ = (
        db.Index('idx_combo_order_tran_order_no', 'combo_order_tran_order_no', 'combo_order_tran_period', 'combo_order_tran_type'),
    )

    combo_order_tran_id = db.Column(db.Integer, primary_key=True, info='单表主键')
    combo_order_tran_period = db.Column(db.Integer, nullable=False, info='期次')
    combo_order_tran_order_no = db.Column(db.String(48), nullable=False, info='订单编号')
    combo_order_tran_amount = db.Column(db.BigInteger, nullable=False, info='订单金额:分')
    combo_order_tran_repaid_amount = db.Column(db.BigInteger, nullable=False, server_default=db.FetchedValue())
    combo_order_tran_status = db.Column(db.Enum('finish', 'nofinish'), nullable=False, info='状态')
    combo_order_tran_finish_at = db.Column(db.DateTime, info='还款完成日期')
    combo_order_tran_due_at = db.Column(db.DateTime, index=True, info='本期 到期时间')
    combo_order_tran_create_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='创建时间')
    combo_order_tran_update_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='更新时间')
    combo_order_tran_type = db.Column(db.String(32), nullable=False, server_default=db.FetchedValue(), info='第三单还款计划类型')
    combo_order_tran_decrease_amount = db.Column(db.BigInteger, nullable=False, server_default=db.FetchedValue(), info='减免金额：分')
    combo_order_tran_repay_priority = db.Column(db.SmallInteger, nullable=False, server_default=db.FetchedValue(), info='还款优先级')



class Coupon(db.Model, BaseToDict):
    __tablename__ = 'coupon'

    coupon_id = db.Column(db.BigInteger, primary_key=True, info='自增长ID')
    coupon_no = db.Column(db.String(64), nullable=False, unique=True, info='业务主键')
    coupon_num = db.Column(db.String(64), nullable=False, index=True, info='贷上钱优惠券编号')
    coupon_type = db.Column(db.String(32), nullable=False, server_default=db.FetchedValue(), info='代金券类型，cash->现金卷，interest->免息卷')
    coupon_amount = db.Column(db.BigInteger, nullable=False, info='优惠券金额')
    coupon_status = db.Column(db.Enum('ready', 'fail', 'success'), nullable=False, server_default=db.FetchedValue(), info='优惠券使用状态')
    coupon_withhold_result_serial_no = db.Column(db.String(64), nullable=False, index=True, server_default=db.FetchedValue(), info='代扣流水号')
    coupon_asset_item_no = db.Column(db.String(64), nullable=False, index=True, info='资产编号')
    coupon_asset_type = db.Column(db.String(64), nullable=False, info='资产类型')
    coupon_create_at = db.Column(db.DateTime, nullable=False, index=True, server_default=db.FetchedValue(), info='创建时间')
    coupon_update_at = db.Column(db.DateTime, nullable=False, index=True, server_default=db.FetchedValue(), info='更新时间')



class DistributedLock(db.Model, BaseToDict):
    __tablename__ = 'distributed_lock'

    distributed_lock_id = db.Column(db.BigInteger, primary_key=True, info='主键id自动增长')
    distributed_lock_key = db.Column(db.String(100), nullable=False, unique=True, info='唯一值，根据这个值来生成分布式锁的key')
    distributed_lock_create_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='锁创建时间')
    distributed_lock_owner = db.Column(db.String(50))



class FeeLog(db.Model, BaseToDict):
    __tablename__ = 'fee_log'

    fee_log_id = db.Column(db.BigInteger, primary_key=True)
    fee_log_asset_item_no = db.Column(db.String(48), nullable=False, index=True, server_default=db.FetchedValue(), info='所属资产id')
    fee_log_period = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue())
    fee_log_pay_type = db.Column(db.Enum('repay', 'pay'), nullable=False, info='日志类型：repay：已付, pay:需付(repay：充值时就已付，pay：刷新罚息时就是需付)')
    fee_log_amount = db.Column(db.BigInteger, nullable=False, server_default=db.FetchedValue(), info='操作金额')
    fee_log_finish_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='结束时间')
    fee_log_amount_type = db.Column(db.Enum('service', 'lateinterest', 'latemanage', 'manage', 'qscservice', 'lateservice', 'penalty', 'writeoff_penalty', 'delay', 'delay_interest'), nullable=False, server_default=db.FetchedValue(), info='费用类型： service：融资服务手续费；manage：融资管理手续费；lateinterest：罚息; latemanage：逾期管理费;qscservice：钱生财服务手续费;lateservice:逾期服务费; penalty:违约金; writeoff_penalty 注销违约金, delay 延期服务费, delay_interest 延期息费')
    fee_log_opt_type = db.Column(db.Enum('normal', 'machine', 'human'), nullable=False, server_default=db.FetchedValue(), info='操作标志位（normal：刷新罚息，machine：纠正罚息，human：费用减免）')
    fee_log_create_at = db.Column(db.DateTime, nullable=False, index=True, server_default=db.FetchedValue(), info='操作结束时间')
    fee_log_flag = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), info='逆操作标志位,0:未删除;1:删除')
    fee_log_system = db.Column(db.Enum('rbiz', 'cmdb', 'fox'), nullable=False, server_default=db.FetchedValue(), info='该费用变更来自哪个系统：rbiz-还款系统，cmdb-费率系统，fox-贷后系统')
    fee_log_item_type = db.Column(db.String(32), nullable=False, server_default=db.FetchedValue(), info='类型：asset-资产，combo_order-第三单')



class FixAssetFromSystem(db.Model, BaseToDict):
    __tablename__ = 'fix_asset_from_system'

    fix_id = db.Column(db.BigInteger, primary_key=True)
    item_no = db.Column(db.String(48), unique=True)
    from_system = db.Column(db.String(24))
    from_system_name = db.Column(db.String(24))
    repayment_app = db.Column(db.String(24))



class Individual(db.Model, BaseToDict):
    __tablename__ = 'individual'
    __table_args__ = (
        db.Index('idx_individual_idnum', 'individual_id_num', 'individual_name'),
    )

    individual_id = db.Column(db.Integer, primary_key=True)
    individual_no = db.Column(db.String(32), nullable=False, unique=True)
    individual_name = db.Column(db.String(32), nullable=False, index=True, server_default=db.FetchedValue(), info='姓名')
    individual_id_num = db.Column(db.String(32), nullable=False, server_default=db.FetchedValue(), info='身份证号码')
    individual_id_addr = db.Column(db.String(255), server_default=db.FetchedValue(), info='身份证地址')
    individual_id_type = db.Column(db.SmallInteger, server_default=db.FetchedValue(), info='身份类型(0-未知,1-在职,2-在读,3-待业)')
    individual_id_post_code = db.Column(db.String(8), server_default=db.FetchedValue(), info='身份证地址邮编')
    individual_gender = db.Column(db.String(10), server_default=db.FetchedValue(), info='性别')
    individual_education = db.Column(db.SmallInteger, server_default=db.FetchedValue(), info='学历(0-未知,1-博士研究生,2-硕士研究生,3-本科,4-大专,5-中专,6-技校,7-高中,8-初中,9-小学,10-文盲或半文盲)')
    individual_credit_type = db.Column(db.SmallInteger, server_default=db.FetchedValue(), info='信用类型(0-未知,1-芝麻分,2-万象分,3-考拉分,4-星辰分,5-京东分,\\n6-腾讯分)')
    individual_credit_score = db.Column(db.Integer, server_default=db.FetchedValue(), info='信用分数')
    individual_residence = db.Column(db.String(128), server_default=db.FetchedValue(), info='居住地')
    individual_residence_tel = db.Column(db.String(16), server_default=db.FetchedValue(), info='住宅电话')
    individual_residence_status = db.Column(db.SmallInteger, server_default=db.FetchedValue(), info='居住状况(0-未知,1-自置,2-按揭,3-亲属楼宇,4-集体宿舍,5-租房,6-共有住宅,7-其他)')
    individual_corp_name = db.Column(db.String(255), server_default=db.FetchedValue(), info='单位名称')
    individual_corp_tel = db.Column(db.String(16), server_default=db.FetchedValue(), info='单位电话')
    individual_corp_trade = db.Column(db.SmallInteger, server_default=db.FetchedValue(), info='单位所属行业(0-未知,1-政府机关/社会团体,2-军事/公检法,3-教育/科研,4-医院,5-公共事业/邮电通信/仓储运输物流,6-建筑业,7-传统制造业,8-互联网/其他高新技术行业,9-金融业,10-商业/贸易,11-餐饮/酒店/旅游,12-媒体/体育/娱乐,13-服务业,14-专业事务所,15-农林牧渔/自由职业/其他)')
    individual_duty = db.Column(db.SmallInteger, server_default=db.FetchedValue(), info='职务(0-未知,1-高级管理人员,2-中级管理人员,3-办公类员工,4-技术类员工,5-后勤类员工,6-操作类员工,7-服务类员工,8-销售类员工,9-其他类型员工)')
    individual_workplace = db.Column(db.String(128), server_default=db.FetchedValue(), info='工作地')
    individual_tel = db.Column(db.String(16), index=True, server_default=db.FetchedValue(), info='联系电话')
    individual_marriage = db.Column(db.SmallInteger, server_default=db.FetchedValue(), info='婚姻状况(0-未知,1-未婚,2-已婚,3-丧偶,4-离婚)')
    individual_mate_name = db.Column(db.String(32), server_default=db.FetchedValue(), info='配偶姓名')
    individual_mate_tel = db.Column(db.String(16), server_default=db.FetchedValue(), info='配偶联系方式')
    individual_relative_name = db.Column(db.String(32), server_default=db.FetchedValue(), info='亲属姓名')
    individual_relative_relation = db.Column(db.String(32), server_default=db.FetchedValue(), info='和借款人的亲属关系')
    individual_relative_tel = db.Column(db.String(16), server_default=db.FetchedValue(), info='亲属联系方式')
    individual_sec_relative_name = db.Column(db.String(32), info='第二联系人亲属姓名')
    individual_sec_relative_relation = db.Column(db.String(32), info='第二联系人和借款人的亲属关系')
    individual_sec_relative_tel = db.Column(db.String(16), info='第二联系人联系方式')
    individual_workmate_name = db.Column(db.String(32), server_default=db.FetchedValue(), info='同事姓名')
    individual_workmate_tel = db.Column(db.String(16), server_default=db.FetchedValue(), info='同事联系方式')
    individual_school_name = db.Column(db.String(128), server_default=db.FetchedValue(), info='学校名称')
    individual_school_place = db.Column(db.String(128), server_default=db.FetchedValue(), info='学校电话')
    individual_enrollment_time = db.Column(db.DateTime, server_default=db.FetchedValue(), info='入学时间')
    individual_audit_status = db.Column(db.SmallInteger, info="'nopass'=>0,'pass'=>1")
    individual_audit_time = db.Column(db.DateTime, info='审核时间')
    individual_account_name = db.Column(db.String(50), info='个人在财务系统中的名称')
    individual_auditor_name = db.Column(db.String(256), server_default=db.FetchedValue(), info='审核者用户名')
    individual_create_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())
    individual_update_name = db.Column(db.String(256), server_default=db.FetchedValue(), info='更新者用户名')
    individual_update_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())
    individual_name_encrypt = db.Column(db.String(128), nullable=False, index=True, server_default=db.FetchedValue(), info='姓名 密文')
    individual_id_num_encrypt = db.Column(db.String(128), nullable=False, unique=True, server_default=db.FetchedValue(), info='身份证号码 密文')
    individual_tel_encrypt = db.Column(db.String(128), nullable=False, index=True, server_default=db.FetchedValue(), info='联系电话 密文')



class IndividualAsset(db.Model, BaseToDict):
    __tablename__ = 'individual_asset'
    __table_args__ = (
        db.Index('idx_individual_asset_asset_item_no', 'individual_asset_asset_item_no', 'individual_asset_type'),
    )

    individual_asset_id = db.Column(db.BigInteger, primary_key=True)
    individual_asset_type = db.Column(db.String(20), nullable=False, info='个人类型：borrow：借款人；secure：担保人；mortgagee:抵押权人；subborrow：从借款人; repay:还款人')
    individual_asset_asset_no = db.Column(db.String(20), nullable=False, server_default=db.FetchedValue(), info='资产主建')
    individual_asset_asset_item_no = db.Column(db.String(48), nullable=False, server_default=db.FetchedValue(), info='项目编号,关联asset')
    individual_asset_individual_no = db.Column(db.String(20), nullable=False, index=True)
    individual_asset_create_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())
    individual_asset_update_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())



class NacosConfig(db.Model, BaseToDict):
    __tablename__ = 'nacos_config'

    nacos_config_id = db.Column(db.Integer, primary_key=True)
    nacos_config_desc = db.Column(db.String(100), nullable=False)
    nacos_config_key = db.Column(db.String(20), nullable=False)
    nacos_config_name = db.Column(db.String(20), nullable=False)
    nacos_config_program = db.Column(db.String(20), nullable=False)
    nacos_config_value = db.Column(db.String(500), nullable=False)
    nacos_config_order = db.Column(db.Integer)
    nacos_config_is_collect = db.Column(db.Integer)
    nacos_config_is_active = db.Column(db.Integer)
    nacos_config_timeout = db.Column(db.Integer, nullable=False)
    nacos_config_creater = db.Column(db.String(8), nullable=False)
    nacos_config_updater = db.Column(db.String(8), nullable=False)
    nacos_config_create_at = db.Column(db.DateTime, nullable=False)
    nacos_config_update_at = db.Column(db.DateTime, nullable=False)



class Provision(db.Model, BaseToDict):
    __tablename__ = 'provision'
    __table_args__ = (
        db.Index('uniq_idx_provision', 'provision_item_no', 'provision_tran_period', 'provision_tran_type', 'provision_recharge_serial_no'),
    )

    provision_id = db.Column(db.BigInteger, primary_key=True, info='拨备垫资主键')
    provision_type = db.Column(db.Enum('arbitration', 'asset_void', 'asset_reverse', 'clear_error', 'manual_decrease', 'capital_decrease'), nullable=False, info='拨备垫资类型，arbitration=>仲裁;asset_void=>资产作废;asset_reverse=>资产冲正;clear_error=>清分错误;manual_decrease=>手动减免;capital_decrease=>资方要求减免')
    provision_recharge_serial_no = db.Column(db.String(64), nullable=False, index=True, server_default=db.FetchedValue(), info='拨备垫资充值序列号')
    provision_item_type = db.Column(db.Enum('asset', 'combo_order'), nullable=False, info='拨备垫资项目类型：assset=>资产，combo_order=>第三单')
    provision_item_no = db.Column(db.String(64), nullable=False, server_default=db.FetchedValue(), info='拨备垫资项目编号')
    provision_tran_type = db.Column(db.String(20), nullable=False, info='交易类型')
    provision_tran_no = db.Column(db.String(64), nullable=False, server_default=db.FetchedValue(), info='还款计划编号')
    provision_tran_period = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), info='期次')
    provision_amount = db.Column(db.BigInteger, nullable=False, server_default=db.FetchedValue(), info='拨备垫资金额')
    provision_date = db.Column(db.Date, nullable=False, info='拨备垫资日期')
    provision_status = db.Column(db.Enum('open', 'process', 'close'), nullable=False, server_default=db.FetchedValue(), info='拨备金垫资状态')
    provision_create_at = db.Column(db.DateTime, nullable=False, index=True, server_default=db.FetchedValue(), info='创建时间')
    provision_update_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='更新时间')



class RefundDetail(db.Model, BaseToDict):
    __tablename__ = 'refund_detail'

    refund_detail_id = db.Column(db.BigInteger, primary_key=True)
    refund_detail_serial_no = db.Column(db.String(32), nullable=False, index=True)
    refund_detail_operate_type = db.Column(db.Enum('repay', 'decrease', 'inverse', 'provision_recharge', 'provision_repay'), nullable=False, server_default=db.FetchedValue())
    refund_detail_withhold_serial_no = db.Column(db.String(50), nullable=False, info='代扣序列号')
    refund_detail_withhold_channel_key = db.Column(db.String(50), nullable=False, info='代扣channel_key')
    refund_detail_item_no = db.Column(db.String(64), nullable=False, index=True)
    refund_detail_tran_no = db.Column(db.String(32), nullable=False)
    refund_detail_amount = db.Column(db.BigInteger, nullable=False)
    refund_detail_create_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())
    refund_detail_update_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())



class RefundRequest(db.Model, BaseToDict):
    __tablename__ = 'refund_request'

    refund_request_id = db.Column(db.BigInteger, primary_key=True, info='退款请求ID，自增长主键')
    refund_request_serial_no = db.Column(db.String(32), nullable=False, unique=True, info='退款序列号，唯一')
    refund_request_withhold_serial_no = db.Column(db.String(64), nullable=False, unique=True, info='退款请求代扣序列号')
    refund_request_withhold_channel_key = db.Column(db.String(64), nullable=False, info='代扣第三方序列号')
    refund_request_from_system = db.Column(db.String(255), nullable=False, info='请求系统')
    refund_request_req_key = db.Column(db.String(64), nullable=False, unique=True, info='退款请求key')
    refund_request_status = db.Column(db.Enum('ready', 'refunding', 'refund_fail', 'withdrawing', 'withdraw_fail', 'refund_success', 'withdraw_success'), nullable=False, server_default=db.FetchedValue(), info='退款请求状态：ready：数据初始状态;refunding：走退款接口处理中;refund_fail：退款接口处理失败，非最终失败; withdrawing：代付处理中;withdraw_fail：代付失败，最终失败，如果是该状态，会通知企业微信及邮件进行人工处理;refund_success：退款成功;withdraw_success：代付成功;refund_success/withdraw_success都是终态')
    refund_request_trade_type = db.Column(db.Enum('ONLINE', 'OFFLINE'), nullable=False, server_default=db.FetchedValue(), info='退款交易方式：online:线上 OFFLINE:线下')
    refund_request_scene = db.Column(db.Enum('repeated_withhold', 'force_refund', 'trade_refund'), nullable=False, server_default=db.FetchedValue(), info='退款场景：repeated_withhold:重复代扣退款 force_refund:强制退款 trade_refund:订单退款')
    refund_request_amount = db.Column(db.BigInteger, nullable=False, info='退款请求金额')
    refund_request_withhold_amount = db.Column(db.BigInteger, nullable=False, info='退款的代扣订单金额')
    refund_request_user_id_num = db.Column(db.String(64), nullable=False, index=True, info='退款用户名')
    refund_request_user_name = db.Column(db.String(64), nullable=False, info='退款人员名称')
    refund_request_card_num = db.Column(db.String(64), nullable=False, info='退款卡号')
    refund_request_user_phone = db.Column(db.String(64), nullable=False, index=True, info='退款用户手机号')
    refund_request_finish_at = db.Column(db.DateTime, nullable=False, index=True, server_default=db.FetchedValue(), info='退款完成时间')
    refund_request_comment = db.Column(db.String(128), nullable=False, server_default=db.FetchedValue(), info='备注')
    refund_request_callback = db.Column(db.String(256), nullable=False, server_default=db.FetchedValue(), info='退款完成后回调')
    refund_request_operator = db.Column(db.String(50), nullable=False, server_default=db.FetchedValue())
    refund_request_create_at = db.Column(db.DateTime, nullable=False, index=True, server_default=db.FetchedValue())
    refund_request_update_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())



class RefundResult(db.Model, BaseToDict):
    __tablename__ = 'refund_result'

    refund_result_id = db.Column(db.BigInteger, primary_key=True, info='退款自增长ID')
    refund_result_no = db.Column(db.String(20), nullable=False, info='refund_result业务主键')
    refund_result_trade_no = db.Column(db.String(50), nullable=False, index=True, info='订单号')
    refund_result_amount = db.Column(db.BigInteger, nullable=False, info='退款总金额')
    refund_result_status = db.Column(db.Enum('ready', 'success', 'fail', 'process', 'cancel'), nullable=False, index=True, info='退款状态')
    refund_result_serial_no = db.Column(db.String(50), nullable=False, unique=True, info='执行退款流水号')
    refund_result_withhold_result_serial_no = db.Column(db.String(50), nullable=False, index=True, info='执行代扣流水号')
    refund_result_comment = db.Column(db.Text, info='退款备注')
    refund_result_run_times = db.Column(db.SmallInteger, nullable=False, info='代扣执行次数')
    refund_result_channel = db.Column(db.String(32), info='退款通道')
    refund_result_channel_key = db.Column(db.String(50), info='退款通道返回的key')
    refund_result_channel_code = db.Column(db.String(32), info='退款通道返回的code')
    refund_result_error_code = db.Column(db.String(32), info='退款由paysvr返回的error_code,如果是其他通道的，需要与paysvr对应')
    refund_result_custom_code = db.Column(db.String(32), info='退款->自定义编码')
    refund_result_req_data = db.Column(db.Text, info='退款请求数据')
    refund_result_res_data = db.Column(db.Text, info='退款返回数据')
    refund_result_create_at = db.Column(db.DateTime, nullable=False, index=True, server_default=db.FetchedValue(), info='创建时间')
    refund_result_execute_at = db.Column(db.DateTime, nullable=False, info='退款执行时间')
    refund_result_update_at = db.Column(db.DateTime, nullable=False, index=True, server_default=db.FetchedValue(), info='退款更新时间')
    refund_result_finish_at = db.Column(db.DateTime, nullable=False, index=True, server_default=db.FetchedValue(), info='退款完成时间，在退款完成时写入')
    refund_result_creator = db.Column(db.String(50), nullable=False, server_default=db.FetchedValue(), info='创建者，如果没有则是"系统"')
    refund_result_operator = db.Column(db.String(50), nullable=False, server_default=db.FetchedValue(), info='操作者，如果没有则是"系统"')



class Seed(db.Model, BaseToDict):
    __tablename__ = 'seed'

    seed_type = db.Column(db.String(45), primary_key=True)
    seed_no = db.Column(db.Integer, nullable=False)
    seed_update_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())



class SendMsg(db.Model, BaseToDict):
    __tablename__ = 'sendmsg'
    __table_args__ = (
        db.Index('idx_sendmsg_priority_type', 'sendmsg_priority', 'sendmsg_type'),
        db.Index('idx_sendmsg_nextRun_status_priority', 'sendmsg_status', 'sendmsg_priority', 'sendmsg_next_run_at')
    )

    sendmsg_id = db.Column(db.BigInteger, primary_key=True)
    sendmsg_order_no = db.Column(db.String(64), nullable=False, index=True, server_default=db.FetchedValue(), info='消息业务编号')
    sendmsg_type = db.Column(db.String(45), nullable=False, info='消息具体类型')
    sendmsg_content = db.Column(db.String, nullable=False, info='消息内容')
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



class SmsTemplate(db.Model, BaseToDict):
    __tablename__ = 'sms_template'
    __table_args__ = (
        db.Index('sms_template_idx', 'sms_template_type', 'sms_template_key'),
    )

    sms_template_id = db.Column(db.Integer, primary_key=True)
    sms_template_type = db.Column(db.String(50), nullable=False, info='模板类型信息，比如：support_params,短信模板支持的参数，content_template,短信内容模板')
    sms_template_key = db.Column(db.String(50), info='模板键值，对于内容模板键值：资产类型，对于支持模板键值为空。')
    sms_template_content = db.Column(db.Text, info='配置信息，Json格式存储')
    sms_template_status = db.Column(db.Enum('active', 'inactive'), nullable=False, info='短信模板状态：active－可用，inactive－不可用')
    sms_template_create_at = db.Column(db.DateTime, nullable=False, info='创建时间')
    sms_template_create_userid = db.Column(db.Integer, nullable=False, info='创建用户名')
    sms_template_update_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())
    sms_template_update_userid = db.Column(db.Integer, nullable=False, info='修改用户名')



class SplitOrderConfig(db.Model, BaseToDict):
    __tablename__ = 'split_order_config'

    split_order_config_id = db.Column(db.Integer, primary_key=True, info='主键')
    split_order_config_capital_code = db.Column(db.String(32), nullable=False, unique=True, info='资金方code')
    split_order_config_type = db.Column(db.String(64), nullable=False, info='拆单类型')
    split_order_config_creator = db.Column(db.String(32), nullable=False, server_default=db.FetchedValue(), info='创建人')
    split_order_config_updator = db.Column(db.String(32), server_default=db.FetchedValue(), info='更新人')
    split_order_config_create_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='创建时间')
    split_order_config_update_at = db.Column(db.DateTime, server_default=db.FetchedValue(), info='更新时间')



class SplitOrderRule(db.Model, BaseToDict):
    __tablename__ = 'split_order_rule'

    split_order_rule_id = db.Column(db.Integer, primary_key=True, info='主键')
    split_order_rule_config_id = db.Column(db.Integer, nullable=False, info='拆单配置id，外键')
    split_order_rule_priority = db.Column(db.Integer, info='拆单顺序')
    split_order_rule_can_combo = db.Column(db.Enum('Y', 'N'), nullable=False, server_default=db.FetchedValue(), info='是否能够合并支付')
    split_order_rule_use_paysvr_channel = db.Column(db.String(1), nullable=False, server_default=db.FetchedValue(), info='是否使用paysvr代扣')
    split_order_rule_sign_company = db.Column(db.String(32), info='签约主体')
    split_order_rule_can_partly = db.Column(db.Enum('Y', 'N'), nullable=False, server_default=db.FetchedValue(), info='是否能够部分还款')
    split_order_rule_overdue = db.Column(db.Enum('Y', 'N'), nullable=False, server_default=db.FetchedValue(), info='逾期')
    split_order_rule_create_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='创建时间')
    split_order_rule_update = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='更新时间')
    split_order_rule_period_type = db.Column(db.String(32), nullable=False, server_default=db.FetchedValue(), info='期次类型')
    split_order_rule_same_company_combo = db.Column(db.String(1), nullable=False, server_default=db.FetchedValue(), info='同一个签约主体是否能合并')
    split_order_rule_same_channel_combo = db.Column(db.String(1), nullable=False, server_default=db.FetchedValue(), info='同一个代扣通道是否能合并')



class SplitOrderRuleCondition(db.Model, BaseToDict):
    __tablename__ = 'split_order_rule_condition'

    split_order_rule_condition_id = db.Column(db.Integer, primary_key=True)
    split_order_rule_condition_rule_id = db.Column(db.Integer, nullable=False, info='规则id，外键')
    split_order_rule_condition_type = db.Column(db.String(64), nullable=False, info='条件类型,如果同一类型的有多个取值，则配置多条')
    split_order_rule_condition_value = db.Column(db.String(256), info='条件取值')
    split_order_rule_condition_create_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='创建时间')
    split_order_rule_condition_update_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='更新时间')



class SplitOrderRuleExpres(db.Model, BaseToDict):
    __tablename__ = 'split_order_rule_express'

    split_order_rule_express_id = db.Column(db.Integer, primary_key=True, info='主键')
    split_order_rule_express_rule_id = db.Column(db.Integer, nullable=False, info='规则id，外键')
    split_order_rule_express_type = db.Column(db.String(64), nullable=False, info='表达式类型')
    split_order_rule_express_value = db.Column(db.String(256), nullable=False, info='表达式取值')
    split_order_rule_express_create_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='创建时间')
    split_order_rule_express_update_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='更新时间')
    split_order_rule_express_percent = db.Column(db.String(12), server_default=db.FetchedValue(), info='拆分百分比')



class Synctask(db.Model, BaseToDict):
    __tablename__ = 'synctask'
    __table_args__ = (
        db.Index('idx_synctask_create_at_type_status', 'synctask_create_at', 'synctask_type', 'synctask_status'),
        db.Index('idx_synctask_key_type_fromsystem', 'synctask_key', 'synctask_type', 'synctask_from_system')
    )

    synctask_id = db.Column(db.BigInteger, primary_key=True, info='同步任务ID')
    synctask_type = db.Column(db.String(50), nullable=False, info='任务类型')
    synctask_key = db.Column(db.String(50), nullable=False, info='任务键值')
    synctask_from_system = db.Column(db.String(50), nullable=False, info='任务来源系统')
    synctask_memo = db.Column(db.Text, info='任务执行中出现异常时,纪录异常日志')
    synctask_status = db.Column(db.Enum('open', 'running', 'terminated', 'close', 'error'), nullable=False, server_default=db.FetchedValue(), info='任务状态，初始状态Open， 执行中为runing, 错误为error，执行完成为close,错误次数达上限为terminated')
    synctask_create_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())
    synctask_update_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())
    synctask_request_data = db.Column(db.String, info='任务数据，Json格式')
    synctask_response_data = db.Column(db.Text, info='任务执行完车后，返回结果数据，Json格式')
    synctask_order_no = db.Column(db.String(64), nullable=False, index=True, server_default=db.FetchedValue(), info='业务主键')
    synctask_last_run_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='最后执行时间')
    synctask_retrytimes = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue())



class Task(db.Model, BaseToDict):
    __tablename__ = 'task'
    __table_args__ = (
        db.Index('idx_task_status_priority_next_run_at', 'task_status', 'task_priority', 'task_next_run_at'),
    )

    task_id = db.Column(db.BigInteger, primary_key=True)
    task_type = db.Column(db.String(45), nullable=False, info='任务类型')
    task_memo = db.Column(db.Text, info='任务备注')
    task_status = db.Column(db.Enum('open', 'running', 'error', 'terminated', 'close'), nullable=False, info='任务状态')
    task_version = db.Column(db.SmallInteger, nullable=False, server_default=db.FetchedValue(), info='版本号')
    task_priority = db.Column(db.SmallInteger, nullable=False, server_default=db.FetchedValue(), info='任务优先级')
    task_next_run_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='下次运行时间')
    task_create_at = db.Column(db.DateTime, nullable=False, index=True, server_default=db.FetchedValue(), info='创建时间')
    task_update_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='更新时间')
    task_order_no = db.Column(db.String(64), nullable=False, index=True, server_default=db.FetchedValue())
    task_request_data = db.Column(db.String, info='任务请求数据')
    task_response_data = db.Column(db.Text, info='任务返回数据')
    task_retrytimes = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue())



class TmpDataFix(db.Model, BaseToDict):
    __tablename__ = 'tmp_data_fix'

    tmp_data_fix_id = db.Column(db.BigInteger, primary_key=True, info='主键ID')
    tmp_data_fix_item_no = db.Column(db.String(120), nullable=False, index=True, info='数据修复资产编号')
    tmp_data_fix_tran_no = db.Column(db.String(120), nullable=False, unique=True, info='数据修复还款计划编号')
    tmp_data_fix_tran_type = db.Column(db.String(50), nullable=False, info='还款计划类型')
    tmp_data_fix_tran_period = db.Column(db.Integer, nullable=False, info='还款期次')
    tmp_data_fix_decreace_amt_opening = db.Column(db.BigInteger, nullable=False, server_default=db.FetchedValue(), info='减免金额期初值')
    tmp_data_fix_decrease_amt_fix = db.Column(db.BigInteger, nullable=False, server_default=db.FetchedValue(), info='减免金额需要修复的值')
    tmp_data_fix_decrease_amt_closing = db.Column(db.BigInteger, nullable=False, server_default=db.FetchedValue(), info='减免金额期末值')
    tmp_data_fix_amt_opening = db.Column(db.BigInteger, nullable=False, server_default=db.FetchedValue(), info='应还期初值')
    tmp_data_fix_amt_fix = db.Column(db.BigInteger, nullable=False, server_default=db.FetchedValue(), info='期末修复值')
    tmp_data_fix_amt_closing = db.Column(db.BigInteger, nullable=False, server_default=db.FetchedValue(), info='应还期末值')
    tmp_data_fix_over_charge = db.Column(db.BigInteger, nullable=False, server_default=db.FetchedValue(), info='多还金额')
    tmp_data_fix_status = db.Column(db.Enum('ready', 'process', 'success', 'fail', 'cancel'), nullable=False, server_default=db.FetchedValue(), info='状态')
    tmp_data_fix_comment = db.Column(db.String(250), nullable=False, server_default=db.FetchedValue(), info='修复备注')
    tmp_data_fix_create_at = db.Column(db.DateTime, nullable=False, index=True, server_default=db.FetchedValue(), info='创建时间')
    tmp_data_fix_update_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='修改时间')



class TmpSylCard(db.Model, BaseToDict):
    __tablename__ = 'tmp_syl_card'

    id = db.Column(db.Integer, primary_key=True)
    card_num = db.Column(db.String(24), nullable=False, index=True, server_default=db.FetchedValue())
    bind_at = db.Column(db.DateTime)



class Trade(db.Model, BaseToDict):
    __tablename__ = 'trade'
    __table_args__ = (
        db.Index('idx_unique_trade_ref_no_owner_type', 'trade_ref_no', 'trade_owner', 'trade_type'),
    )

    trade_id = db.Column(db.Integer, primary_key=True)
    trade_no = db.Column(db.String(50), nullable=False, unique=True, server_default=db.FetchedValue(), info='订单号，则有系统自动生成')
    trade_status = db.Column(db.Enum('open', 'payoff', 'refund', 'void'), nullable=False, server_default=db.FetchedValue(), info='订单状态：未付款:open，完成支付：payoff，退款：refund，作废：void')
    trade_type = db.Column(db.String(50), nullable=False, server_default=db.FetchedValue())
    trade_ref_no = db.Column(db.String(50), nullable=False, server_default=db.FetchedValue(), info='原始单据编号')
    trade_ref_type = db.Column(db.String(50), nullable=False, server_default=db.FetchedValue(), info='原始单据类型 资产:asset;游戏：game')
    trade_owner = db.Column(db.String(50), nullable=False, server_default=db.FetchedValue(), info='交易收款方：商城：store;游戏：game')
    trade_from_system = db.Column(db.String(20), nullable=False, info='订单系统来源;dsq,cash')
    trade_amount = db.Column(db.BigInteger, nullable=False, server_default=db.FetchedValue(), info='订单总金额（分）')
    trade_pay_amount = db.Column(db.BigInteger, nullable=False, server_default=db.FetchedValue(), info='实际支付金额（分）')
    trade_pay_at = db.Column(db.DateTime, server_default=db.FetchedValue(), info='支付完成时间')
    trade_refund_amount = db.Column(db.BigInteger, nullable=False, server_default=db.FetchedValue(), info='退款金额（分）')
    trade_refund_at = db.Column(db.DateTime, server_default=db.FetchedValue(), info='退款完成时间')
    trade_extend = db.Column(db.Text, info='订单扩展信息，以key-value形式的json字符串存储')
    trade_comment = db.Column(db.String(250), server_default=db.FetchedValue(), info='订单备注')
    trade_create_at = db.Column(db.DateTime, nullable=False, index=True, server_default=db.FetchedValue(), info='订单创建时间')
    trade_update_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='订单更新时间')



class TradeProduct(db.Model, BaseToDict):
    __tablename__ = 'trade_product'
    __table_args__ = (
        db.Index('idx_trade_product_trade_no', 'trade_product_trade_no', 'trade_product_no'),
    )

    trade_product_id = db.Column(db.BigInteger, primary_key=True)
    trade_product_trade_no = db.Column(db.String(50), nullable=False, info='订单编号')
    trade_product_no = db.Column(db.String(64), nullable=False, server_default=db.FetchedValue(), info='商品编码')
    trade_product_name = db.Column(db.String(64), nullable=False, server_default=db.FetchedValue(), info='商品名称')
    trade_product_category = db.Column(db.String(32), nullable=False, server_default=db.FetchedValue(), info='商品分类：卷')
    trade_product_vendor_no = db.Column(db.String(32), nullable=False, server_default=db.FetchedValue(), info='供应商编码')
    trade_product_vendor_name = db.Column(db.String(100), nullable=False, server_default=db.FetchedValue(), info='供应商名称')
    trade_product_po_cost = db.Column(db.BigInteger, nullable=False, server_default=db.FetchedValue(), info='商品成本')
    trade_product_count = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), info='商品数量')
    trade_product_create_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())
    trade_product_update_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())



class TradeTran(db.Model, BaseToDict):
    __tablename__ = 'trade_tran'
    __table_args__ = (
        db.Index('idx_trade_tran_trade_no_type_status', 'trade_tran_trade_no', 'trade_tran_type', 'trade_tran_status'),
    )

    trade_tran_id = db.Column(db.Integer, primary_key=True)
    trade_tran_trade_no = db.Column(db.String(50))
    trade_tran_serial_no = db.Column(db.String(60), nullable=False, unique=True, server_default=db.FetchedValue(), info='代扣，代付订单号')
    trade_tran_req_key = db.Column(db.String(60), nullable=False, index=True, server_default=db.FetchedValue(), info='请求key')
    trade_tran_ref_type = db.Column(db.String(50), nullable=False, index=True, server_default=db.FetchedValue(), info='trade_tran_ref_no 关联的类型 withhold,withholdreturn,withdraw')
    trade_tran_type = db.Column(db.Enum('pay', 'refund'), nullable=False, server_default=db.FetchedValue(), info='pay:支付,refund:退款')
    trade_tran_status = db.Column(db.Enum('open', 'success', 'fail'), nullable=False, server_default=db.FetchedValue(), info='支付状态:open:未支付，success：已支付；fail 交易失败')
    trade_tran_comment = db.Column(db.String(250), server_default=db.FetchedValue(), info='备注，代扣返回消息')
    trade_tran_amount = db.Column(db.BigInteger, nullable=False, server_default=db.FetchedValue(), info='交易金额')
    trade_tran_create_at = db.Column(db.DateTime, nullable=False, index=True, server_default=db.FetchedValue(), info='订单创建时间')
    trade_tran_update_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='订单更新时间')
    trade_tran_callback = db.Column(db.String(500), info='补单回调地址')



class TransactionFlowDistribute(db.Model, BaseToDict):
    __tablename__ = 'transaction_flow_distribute'

    transaction_flow_distribute_id = db.Column(db.Integer, primary_key=True, info='主键')
    transaction_flow_distribute_record_no = db.Column(db.String(64), nullable=False, index=True, info='流水号')
    transaction_flow_distribute_withhold_serial_no = db.Column(db.String(64), nullable=False, info='代扣流水号')
    transaction_flow_distribute_recharge_serial_no = db.Column(db.String(64), nullable=False, index=True, info='充值序列号')
    transaction_flow_distribute_recharge_amount = db.Column(db.Integer, nullable=False, info='充值金额')



class TransactionFlowRecord(db.Model, BaseToDict):
    __tablename__ = 'transaction_flow_record'

    transaction_flow_record_id = db.Column(db.Integer, primary_key=True, info='主键')
    transaction_flow_record_no = db.Column(db.String(64), nullable=False, unique=True, info='上传的自定义流水编号')
    transaction_flow_record_download_url = db.Column(db.String(256), nullable=False, info='流水的url地址')
    transaction_flow_record_amount = db.Column(db.Integer, nullable=False, info='金额')
    transaction_flow_record_repaid_amount = db.Column(db.Integer, info='已还的金额')
    transaction_flow_record_create_at = db.Column(db.DateTime, nullable=False, index=True, server_default=db.FetchedValue(), info='创建时间')
    transaction_flow_record_update_at = db.Column(db.DateTime, server_default=db.FetchedValue(), info='更新时间')



class Withdraw(db.Model, BaseToDict):
    __tablename__ = 'withdraw'

    withdraw_id = db.Column(db.BigInteger, primary_key=True, info='代付ID，自增长主键')
    withdraw_ref_no = db.Column(db.String(50), nullable=False, unique=True, server_default=db.FetchedValue(), info='代付关联订单号(一般情况下是退款订单号)')
    withdraw_serial_no = db.Column(db.String(50), nullable=False, unique=True, server_default=db.FetchedValue(), info='代付请求序列号')
    withdraw_amount = db.Column(db.BigInteger, nullable=False, info='代付金额')
    withdraw_channel = db.Column(db.String(32), nullable=False, server_default=db.FetchedValue(), info='代付通道')
    withdraw_channel_code = db.Column(db.String(20), nullable=False, server_default=db.FetchedValue(), info='通道code')
    withdraw_channel_key = db.Column(db.String(50), nullable=False, index=True, server_default=db.FetchedValue(), info='代付通道序列号')
    withdraw_account = db.Column(db.String(32), nullable=False, server_default=db.FetchedValue(), info='代付账户')
    withdraw_sign_company = db.Column(db.String(20), nullable=False, server_default=db.FetchedValue(), info='代付签约主体')
    withdraw_reason = db.Column(db.String(128), nullable=False, server_default=db.FetchedValue(), info='代付原因')
    withdraw_receiver_type = db.Column(db.Enum('private', 'public'), nullable=False, server_default=db.FetchedValue(), info='private:对私，public:对公')
    withdraw_receiver_name = db.Column(db.String(128), nullable=False, server_default=db.FetchedValue(), info='收款账户名称—密文')
    withdraw_receiver_account = db.Column(db.String(32), nullable=False, server_default=db.FetchedValue(), info='收款账户—密文')
    withdraw_receiver_identity = db.Column(db.String(32), nullable=False, index=True, server_default=db.FetchedValue(), info='收款人证件号(对私 - 身份证, 对公 - 组织机构代码证/企业信用代码)')
    withdraw_receiver_phone = db.Column(db.String(32), nullable=False, index=True, info='收款人手机号')
    withdraw_receiver_bank_code = db.Column(db.String(20), nullable=False, server_default=db.FetchedValue(), info='收款用户银行编号')
    withdraw_status = db.Column(db.Enum('ready', 'process', 'success', 'fail'), nullable=False, server_default=db.FetchedValue(), info='代付状态')
    withdraw_finish_at = db.Column(db.DateTime, nullable=False, index=True, server_default=db.FetchedValue(), info='代付完成时间')
    withdraw_comment = db.Column(db.String(128), nullable=False, server_default=db.FetchedValue(), info='代付comment')
    withdraw_create_at = db.Column(db.DateTime, nullable=False, index=True, server_default=db.FetchedValue())
    withdraw_update_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())



class Withhold(db.Model, BaseToDict):
    __tablename__ = 'withhold'

    withhold_id = db.Column(db.Integer, primary_key=True, info='主键')
    withhold_serial_no = db.Column(db.String(32), nullable=False, unique=True, info='代扣流水号，业务主键')
    withhold_request_no = db.Column(db.String(32), nullable=False, index=True, info='代扣请求编号')
    withhold_amount = db.Column(db.Integer, nullable=False, info='代扣金额（单位:分）')
    withhold_channel = db.Column(db.String(50), info='代扣渠道，根据不同的放款渠道进行路由')
    withhold_status = db.Column(db.Enum('ready', 'process', 'success', 'fail', 'cancel'), nullable=False, info='状态')
    withhold_sub_status = db.Column(db.Enum('normal', 'payment_cancel', 'agreement'), nullable=False, server_default=db.FetchedValue(), info='子状态,normal:正常,payment_cancel:协议支付取消,agreement:协议支付')
    withhold_channel_code = db.Column(db.String(32), info='代扣渠道返回的code')
    withhold_channel_message = db.Column(db.String(255), info='代扣渠道返回的消息描述')
    withhold_channel_key = db.Column(db.String(64), index=True)
    withhold_channel_fee = db.Column(db.Integer, info='代扣渠道费用（单位:分）')
    withhold_comment = db.Column(db.String(255), info='备注')
    withhold_error_code = db.Column(db.String(32), info='根据代扣渠道返回的状态自定义的code')
    withhold_custom_code = db.Column(db.String(32), info='自定义code')
    withhold_supplement = db.Column(db.Enum('Y', 'N'), nullable=False, server_default=db.FetchedValue(), info='是否为补单 Y N ')
    withhold_order = db.Column(db.Integer, info='代扣顺序')
    withhold_third_serial_no = db.Column(db.String(64), info='代扣通道返回的流水号')
    withhold_extend_info = db.Column(db.Text, info='针对一些特殊处理保存数据')
    withhold_create_at = db.Column(db.DateTime, nullable=False, index=True, server_default=db.FetchedValue(), info='创建时间')
    withhold_update_at = db.Column(db.DateTime, nullable=False, index=True, server_default=db.FetchedValue(), info='更新时间')
    withhold_execute_at = db.Column(db.DateTime, server_default=db.FetchedValue(), info='执行时间')
    withhold_finish_at = db.Column(db.DateTime, index=True, server_default=db.FetchedValue(), info='代扣完成时间')
    withhold_version = db.Column(db.Integer, info='版本号')
    withhold_req_key = db.Column(db.String(64), nullable=False, index=True, info='代扣请求key')
    withhold_user_name = db.Column(db.String(32), nullable=False, info='姓名')
    withhold_user_idnum = db.Column(db.String(32), nullable=False, index=True, info='身份证号')
    withhold_user_phone = db.Column(db.String(32), nullable=False, info='手机号')
    withhold_card_num = db.Column(db.String(32), nullable=False, index=True, info='用户卡号')
    withhold_capital_receive_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='资方接收时间')
    withhold_call_back = db.Column(db.String(500), info='回调地址')



class WithholdAssetDetailLock(db.Model, BaseToDict):
    __tablename__ = 'withhold_asset_detail_lock'
    __table_args__ = (
        db.Index('uidx_asset_item_no_serial_no', 'withhold_asset_detail_lock_asset_item_no', 'withhold_asset_detail_lock_serial_no'),
    )

    withhold_asset_detail_lock_id = db.Column(db.Integer, primary_key=True, info='主键')
    withhold_asset_detail_lock_asset_item_no = db.Column(db.String(50), nullable=False, info='资产编号')
    withhold_asset_detail_lock_serial_no = db.Column(db.String(50), nullable=False, info='代扣序列号')



class WithholdAutoLog(db.Model, BaseToDict):
    __tablename__ = 'withhold_auto_log'

    withhold_auto_log_id = db.Column(db.Integer, primary_key=True, info='主键')
    withhold_auto_log_asset_item_no = db.Column(db.String(64), nullable=False, index=True, info='资产编号')
    withhold_auto_log_asset_type = db.Column(db.String(60), nullable=False, info='资产类型')
    withhold_auto_log_asset_repay_period = db.Column(db.Integer, nullable=False, info='还款期数')
    withhold_auto_log_overdue_days = db.Column(db.Integer, nullable=False, info='逾期天数')
    withhold_auto_log_run_at = db.Column(db.DateTime, nullable=False, info='预计运行时间')
    withhold_auto_log_create_at = db.Column(db.DateTime, nullable=False, index=True, server_default=db.FetchedValue(), info='创建时间')
    withhold_auto_log_update_at = db.Column(db.DateTime, nullable=False, index=True, server_default=db.FetchedValue(), info='更新时间')
    withhold_auto_log_percent = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), info='自动代扣金额百分比')



class WithholdCard(db.Model, BaseToDict):
    __tablename__ = 'withhold_card'
    __table_args__ = (
        db.Index('idx_withhold_card_individual', 'withhold_card_individual_no', 'withhold_card_priority'),
    )

    withhold_card_id = db.Column(db.BigInteger, primary_key=True)
    withhold_card_individual_no = db.Column(db.String(20), nullable=False, info='代扣人员编号')
    withhold_card_card_no = db.Column(db.String(20), nullable=False, index=True, info='卡编号')
    withhold_card_bind_time = db.Column(db.DateTime, nullable=False, info='绑定时间')
    withhold_card_priority = db.Column(db.SmallInteger, nullable=False, info='代扣顺序')
    withhold_card_memo = db.Column(db.String(255))
    withhold_card_create_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='创建时间')
    withhold_card_update_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='更新时间')
    withhold_card_from_app = db.Column(db.String(20), nullable=False, server_default=db.FetchedValue())



class WithholdDetail(db.Model, BaseToDict):
    __tablename__ = 'withhold_detail'
    __table_args__ = (
        db.Index('idx_item_no_period', 'withhold_detail_asset_item_no', 'withhold_detail_period'),
    )

    withhold_detail_id = db.Column(db.Integer, primary_key=True, info='主键')
    withhold_detail_serial_no = db.Column(db.String(50), nullable=False, index=True, info='代扣流水号')
    withhold_detail_asset_item_no = db.Column(db.String(50), nullable=False, info='资产编号')
    withhold_detail_period = db.Column(db.Integer, nullable=False, info='期次')
    withhold_detail_asset_tran_type = db.Column(db.String(32), nullable=False, info='资产明细类型，根据asset_tran获取')
    withhold_detail_asset_tran_no = db.Column(db.String(50), nullable=False, info='资产明细编号')
    withhold_detail_asset_tran_amount = db.Column(db.Integer, nullable=False, info='资产应扣金额（单位:分）')
    withhold_detail_asset_tran_balance_amount = db.Column(db.Integer, nullable=False, info='资产剩余金额（单位:分）')
    withhold_detail_withhold_amount = db.Column(db.Integer, nullable=False, info='实际代扣金额（单位:分）')
    withhold_detail_type = db.Column(db.String(32), nullable=False, info='代扣明细分类，根据asset_tran而来')
    withhold_detail_partial = db.Column(db.Enum('Y', 'N'), nullable=False, server_default=db.FetchedValue(), info='是否部分还款')
    withhold_detail_status = db.Column(db.String(16), nullable=False, info='状态')
    withhold_detail_priority = db.Column(db.Integer, nullable=False, info='优先级')
    withhold_detail_create_at = db.Column(db.DateTime, nullable=False, index=True, server_default=db.FetchedValue(), info='创建时间')
    withhold_detail_update_at = db.Column(db.DateTime, nullable=False, index=True, server_default=db.FetchedValue(), info='更新时间')
    withhold_detail_repay_type = db.Column(db.Enum('advance', 'normal', 'overdue'), nullable=False, info='还款类型')
    withhold_detail_ledger_account = db.Column(db.String(64), info='分账账号')



class WithholdExtend(db.Model, BaseToDict):
    __tablename__ = 'withhold_extend'
    __table_args__ = (
        db.Index('idx_withhold_extend_asset_item_no_period', 'withhold_extend_asset_item_no', 'withhold_extend_period'),
    )

    withhold_extend_id = db.Column(db.BigInteger, primary_key=True, info='自增长ID')
    withhold_extend_asset_item_no = db.Column(db.String(50), nullable=False, info='资产编号，或订单编号')
    withhold_extend_period = db.Column(db.Integer, nullable=False, info='代扣期次')
    withhold_extend_asset_type = db.Column(db.String(50), nullable=False, info='资产类型或订单类型')
    withhold_extend_withhold_result_serial_no = db.Column(db.String(50), nullable=False, index=True, info='代扣流水号')
    withhold_extend_refund_result_serial_no = db.Column(db.String(50), info='最后一次退款流水号')
    withhold_extend_repay_type = db.Column(db.Enum('partial', 'full', 'multiple'), nullable=False, info='从代扣金额上判断，部分还款，全额还款，多期还款')
    withhold_extend_should_repay_amount = db.Column(db.BigInteger, nullable=False, info='当期应还金额')
    withhold_extend_duplicate_status = db.Column(db.Enum('normal', 'suspect', 'duplicate'), nullable=False, info='重复代扣状态,normal正常，suspect疑似重复，duplicate确认重复')
    withhold_extend_create_at = db.Column(db.DateTime, nullable=False, index=True, server_default=db.FetchedValue(), info='创建时间')
    withhold_extend_update_at = db.Column(db.DateTime, nullable=False, index=True, server_default=db.FetchedValue(), info='更新时间')
    withhold_extend_repay_time_type = db.Column(db.Enum('normal', 'advance', 'overdue'), nullable=False, server_default=db.FetchedValue(), info='还款时间类型')



class WithholdHi(db.Model, BaseToDict):
    __tablename__ = 'withhold_his'

    withhold_his_id = db.Column(db.Integer, primary_key=True, info='主键')
    withhold_id = db.Column(db.Integer, info='主键')
    withhold_serial_no = db.Column(db.String(32), nullable=False, unique=True, info='代扣流水号，业务主键')
    withhold_request_no = db.Column(db.String(32), nullable=False, info='代扣请求编号')
    withhold_amount = db.Column(db.Integer, nullable=False, info='代扣金额（单位:分）')
    withhold_channel = db.Column(db.String(50), info='代扣渠道，根据不同的放款渠道进行路由')
    withhold_status = db.Column(db.Enum('ready', 'process', 'success', 'fail', 'cancel'), nullable=False, info='状态')
    withhold_sub_status = db.Column(db.Enum('normal', 'payment_cancel', 'agreement'), nullable=False, server_default=db.FetchedValue(), info='子状态,normal:正常,payment_cancel:协议支付取消,agreement:协议支付')
    withhold_channel_code = db.Column(db.String(32), info='代扣渠道返回的code')
    withhold_channel_message = db.Column(db.String(255), info='代扣渠道返回的消息描述')
    withhold_channel_key = db.Column(db.String(64))
    withhold_channel_fee = db.Column(db.Integer, info='代扣渠道费用（单位:分）')
    withhold_comment = db.Column(db.String(255), info='备注')
    withhold_error_code = db.Column(db.String(32), info='根据代扣渠道返回的状态自定义的code')
    withhold_custom_code = db.Column(db.String(32), info='自定义code')
    withhold_supplement = db.Column(db.Enum('Y', 'N'), nullable=False, server_default=db.FetchedValue(), info='是否为补单 Y N ')
    withhold_order = db.Column(db.Integer, info='代扣顺序')
    withhold_third_serial_no = db.Column(db.String(64), info='代扣通道返回的流水号')
    withhold_extend_info = db.Column(db.Text, info='针对一些特殊处理保存数据')
    withhold_create_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='创建时间')
    withhold_update_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='更新时间')
    withhold_execute_at = db.Column(db.DateTime, server_default=db.FetchedValue(), info='执行时间')
    withhold_finish_at = db.Column(db.DateTime, server_default=db.FetchedValue(), info='代扣完成时间')
    withhold_version = db.Column(db.Integer, info='版本号')
    withhold_req_key = db.Column(db.String(64), nullable=False, info='代扣请求key')
    withhold_user_name = db.Column(db.String(32), nullable=False, info='姓名')
    withhold_user_idnum = db.Column(db.String(32), nullable=False, info='身份证号')
    withhold_user_phone = db.Column(db.String(32), nullable=False, info='手机号')
    withhold_card_num = db.Column(db.String(32), nullable=False, info='用户卡号')
    withhold_capital_receive_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='资方接收时间')
    withhold_call_back = db.Column(db.String(500), info='回调地址')


class WithholdOrder(db.Model, BaseToDict):
    __tablename__ = 'withhold_order'
    __table_args__ = (
        db.Index('uidx_serial_no_reference_no', 'withhold_order_serial_no', 'withhold_order_reference_no'),
    )

    withhold_order_id = db.Column(db.Integer, primary_key=True, info='主键')
    withhold_order_request_no = db.Column(db.String(32), nullable=False, index=True, info='请求编号')
    withhold_order_serial_no = db.Column(db.String(64), nullable=False, info='代扣流水号')
    withhold_order_req_key = db.Column(db.String(64), nullable=False, index=True, info='请求key')
    withhold_order_amount = db.Column(db.Integer, nullable=False, info='订单金额（单位:分）')
    withhold_order_withhold_amount = db.Column(db.Integer, nullable=False, info='代扣金额（单位:分）')
    withhold_order_reference_no = db.Column(db.String(50), nullable=False, index=True, info='关联项目编号')
    withhold_order_withhold_status = db.Column(db.Enum('ready', 'process', 'success', 'fail', 'cancel'), nullable=False, info='状态')
    withhold_order_withhold_sub_status = db.Column(db.Enum('normal', 'payment_cancel', 'agreement'), nullable=False, info='子状态,normal:正常,payment_cancel:协议支付取消,agreement:协议支付')
    withhold_order_operate_type = db.Column(db.Enum('active', 'auto', 'manual'), info='代扣操作类型')
    withhold_order_create_at = db.Column(db.DateTime, nullable=False, index=True, server_default=db.FetchedValue(), info='创建时间')
    withhold_order_update_at = db.Column(db.DateTime, nullable=False, index=True, server_default=db.FetchedValue(), info='更新时间')
    withhold_order_balance_amount = db.Column(db.Integer, nullable=False, info='剩余金额(单位:分)')



class WithholdRepeated(db.Model, BaseToDict):
    __tablename__ = 'withhold_repeated'
    __table_args__ = (
        db.Index('idx_serial_no_tran_no', 'withhold_repeated_serial_no', 'withhold_repeated_asset_item_no', 'withhold_repeated_asset_tran_no'),
        db.Index('idx_serial_no_tran_type', 'withhold_repeated_serial_no', 'withhold_repeated_asset_item_no', 'withhold_repeated_asset_tran_type')
    )

    withhold_repeated_id = db.Column(db.Integer, primary_key=True, info='主键')
    withhold_repeated_serial_no = db.Column(db.String(50), nullable=False, info='代扣流水号')
    withhold_repeated_asset_item_no = db.Column(db.String(50), index=True)
    withhold_repeated_asset_tran_type = db.Column(db.String(32), nullable=False, info='资产明细类型')
    withhold_repeated_asset_tran_no = db.Column(db.String(32), nullable=False, info='资产明细编号')
    withhold_repeated_period = db.Column(db.Integer, nullable=False, info='期次')
    withhold_repeated_withhold_amount = db.Column(db.Integer, nullable=False, info='代扣金额（单位:分）')
    withhold_repeated_status = db.Column(db.Enum('normal', 'suspect', 'duplicate'), nullable=False, info='状态,normal:非重复代扣,suspect:疑似重复代扣,duplicate:重复代扣')
    withhold_repeated_create_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='创建时间')
    withhold_repeated_update_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='更新时间')
    withhold_repeated_refund_serial_no = db.Column(db.String(50), info='退款序列号')



class WithholdRequest(db.Model, BaseToDict):
    __tablename__ = 'withhold_request'

    withhold_request_id = db.Column(db.Integer, primary_key=True, info='主键')
    withhold_request_no = db.Column(db.String(32), nullable=False, unique=True, info='业务主键，编号')
    withhold_request_req_key = db.Column(db.String(64), nullable=False, unique=True, info='请求key')
    withhold_request_operate_type = db.Column(db.Enum('active', 'auto', 'manual'), nullable=False, info='代扣操作类型：active  auto  manual')
    withhold_request_amount = db.Column(db.Integer, nullable=False, info='代扣请求金额（单位:分）')
    withhold_request_user_name = db.Column(db.String(32), nullable=False, info='用户姓名')
    withhold_request_user_phone = db.Column(db.String(32), nullable=False, info='手机号')
    withhold_request_user_idnum = db.Column(db.String(32), nullable=False, info='身份证号')
    withhold_request_card_num = db.Column(db.String(32), nullable=False, info='银行卡号')
    withhold_request_bank_code = db.Column(db.String(12), nullable=False, info='银行编码')
    withhold_request_status = db.Column(db.Enum('nofinish', 'finish', 'void'), nullable=False, info='状态,nofinish:未完成,finish:完成,void:作废')
    withhold_request_creator = db.Column(db.String(32), info='创建人')
    withhold_request_operator = db.Column(db.String(32), info='操作人')
    withhold_request_create_at = db.Column(db.DateTime, nullable=False, index=True, server_default=db.FetchedValue(), info='创建时间')
    withhold_request_update_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='修改时间')
    withhold_request_finished_at = db.Column(db.DateTime, info='完成时间')
    withhold_request_origin_req_key = db.Column(db.String(64), index=True, info='原始请求key')
    withhold_request_extend = db.Column(db.Text, info='保存短信验证码等信息')
    withhold_request_from_system = db.Column(db.String(32), info='系统来源')
    withhold_request_trade_type = db.Column(db.String(32), nullable=False, info='交易类型')



class WithholdResult(db.Model, BaseToDict):
    __tablename__ = 'withhold_result'
    __table_args__ = (
        db.Index('idx_withhold_result_user', 'withhold_result_user_idnum', 'withhold_result_card_num'),
    )

    withhold_result_id = db.Column(db.BigInteger, primary_key=True, info='代扣自增长ID')
    withhold_result_no = db.Column(db.String(20), nullable=False, unique=True, info='withhold_result业务主键')
    withhold_result_req_key = db.Column(db.String(50), nullable=False, index=True, info='外部请求key，主动 由贷上钱 提供，自动由 系统生成，手动也由系统生成，同时可以通过该KEY做幂等~~')
    withhold_result_type = db.Column(db.Enum('active', 'auto', 'manual'), nullable=False, info='代扣类型')
    withhold_result_asset_item_no = db.Column(db.String(50), nullable=False, index=True, info='代扣资产编号')
    withhold_result_asset_type = db.Column(db.String(32), nullable=False, info='代扣资产类型')
    withhold_result_asset_period = db.Column(db.Integer, nullable=False, info='代扣资产期数')
    withhold_result_asset_loan_channel = db.Column(db.String(32), nullable=False, info='代扣资产放款渠道')
    withhold_result_amount = db.Column(db.BigInteger, nullable=False, info='代扣总金额(包含通道手续费)')
    withhold_result_user_name = db.Column(db.String(255), nullable=False, server_default=db.FetchedValue(), info='还款人姓名')
    withhold_result_user_phone = db.Column(db.String(32), nullable=False, server_default=db.FetchedValue(), info='还款人手机号')
    withhold_result_user_idnum = db.Column(db.String(32), nullable=False, server_default=db.FetchedValue(), info='还款人身份证号')
    withhold_result_card_num = db.Column(db.String(32), nullable=False, server_default=db.FetchedValue(), info='代扣卡号')
    withhold_result_bank_code = db.Column(db.String(32), nullable=False, info='代扣银行代码')
    withhold_result_status = db.Column(db.Enum('ready', 'success', 'fail', 'process', 'cancel'), nullable=False, info='代扣状态')
    withhold_result_serial_no = db.Column(db.String(50), nullable=False, index=True, info='执行代扣流水号')
    withhold_result_comment = db.Column(db.Text, info='代扣备注')
    withhold_result_run_times = db.Column(db.SmallInteger, nullable=False, info='代扣执行次数')
    withhold_result_channel = db.Column(db.String(32), info='代扣通道')
    withhold_result_channel_key = db.Column(db.String(50), index=True, info='代扣通道返回的key')
    withhold_result_channel_code = db.Column(db.String(32), info='代扣通道返回的code')
    withhold_result_channel_fee = db.Column(db.BigInteger, info='代扣通道费')
    withhold_result_error_code = db.Column(db.String(32), info='代扣由paysvr返回的error_code,如果是其他通道的，需要与paysvr对应')
    withhold_result_custom_code = db.Column(db.String(32), info='代扣->自定义编码')
    withhold_result_withhold_card_no = db.Column(db.String(20), info='轮询代扣卡业务主键，如果是轮询代扣 则写 轮询代扣卡的业务主键，否则为空(null)')
    withhold_result_req_data = db.Column(db.Text, info='代扣请求数据')
    withhold_result_res_data = db.Column(db.Text, info='代扣返回数据')
    withhold_result_create_at = db.Column(db.DateTime, nullable=False, index=True, server_default=db.FetchedValue(), info='创建时间')
    withhold_result_execute_at = db.Column(db.DateTime, nullable=False, info='代扣执行时间')
    withhold_result_update_at = db.Column(db.DateTime, nullable=False, index=True, server_default=db.FetchedValue(), info='代扣更新时间')
    withhold_result_finish_at = db.Column(db.DateTime, nullable=False, index=True, server_default=db.FetchedValue(), info='代扣完成时间，在代扣完成时写入')
    withhold_result_creator = db.Column(db.String(50), nullable=False, server_default=db.FetchedValue(), info='创建者，如果没有则是"系统"')
    withhold_result_operator = db.Column(db.String(50), nullable=False, server_default=db.FetchedValue(), info='操作者，如果没有则是"系统"')
    withhold_result_owner = db.Column(db.String(24), nullable=False, server_default=db.FetchedValue(), info='代扣资产所有者')
    withhold_result_user_name_encrypt = db.Column(db.String(128), nullable=False, server_default=db.FetchedValue(), info='还款人姓名 密文')
    withhold_result_user_phone_encrypt = db.Column(db.String(128), nullable=False, server_default=db.FetchedValue(), info='还款人手机号 密文')
    withhold_result_user_idnum_encrypt = db.Column(db.String(128), nullable=False, index=True, server_default=db.FetchedValue(), info='还款人身份证号 密文')
    withhold_result_card_num_encrypt = db.Column(db.String(128), nullable=False, index=True, server_default=db.FetchedValue(), info='代扣卡号 密文')
    withhold_result_channel_message = db.Column(db.String(128), nullable=False, server_default=db.FetchedValue())
    withhold_result_capital_receive_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='资方接收时间')
