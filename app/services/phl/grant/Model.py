# coding: utf-8

from flask_sqlalchemy import SQLAlchemy

from app.common.db_util import BaseToDict

db = SQLAlchemy()


class Asset(db.Model, BaseToDict):
    __tablename__ = 'asset'

    asset_id = db.Column(db.Integer, primary_key=True, info='资产行号，单表主键')
    asset_item_no = db.Column(db.String(48), nullable=False, unique=True, info='项目编号，有一系列规则，用来标识某个项目，可以从项目编号里看到很多信息')
    asset_type = db.Column(db.String(32), nullable=False, info='资产类型')
    asset_sub_type = db.Column(db.String(32), nullable=False)
    asset_period_type = db.Column(db.Enum('month', 'day'), nullable=False, server_default=db.FetchedValue(), info='还款周期类型')
    asset_period_count = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), info='还款总期数')
    asset_product_category = db.Column(db.String(16), nullable=False, server_default=db.FetchedValue(), info='资产类别名称：14天，30天，3个月，6个月')
    asset_cmdb_product_number = db.Column(db.String(48), nullable=False, server_default=db.FetchedValue(), info='资产产品在费率系统编号')
    asset_create_at = db.Column(db.DateTime, nullable=False, index=True, server_default=db.FetchedValue(), info='创建时间')
    asset_import_at = db.Column(db.DateTime, nullable=False, index=True, server_default=db.FetchedValue(), info='首次进件时间')
    asset_grant_at = db.Column(db.DateTime, nullable=False, index=True, server_default=db.FetchedValue(), info='放款时间')
    asset_effect_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='合同生效日')
    asset_actual_grant_at = db.Column(db.DateTime, nullable=False, index=True, server_default=db.FetchedValue(), info='实际放款日')
    asset_due_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='资产到期日')
    asset_payoff_at = db.Column(db.DateTime, nullable=False, index=True, server_default=db.FetchedValue(), info='偿清时间')
    asset_update_at = db.Column(db.DateTime, nullable=False, index=True, server_default=db.FetchedValue())
    asset_from_system = db.Column(db.String(24), nullable=False, server_default=db.FetchedValue())
    asset_status = db.Column(db.Enum('sign', 'sale', 'repay', 'payoff', 'void', 'writeoff'), nullable=False, server_default=db.FetchedValue(), info='资产状态')
    asset_principal_amount = db.Column(db.BigInteger, nullable=False, server_default=db.FetchedValue(), info='合同本金')
    asset_granted_principal_amount = db.Column(db.BigInteger, nullable=False, server_default=db.FetchedValue(), info='实际放款本金')
    asset_loan_channel = db.Column(db.String(32), nullable=False, server_default=db.FetchedValue(), info='放款渠道')
    asset_alias_name = db.Column(db.String(64), nullable=False, server_default=db.FetchedValue(), info='资产名称')
    asset_interest_amount = db.Column(db.BigInteger, nullable=False, server_default=db.FetchedValue(), info='利息总金额')
    asset_fee_amount = db.Column(db.BigInteger, nullable=False, server_default=db.FetchedValue(), info='费总金额')
    asset_balance_amount = db.Column(db.BigInteger, nullable=False, server_default=db.FetchedValue(), info='剩余未偿还总金额(分）包括：本，息，费')
    asset_repaid_amount = db.Column(db.BigInteger, nullable=False, server_default=db.FetchedValue(), info='已偿还总金额')
    asset_total_amount = db.Column(db.BigInteger, nullable=False, server_default=db.FetchedValue(), info='本息费总额。\\n=principalAmt+interestAmt+feeAmt\\n=balance_amount+repaidAmt\\n')
    asset_version = db.Column(db.BigInteger, server_default=db.FetchedValue(), info='资产修改版本号, 主动修改资产时才递增版本号')
    asset_interest_rate = db.Column(db.Numeric(10, 3), nullable=False, server_default=db.FetchedValue(), info='利率')
    asset_from_system_name = db.Column(db.String(10), nullable=False, server_default=db.FetchedValue(), info='资产来源系统名称')
    asset_owner = db.Column(db.String(24), nullable=False, server_default=db.FetchedValue(), info='资产所有权者(KN-快牛、STB)')
    asset_idnum_encrypt = db.Column(db.String(128), nullable=False, index=True, server_default=db.FetchedValue(), info='身份证密文')
    asset_from_app = db.Column(db.String(100), nullable=False, server_default=db.FetchedValue(), info='马甲包字段')


class AssetAttachment(db.Model, BaseToDict):
    __tablename__ = 'asset_attachment'

    asset_attachment_id = db.Column(db.Integer, primary_key=True)
    asset_attachment_type = db.Column(db.Integer, nullable=False)
    asset_attachment_type_text = db.Column(db.String(255), nullable=False, server_default=db.FetchedValue())
    asset_attachment_url = db.Column(db.String(1000), nullable=False, server_default=db.FetchedValue())
    asset_attachment_status = db.Column(db.Integer, nullable=False, info='状态：1：正常；0：作废')
    asset_attachment_from_system = db.Column(db.String(24), server_default=db.FetchedValue(), info='附件来源：进件为来源系统dsq/hxyl，合同下载对应资方渠道')
    asset_attachment_create_at = db.Column(db.DateTime, nullable=False, index=True, server_default=db.FetchedValue(), info='创建时间')
    asset_attachment_update_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='更新时间')
    asset_attachment_contract_code = db.Column(db.String(25), nullable=False, server_default=db.FetchedValue(), info='合同编号')
    asset_attachment_contract_sign_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info=' 合同签约时间')
    asset_attachment_asset_item_no = db.Column(db.String(48), nullable=False, index=True, server_default=db.FetchedValue(), info='资产编号')


class AssetCard(db.Model, BaseToDict):
    __tablename__ = 'asset_card'

    asset_card_id = db.Column(db.Integer, primary_key=True)
    asset_card_type = db.Column(db.Enum('receive', 'repay'), nullable=False, server_default=db.FetchedValue(), info='卡类型 receive 收款卡,repay 还款卡')
    asset_card_owner_type = db.Column(db.Enum('individual', 'enterprise'), server_default=db.FetchedValue(), info='持有人类型：individual：个人；enterprise：企业')
    asset_card_account_category = db.Column(db.Enum('private', 'public'), server_default=db.FetchedValue(), info='账户种类：private：对私；public：对公')
    asset_card_account_branch_name = db.Column(db.String(32), info='开户行名称')
    asset_card_account_type = db.Column(db.Enum('debit', 'loan'), server_default=db.FetchedValue(), info='账户类型：debit：借记卡；loan：贷记卡')
    asset_card_account_bank_name = db.Column(db.String(45), info='银行名称')
    asset_card_account_bank_code = db.Column(db.String(50), info='银行编码')
    asset_card_create_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())
    asset_card_create_user_name = db.Column(db.String(10), nullable=False)
    asset_card_update_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())
    asset_card_update_user_name = db.Column(db.String(10), nullable=False)
    asset_card_status = db.Column(db.Enum('inactive', 'active'), nullable=False, server_default=db.FetchedValue(), info='状态')
    asset_card_owner_idnum_encrypt = db.Column(db.String(128), nullable=False, index=True, server_default=db.FetchedValue(), info='持卡人身份证号/企业lincense number加密')
    asset_card_owner_name_encrypt = db.Column(db.String(128), nullable=False, server_default=db.FetchedValue(), info='持卡人姓名/企业名称加密')
    asset_card_account_name_encrypt = db.Column(db.String(128), nullable=False, server_default=db.FetchedValue(), info='账户户名加密')
    asset_card_account_tel_encrypt = db.Column(db.String(128), nullable=False, server_default=db.FetchedValue(), info='账户手机号加密')
    asset_card_account_idnum_encrypt = db.Column(db.String(128), nullable=False, index=True, server_default=db.FetchedValue(), info='账户身份证号加密')
    asset_card_account_card_number_encrypt = db.Column(db.String(128), nullable=False, server_default=db.FetchedValue(), info='账户号加密')
    asset_card_asset_item_no = db.Column(db.String(48), nullable=False, index=True, server_default=db.FetchedValue(), info='资产编号')


class AssetConfirm(db.Model, BaseToDict):
    __tablename__ = 'asset_confirm'
    __table_args__ = (
        db.Index('idx_asset_confirm_item_no_type_channel', 'asset_confirm_item_no', 'asset_confirm_channel', 'asset_confirm_type'),
    )

    asset_confirm_id = db.Column(db.Integer, primary_key=True, info='主键')
    asset_confirm_item_no = db.Column(db.String(48), nullable=False, server_default=db.FetchedValue(), info='资产编号')
    asset_confirm_channel = db.Column(db.String(32), nullable=False, server_default=db.FetchedValue(), info='资金方')
    asset_confirm_type = db.Column(db.String(32), nullable=False, server_default=db.FetchedValue(), info='操作类型')
    asset_confirm_status = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), info='状态(0:成功,1:失败,2:处理中,3:超时)')
    asset_confirm_memo = db.Column(db.String(256), server_default=db.FetchedValue(), info='备注')
    asset_confirm_request_data = db.Column(db.String(1024), info='交互请求数据')
    asset_confirm_response_data = db.Column(db.String(1024), info='交互返回数据')
    asset_confirm_retry_times = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), info='允许最大请求次数')
    asset_confirm_create_at = db.Column(db.DateTime, nullable=False, index=True, server_default=db.FetchedValue(), info='创建时间')
    asset_confirm_update_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='更新时间')


class AssetEvent(db.Model, BaseToDict):
    __tablename__ = 'asset_event'
    __table_args__ = (
        db.Index('idx_asset_event_create_at', 'asset_event_create_at', 'asset_event_channel'),
    )

    asset_event_id = db.Column(db.Integer, primary_key=True, info='pk')
    asset_event_item_no = db.Column(db.String(48), nullable=False, index=True, server_default=db.FetchedValue(), info='资产编号')
    asset_event_channel = db.Column(db.String(32), nullable=False, server_default=db.FetchedValue(), info='渠道')
    asset_event_no = db.Column(db.String(2048), nullable=False, server_default=db.FetchedValue(), info='资产流水号')
    asset_event_create_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='创建时间')
    asset_event_update_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='最近更新时间')
    asset_event_memo = db.Column(db.String(64), nullable=False, server_default=db.FetchedValue(), info='备注信息')
    asset_event_type = db.Column(db.String(32), server_default=db.FetchedValue(), info='事件类型')


class AssetExtend(db.Model, BaseToDict):
    __tablename__ = 'asset_extend'

    asset_extend_id = db.Column(db.Integer, primary_key=True)
    asset_extend_district_id = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), info='区域ID')
    asset_extend_create_at = db.Column(db.DateTime, nullable=False, index=True, server_default=db.FetchedValue())
    asset_extend_update_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())
    asset_extend_charge_type = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), info='前置/后置收费')
    asset_extend_loan_usage = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), info='借款用途：0 未知 1 购物 2 娱乐 3 教育 4 旅游 5 装修 6 美容 7 运动')
    asset_extend_asset_item_no = db.Column(db.String(48), nullable=False, index=True, server_default=db.FetchedValue(), info='资产编号')
    asset_extend_ref_order_no = db.Column(db.String(64), nullable=False, index=True, server_default=db.FetchedValue(), info='资产关联订单号')
    asset_extend_ref_order_type = db.Column(db.String(50), nullable=False, server_default=db.FetchedValue(), info='资产关联订单类型')
    asset_extend_withholding_amount = db.Column(db.BigInteger, nullable=False, server_default=db.FetchedValue(), info='预先扣款金额')
    asset_extend_risk_level = db.Column(db.String(10), nullable=False, server_default=db.FetchedValue(), info='风控评级')
    asset_extend_sub_order_type = db.Column(db.String(50), nullable=False, server_default=db.FetchedValue(), info='子订单类型')
    asset_extend_product_name = db.Column(db.String(50), server_default=db.FetchedValue(), info='产品名称')
    asset_extend_flow_type = db.Column(db.SmallInteger, nullable=False, server_default=db.FetchedValue(), info='此资产要走的流程类型 0老流程，1新流程')
    asset_extend_overdue_guarantee_amount = db.Column(db.BigInteger, nullable=False, server_default=db.FetchedValue(), info='逾期担保服务费')
    asset_extend_info = db.Column(db.String(64), server_default=db.FetchedValue(), info='扩展信息')
    asset_extend_distribute_type = db.Column(db.SmallInteger, nullable=False, server_default=db.FetchedValue(), info='分发类型 1：分发类型，2：共债类型')


class AssetIndividual(db.Model, BaseToDict):
    __tablename__ = 'asset_individual'

    asset_individual_id = db.Column(db.Integer, primary_key=True)
    asset_individual_type = db.Column(db.Enum('borrow', 'repay'), nullable=False, info='个人类型：borrow：借款人; repay:还款人')
    asset_individual_id_addr = db.Column(db.String(255), info='身份证地址')
    asset_individual_id_type = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), info='身份类型(0-未知,1-在职,2-在读,3-待业)')
    asset_individual_id_post_code = db.Column(db.String(8), info='身份证地址邮编')
    asset_individual_gender = db.Column(db.Enum('f', 'm'), info='性别')
    asset_individual_education = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), info='学历(0-未知,1-博士研究生,2-硕士研究生,3-本科,4-大专,5-中专,6-技校,7-高中,8-初中,9-小学,10-文盲或半文盲)')
    asset_individual_income_lft = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), info='收入区间左值')
    asset_individual_income_rgt = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), info='收入区间右值')
    asset_individual_credit_type = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), info='信用类型(0-未知,1-芝麻分,2-万象分,3-考拉分,4-星辰分,5-京东分,\\n6-腾讯分)')
    asset_individual_credit_score = db.Column(db.Integer, server_default=db.FetchedValue(), info='信用分数')
    asset_individual_residence = db.Column(db.String(128), info='居住地')
    asset_individual_corp_name = db.Column(db.String(255), info='单位名称')
    asset_individual_corp_tel = db.Column(db.String(16), info='单位电话')
    asset_individual_corp_trade = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), info='单位所属行业(0-未知,1-政府机关/社会团体,2-军事/公检法,3-教育/科研,4-医院,5-公共事业/邮电通信/仓储运输物流,6-建筑业,7-传统制造业,8-互联网/其他高新技术行业,9-金融业,10-商业/贸易,11-餐饮/酒店/旅游,12-媒体/体育/娱乐,13-服务业,14-专业事务所,15-农林牧渔/自由职业/其他)')
    asset_individual_residence_tel = db.Column(db.String(16), info='住宅电话')
    asset_individual_residence_status = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), info='居住状况(0-未知,1-自置,2-按揭,3-亲属楼宇,4-集体宿舍,5-租房,6-共有住宅,7-其他)')
    asset_individual_workplace = db.Column(db.String(128), info='工作地')
    asset_individual_marriage = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), info='婚姻状况(0-未知,1-未婚,2-已婚,3-丧偶,4-离婚)')
    asset_individual_duty = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), info='职务(0-未知,1-高级管理人员,2-中级管理人员,3-办公类员工,4-技术类员工,5-后勤类员工,6-操作类员工,7-服务类员工,8-销售类员工,9-其他类型员工)')
    asset_individual_relative_relation = db.Column(db.String(32), info='和借款人的亲属关系')
    asset_individual_enrollment_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='入学时间')
    asset_individual_school_place = db.Column(db.String(128), nullable=False, server_default=db.FetchedValue(), info='学校电话')
    asset_individual_school_name = db.Column(db.String(128), nullable=False, server_default=db.FetchedValue(), info='学校名称')
    asset_individual_create_at = db.Column(db.DateTime, nullable=False, index=True, server_default=db.FetchedValue())
    asset_individual_create_user_name = db.Column(db.String(10), nullable=False)
    asset_individual_update_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())
    asset_individual_update_user_name = db.Column(db.String(10), nullable=False)
    asset_individual_second_relative_relation = db.Column(db.String(32), nullable=False, server_default=db.FetchedValue(), info='第二联系人和借款人的亲属关系')
    asset_individual_name_encrypt = db.Column(db.String(128), nullable=False, server_default=db.FetchedValue(), info='姓名加密')
    asset_individual_idnum_encrypt = db.Column(db.String(128), nullable=False, index=True, server_default=db.FetchedValue(), info='身份证号码加密')
    asset_individual_tel_encrypt = db.Column(db.String(128), nullable=False, server_default=db.FetchedValue(), info='联系电话加密')
    asset_individual_account_name_encrypt = db.Column(db.String(128), nullable=False, server_default=db.FetchedValue(), info='个人在财务系统中的名称加密')
    asset_individual_mate_name_encrypt = db.Column(db.String(128), nullable=False, server_default=db.FetchedValue(), info='配偶姓名加密')
    asset_individual_mate_tel_encrypt = db.Column(db.String(128), nullable=False, server_default=db.FetchedValue(), info='配偶联系方式加密')
    asset_individual_relative_name_encrypt = db.Column(db.String(128), nullable=False, server_default=db.FetchedValue(), info='亲属姓名加密')
    asset_individual_relative_tel_encrypt = db.Column(db.String(128), nullable=False, server_default=db.FetchedValue(), info='亲属联系方式加密')
    asset_individual_workmate_name_encrypt = db.Column(db.String(128), nullable=False, server_default=db.FetchedValue(), info='同事姓名加密')
    asset_individual_workmate_tel_encrypt = db.Column(db.String(128), nullable=False, server_default=db.FetchedValue(), info='同事联系方式加密')
    asset_individual_second_relative_name_encrypt = db.Column(db.String(128), nullable=False, server_default=db.FetchedValue(), info='第二联系人亲属姓名加密')
    asset_individual_second_relative_tel_encrypt = db.Column(db.String(128), nullable=False, server_default=db.FetchedValue(), info='第二联系人联系方式加密')
    asset_individual_asset_item_no = db.Column(db.String(48), nullable=False, index=True, server_default=db.FetchedValue(), info='资产编号')
    asset_individual_nation = db.Column(db.String(10), nullable=False, server_default=db.FetchedValue(), info='民族；例如 汉族，苗族，土家族')
    asset_individual_email = db.Column(db.String(100), nullable=False, server_default=db.FetchedValue(), info='邮箱地址')
    asset_individual_income_source = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), info='收入来源(1-工资收入,2-个人经营收入,3-其他非工资收入)')
    asset_individual_province_code = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), info='省份编码')
    asset_individual_city_code = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), info='城市编码')
    asset_individual_province_name = db.Column(db.String(32), nullable=False, server_default=db.FetchedValue(), info='省份名称')
    asset_individual_city_name = db.Column(db.String(32), nullable=False, server_default=db.FetchedValue(), info='城市名称')



class AssetIndividualExtend(db.Model, BaseToDict):
    __tablename__ = 'asset_individual_extend'

    asset_individual_extend_id = db.Column(db.BigInteger, primary_key=True)
    asset_individual_extend_asset_item_no = db.Column(db.String(48), index=True)
    asset_individual_extend_is_enterpise_master = db.Column(db.Integer, info='是否是企业主')
    asset_individual_extend_career_type = db.Column(db.String(20), info='职业类型')
    asset_individual_extend_share_ratio = db.Column(db.String(10), info='借款人持股占比')
    asset_individual_extend_business_times = db.Column(db.Integer, info='企业经营时间')
    asset_individual_extend_work_years = db.Column(db.Integer, info='工作年限')
    asset_individual_extend_social_insurance = db.Column(db.Integer, info='是否有社保')
    asset_individual_extend_industry_type = db.Column(db.String(20), info='行业类型')
    asset_individual_extend_info = db.Column(db.String(2048), server_default=db.FetchedValue(), info='用户信息扩展信息')



class AssetInsurance(db.Model, BaseToDict):
    __tablename__ = 'asset_insurance'

    asset_insurance_id = db.Column(db.Integer, primary_key=True, info='自增id')
    asset_insurance_item_no = db.Column(db.String(48), nullable=False, index=True, server_default=db.FetchedValue(), info='资产编号')
    asset_insurance_period = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), info='保单对应的资产期次')
    asset_insurance_order_no = db.Column(db.String(64), nullable=False, index=True, server_default=db.FetchedValue(), info='保险公司订单号')
    asset_insurance_bill_no = db.Column(db.String(64), nullable=False, index=True, server_default=db.FetchedValue(), info='保单编号（保险业务接口需要用）')
    asset_insurance_company_bill_no = db.Column(db.String(64), nullable=False, server_default=db.FetchedValue(), info='保险公司保单号码')
    asset_insurance_start_time = db.Column(db.DateTime, server_default=db.FetchedValue(), info='起保日期')
    asset_insurance_end_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='保险截止日期')
    asset_insurance_premium = db.Column(db.Float(asdecimal=True), nullable=False, server_default=db.FetchedValue(), info='保费')
    asset_insurance_amount = db.Column(db.BigInteger, nullable=False, server_default=db.FetchedValue(), info='保额')
    asset_insurance_status = db.Column(db.Integer, server_default=db.FetchedValue(), info='状态0：待生效，1：生效中，2：已确保（缴费），3：已作废（仅用于资产作废），4：已退保（未还款过期），5：已失效（正常还款过期）')
    asset_insurance_confirm_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='确费时间')
    asset_insurance_create_at = db.Column(db.DateTime, nullable=False, index=True, server_default=db.FetchedValue(), info='创建时间')
    asset_insurance_update_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='更新时间')
    asset_insurance_company_name = db.Column(db.String(64), server_default=db.FetchedValue(), info='保险公司名字')
    asset_insurance_contract_status = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), info='保单状态：0 - 待下载; 1 - 已下载; 2 - 已同步;')
    asset_insurance_contract_url = db.Column(db.String(1000), server_default=db.FetchedValue(), info='合同下载地址')
    asset_insurance_process_info = db.Column(db.String(512), nullable=False, server_default=db.FetchedValue(), info='保单流程')



class AssetLoanRecord(db.Model, BaseToDict):
    __tablename__ = 'asset_loan_record'
    __table_args__ = (
        db.Index('idx_asset_loan_record_asset_item_no', 'asset_loan_record_asset_item_no', 'asset_loan_record_channel'),
    )

    asset_loan_record_id = db.Column(db.Integer, primary_key=True, info='主键')
    asset_loan_record_asset_item_no = db.Column(db.String(48), nullable=False, info='资产编号')
    asset_loan_record_amount = db.Column(db.BigInteger, nullable=False, info='放款金额，即本金，单位：分')
    asset_loan_record_withholding_amount = db.Column(db.BigInteger, nullable=False, server_default=db.FetchedValue(), info='预扣金额，单位：分')
    asset_loan_record_channel = db.Column(db.String(32), nullable=False, info='放款渠道')
    asset_loan_record_status = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), info='放款状态(0-新建，1-进件中，2-进件失败，3-进件成功，4-放款中（审核通过），5-放款失败，6-放款成功，7-审核不通过，8-放款到二类户成功, 9-资金归集成功, 10-放款到二类户/虚户失败, 11-提现中, 12-提现取消)')
    asset_loan_record_identifier = db.Column(db.String(100), nullable=False, unique=True, server_default=db.FetchedValue(), info='编号')
    asset_loan_record_trade_no = db.Column(db.String(45), nullable=False, unique=True, server_default=db.FetchedValue(), info='进件流水号')
    asset_loan_record_due_bill_no = db.Column(db.String(45), index=True, server_default=db.FetchedValue(), info='借据号')
    asset_loan_record_finish_at = db.Column(db.DateTime, nullable=False, index=True, server_default=db.FetchedValue(), info='放款时间')
    asset_loan_record_create_at = db.Column(db.DateTime, nullable=False, index=True, server_default=db.FetchedValue(), info='创建时间')
    asset_loan_record_update_at = db.Column(db.DateTime, nullable=False, index=True, server_default=db.FetchedValue(), info='更新时间')
    asset_loan_record_grant_at = db.Column(db.DateTime, nullable=False, index=True, server_default=db.FetchedValue(), info='放款到虚户/二类户的时间')
    asset_loan_record_memo = db.Column(db.String(2048), server_default=db.FetchedValue(), info='备注信息')
    asset_loan_record_push_at = db.Column(db.DateTime, nullable=False, index=True, server_default=db.FetchedValue(), info='发起进件请求时间')



class AssetLoanRequestLog(db.Model, BaseToDict):
    __tablename__ = 'asset_loan_request_log'

    asset_loan_request_log_id = db.Column(db.Integer, primary_key=True, info='主键')
    asset_loan_request_log_asset_no = db.Column(db.String(25), nullable=False, index=True, server_default=db.FetchedValue(), info='资产主键')
    asset_loan_request_log_asset_item_no = db.Column(db.String(48), nullable=False, index=True, info='资产编号')
    asset_loan_request_log_channel = db.Column(db.String(32), nullable=False, info='资金方')
    asset_loan_request_log_key = db.Column(db.String(60), nullable=False, index=True, info='请求流水号')
    asset_loan_request_log_status = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), info='请求结果(0：成功，1：失败，2：处理中)')
    asset_loan_request_log_comment = db.Column(db.Text, info='请求备注')
    asset_loan_request_log_request_data = db.Column(db.Text, nullable=False, info='请求参数')
    asset_loan_request_log_response_data = db.Column(db.Text, info='返回参数')
    asset_loan_request_log_create_at = db.Column(db.DateTime, nullable=False, index=True, server_default=db.FetchedValue(), info='创建时间')
    asset_loan_request_log_update_at = db.Column(db.DateTime, nullable=False, index=True, server_default=db.FetchedValue(), info='更新时间')



class AssetRiskInfo(db.Model, BaseToDict):
    __tablename__ = 'asset_risk_info'

    asset_risk_info_id = db.Column(db.Integer, primary_key=True, info='主键')
    asset_risk_info_item_no = db.Column(db.String(48), nullable=False, index=True, info='资产编号')
    asset_risk_info_channel = db.Column(db.String(32), nullable=False, index=True, info='资金方')
    asset_risk_info_comment = db.Column(db.String(128), info='请求备注')
    asset_risk_info_request_data = db.Column(db.Text, info='请求参数')
    asset_risk_info_response_data = db.Column(db.Text, info='返回参数')
    asset_risk_info_log_key = db.Column(db.String(60), nullable=False, index=True, info='请求流水号')
    asset_risk_info_create_at = db.Column(db.DateTime, nullable=False, index=True, server_default=db.FetchedValue(), info='创建时间')
    asset_risk_info_update_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='更新时间')



class AssetRouteLog(db.Model, BaseToDict):
    __tablename__ = 'asset_route_log'

    asset_route_log_id = db.Column(db.Integer, primary_key=True)
    asset_route_log_asset_item_no = db.Column(db.String(64), index=True, info='资产编号')
    asset_route_log_asset_type = db.Column(db.String(60), nullable=False, server_default=db.FetchedValue(), info='资产类型')
    asset_route_log_borrower_idnum = db.Column(db.String(32), index=True, info='借款人身份证号')
    asset_route_log_borrower_name = db.Column(db.String(32), nullable=False, info='借款人姓名')
    asset_route_log_loan_channel = db.Column(db.String(32), nullable=False, server_default=db.FetchedValue(), info='放款渠道')
    asset_route_log_message = db.Column(db.String(4096), nullable=False, server_default=db.FetchedValue(), info='消息')
    asset_route_create_at = db.Column(db.DateTime, nullable=False, index=True)
    asset_route_update_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())
    asset_route_log_route_type = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), info='1:一次路由;2:二次路由')
    asset_route_log_period_count = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), info='request路由期数如1，3，6')


class AssetBorrower(db.Model, BaseToDict):
    __tablename__ = 'asset_borrower'
    asset_borrower_id = db.Column(db.Integer, primary_key=True)
    asset_borrower_item_no = db.Column(db.String(64), index=True, info='资产编号')
    asset_borrower_card_uuid = db.Column(db.String(64), nullable=False, server_default=db.FetchedValue(), info='资产类型')
    asset_borrower_uuid = db.Column(db.String(64), index=True, info='借款人身份证号')
    asset_borrower_id_num = db.Column(db.String(50), nullable=False, info='借款人姓名')
    asset_borrower_mobile = db.Column(db.String(32), nullable=False, server_default=db.FetchedValue(), info='放款渠道')
    asset_borrower_loan_usage = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), info='消息')
    asset_borrower_risk_level = db.Column(db.String(10), nullable=False, server_default=db.FetchedValue(), info='消息')
    asset_borrower_extend_info = db.Column(db.String(1024), nullable=False, server_default=db.FetchedValue(), info='消息')
    asset_borrower_individual_uuid = db.Column(db.String(64), nullable=False, server_default=db.FetchedValue(), info='消息')
    asset_borrower_create_at = db.Column(db.DateTime, nullable=False, index=True)
    asset_borrower_update_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())


class AssetTran(db.Model, BaseToDict):
    __tablename__ = 'asset_tran'

    asset_tran_id = db.Column(db.Integer, primary_key=True, info='表主键')
    asset_tran_type = db.Column(db.String(32), nullable=False, info="交易类型：\\n'grant’:放款\\n’repayinterest’：偿还利息\\n'repayprincipal’，偿还本金\\n‘services’：技术服务费\\nmanage:管理费.")
    asset_tran_description = db.Column(db.String(64), nullable=False, info='交易类型中文描述')
    asset_tran_amount = db.Column(db.BigInteger, nullable=False, server_default=db.FetchedValue(), info='实际需要交易的金额 =repaidAmt+balanceAmt')
    asset_tran_decrease_amount = db.Column(db.BigInteger, nullable=False, server_default=db.FetchedValue())
    asset_tran_repaid_amount = db.Column(db.BigInteger, nullable=False, server_default=db.FetchedValue())
    asset_tran_balance_amount = db.Column(db.BigInteger, nullable=False, server_default=db.FetchedValue())
    asset_tran_total_amount = db.Column(db.BigInteger, nullable=False, server_default=db.FetchedValue(), info='总金额：\\n=tranAmt+decrease')
    asset_tran_status = db.Column(db.Enum('finish', 'nofinish'), nullable=False)
    asset_tran_create_at = db.Column(db.DateTime, nullable=False)
    asset_tran_due_at = db.Column(db.DateTime, nullable=False)
    asset_tran_finish_at = db.Column(db.DateTime, nullable=False, index=True)
    asset_tran_update_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())
    asset_tran_period = db.Column(db.Integer, nullable=False)
    asset_tran_late_status = db.Column(db.String(20), nullable=False, server_default=db.FetchedValue())
    asset_tran_remark = db.Column(db.String(2048), nullable=False, server_default=db.FetchedValue())
    asset_tran_repay_priority = db.Column(db.Integer, nullable=False)
    asset_tran_trade_at = db.Column(db.DateTime, nullable=False)
    asset_tran_category = db.Column(db.Enum('grant', 'principal', 'interest', 'fee'), nullable=False)
    asset_tran_asset_item_no = db.Column(db.String(48), nullable=False, index=True, server_default=db.FetchedValue(), info='资产编号')



class CapitalAccount(db.Model, BaseToDict):
    __tablename__ = 'capital_account'
    __table_args__ = (
        db.Index('idx_account_unique', 'capital_account_card_number_encrypt', 'capital_account_channel', 'capital_account_sub_channel'),
    )

    capital_account_id = db.Column(db.BigInteger, primary_key=True)
    capital_account_item_no = db.Column(db.String(64), nullable=False, index=True, server_default=db.FetchedValue(), info='资产编号')
    capital_account_memo = db.Column(db.String(256), info='错误原因')
    capital_account_user_key = db.Column(db.String(128), info='开户成功后，返回的用户唯一标识')
    capital_account_channel = db.Column(db.String(50), nullable=False, info='资金方')
    capital_account_sub_channel = db.Column(db.String(32), nullable=False, server_default=db.FetchedValue(), info='子场景')
    capital_account_status = db.Column(db.Integer, nullable=False, info='开户结果(0:success,1:fail,2:processing)')
    capital_account_create_at = db.Column(db.DateTime, nullable=False, index=True, server_default=db.FetchedValue())
    capital_account_update_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())
    capital_account_way = db.Column(db.String(20), info='通道')
    capital_account_card_number_encrypt = db.Column(db.String(128), info='银行卡脱敏')
    capital_account_idnum_encrypt = db.Column(db.String(128), index=True, info='身份证号脱敏')
    capital_account_name_encrypt = db.Column(db.String(128), nullable=False, server_default=db.FetchedValue(), info='姓名(密文)')
    capital_account_mobile_encrypt = db.Column(db.String(128), nullable=False, server_default=db.FetchedValue(), info='手机号(密文)')



class CapitalAccountAction(db.Model, BaseToDict):
    __tablename__ = 'capital_account_action'
    __table_args__ = (
        db.Index('uniq_idx_item_no_step_id_type', 'capital_account_action_item_no', 'capital_account_action_type', 'capital_account_action_account_step_id'),
    )

    capital_account_action_id = db.Column(db.BigInteger, primary_key=True, info='主键')
    capital_account_action_account_step_id = db.Column(db.BigInteger, nullable=False, index=True, info='capital_account_step表id')
    capital_account_action_item_no = db.Column(db.String(64), nullable=False, index=True, server_default=db.FetchedValue(), info='资产编号')
    capital_account_action_type = db.Column(db.String(32), server_default=db.FetchedValue(), info='开户请求类型')
    capital_account_action_seq = db.Column(db.String(64), index=True, server_default=db.FetchedValue(), info='验证序列')
    capital_account_action_sub_way = db.Column(db.String(32), nullable=False, server_default=db.FetchedValue(), info='通道')
    capital_account_action_group = db.Column(db.String(32), server_default=db.FetchedValue(), info='开户分组')
    capital_account_action_status = db.Column(db.Integer, server_default=db.FetchedValue(), info='环节状态(0:成功,1:不可重试失败,2:可重试失败,3:超时失败,4:未执行)')
    capital_account_action_message = db.Column(db.String(128), nullable=False, server_default=db.FetchedValue(), info='执行信息')
    capital_account_action_retry_times = db.Column(db.Integer, server_default=db.FetchedValue(), info='重试次数')
    capital_account_action_comment = db.Column(db.String(1024), nullable=False, server_default=db.FetchedValue(), info='备注')
    capital_account_action_finish_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='环节完成时间')
    capital_account_action_create_at = db.Column(db.DateTime, index=True, server_default=db.FetchedValue(), info='创建时间')
    capital_account_action_update_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='更新时间')



class CapitalAccountBlacklist(db.Model, BaseToDict):
    __tablename__ = 'capital_account_blacklist'
    __table_args__ = (
        db.Index('idx_capital_account_blacklist_card_number_sub_way', 'capital_account_blacklist_card_number_encrypt', 'capital_account_blacklist_sub_way'),
    )

    capital_account_blacklist_id = db.Column(db.BigInteger, primary_key=True)
    capital_account_blacklist_idnum_encrypt = db.Column(db.String(128), nullable=False, info='身份证')
    capital_account_blacklist_card_number_encrypt = db.Column(db.String(32), nullable=False, info='银行卡')
    capital_account_blacklist_type = db.Column(db.String(32), nullable=False, info='黑名单类型(SMS:绑卡短信)')
    capital_account_blacklist_sub_way = db.Column(db.String(50), nullable=False, info='绑卡通道')
    capital_account_blacklist_code = db.Column(db.String(32), info='列入黑名单编码')
    capital_account_blacklist_msg = db.Column(db.String(256), info='列入黑名单信息')
    capital_account_blacklist_create_at = db.Column(db.DateTime, nullable=False, index=True, server_default=db.FetchedValue())
    capital_account_blacklist_update_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())
    capital_account_blacklist_expired_at = db.Column(db.DateTime, nullable=False, index=True, server_default=db.FetchedValue(), info='过期时间')



class CapitalAccountCard(db.Model, BaseToDict):
    __tablename__ = 'capital_account_card'
    __table_args__ = (
        db.Index('idx_account_card_unique', 'capital_account_card_account_id', 'capital_account_card_card_number_encrypt', 'capital_account_card_step', 'capital_account_card_way'),
    )

    capital_account_card_id = db.Column(db.BigInteger, primary_key=True)
    capital_account_card_item_no = db.Column(db.String(64), nullable=False, index=True, server_default=db.FetchedValue(), info='资产编号')
    capital_account_card_account_id = db.Column(db.BigInteger, nullable=False, index=True, info='capital_account表id')
    capital_account_card_user_key = db.Column(db.String(128), index=True, info='步骤成功唯一标识')
    capital_account_card_status = db.Column(db.Integer, info='状态(0:成功,1:失败,2:处理中,3:中断)')
    capital_account_card_step = db.Column(db.String(50), server_default=db.FetchedValue(), info='步骤')
    capital_account_card_way = db.Column(db.String(32), nullable=False, server_default=db.FetchedValue(), info='通道')
    capital_account_card_card_number_encrypt = db.Column(db.String(128), index=True, info='银行卡脱敏')
    capital_account_card_create_at = db.Column(db.DateTime, server_default=db.FetchedValue(), info='创建时间')
    capital_account_card_update_at = db.Column(db.DateTime, server_default=db.FetchedValue(), info='修改时间')
    capital_account_card_retry_times = db.Column(db.Integer, server_default=db.FetchedValue(), info='请求次数')
    capital_account_card_name_encrypt = db.Column(db.String(128), info='姓名脱敏')
    capital_account_card_phone_encrypt = db.Column(db.String(128), index=True, info='手机号脱敏')
    capital_account_card_serial_no = db.Column(db.String(255), info='流水号')
    capital_account_card_memo = db.Column(db.String(256), server_default=db.FetchedValue(), info='备注信息')



class CapitalAccountRequest(db.Model, BaseToDict):
    __tablename__ = 'capital_account_request'

    capital_account_request_id = db.Column(db.BigInteger, primary_key=True, info='主键')
    capital_account_request_account_card_id = db.Column(db.BigInteger, nullable=False, index=True, info='capital_account_card表id')
    capital_account_request_item_no = db.Column(db.String(64), nullable=False, index=True, server_default=db.FetchedValue(), info='资产编号')
    capital_account_request_sub_way = db.Column(db.String(32), server_default=db.FetchedValue(), info='绑卡通道')
    capital_account_request_type = db.Column(db.Enum('SMS'), server_default=db.FetchedValue(), info='开户请求类型')
    capital_account_request_seq = db.Column(db.String(64), index=True, server_default=db.FetchedValue(), info='验证序列')
    capital_account_request_status = db.Column(db.Integer, server_default=db.FetchedValue(), info='绑卡状态(0:新建,1:成功,2:失败)')
    capital_account_request_group = db.Column(db.String(32), server_default=db.FetchedValue(), info='开户分组')
    capital_account_request_comment = db.Column(db.String(1024), nullable=False, server_default=db.FetchedValue(), info='备注')
    capital_account_request_finish_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='绑卡完成时间')
    capital_account_request_create_at = db.Column(db.DateTime, server_default=db.FetchedValue(), info='创建时间')
    capital_account_request_update_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='更新时间')



class CapitalAccountStep(db.Model, BaseToDict):
    __tablename__ = 'capital_account_step'
    __table_args__ = (
        db.Index('uniq_idx_account_id_step_way', 'capital_account_step_account_id', 'capital_account_step_step', 'capital_account_step_way'),
    )

    capital_account_step_id = db.Column(db.BigInteger, primary_key=True)
    capital_account_step_item_no = db.Column(db.String(64), nullable=False, index=True, server_default=db.FetchedValue(), info='资产编号')
    capital_account_step_account_id = db.Column(db.BigInteger, nullable=False, info='capital_account表id')
    capital_account_step_user_key = db.Column(db.String(50), index=True, info='步骤成功唯一标识')
    capital_account_step_status = db.Column(db.Integer, info='状态(0:成功,1:失败,2:处理中,4:未处理)')
    capital_account_step_step = db.Column(db.String(50), info='步骤')
    capital_account_step_way = db.Column(db.String(32), nullable=False, server_default=db.FetchedValue(), info='主体')
    capital_account_step_serial_no = db.Column(db.String(255), info='流水号')
    capital_account_step_retry_times = db.Column(db.Integer, server_default=db.FetchedValue(), info='请求次数')
    capital_account_step_memo = db.Column(db.String(256), server_default=db.FetchedValue(), info='备注信息')
    capital_account_step_create_at = db.Column(db.DateTime, server_default=db.FetchedValue(), info='创建时间')
    capital_account_step_update_at = db.Column(db.DateTime, server_default=db.FetchedValue(), info='修改时间')



class CapitalAsset(db.Model, BaseToDict):
    __tablename__ = 'capital_asset'
    __table_args__ = (
        db.Index('idx_capital_asset_item_no_channel', 'capital_asset_item_no', 'capital_asset_channel'),
    )

    capital_asset_id = db.Column(db.BigInteger, primary_key=True)
    capital_asset_item_no = db.Column(db.String(48), nullable=False, server_default=db.FetchedValue(), info='资产编号')
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
    capital_asset_finish_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='偿清时间')
    capital_asset_version = db.Column(db.SmallInteger, nullable=False, server_default=db.FetchedValue(), info='版本号')



class CapitalBlacklist(db.Model, BaseToDict):
    __tablename__ = 'capital_blacklist'

    capital_blacklist_id = db.Column(db.BigInteger, primary_key=True)
    capital_blacklist_value = db.Column(db.String(32), nullable=False, index=True, info='黑名单')
    capital_blacklist_type = db.Column(db.Enum('id_card', 'bank_card'), nullable=False, info='黑名单类型(id_card:身份证,bank_card:银行卡账号)')
    capital_blacklist_channel = db.Column(db.String(50), nullable=False, info='资金方')
    capital_blacklist_reason = db.Column(db.String(256), info='列入黑名单原因')
    capital_blacklist_create_at = db.Column(db.DateTime, nullable=False, index=True, server_default=db.FetchedValue())
    capital_blacklist_update_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())
    capital_blacklist_expired_at = db.Column(db.DateTime, nullable=False, index=True, server_default=db.FetchedValue(), info='过期时间')



class CapitalTransaction(db.Model, BaseToDict):
    __tablename__ = 'capital_transaction'
    __table_args__ = (
        db.Index('uqidx_capital_transaction_asset_id_period_period_type', 'capital_transaction_asset_id', 'capital_transaction_period', 'capital_transaction_type'),
    )

    capital_transaction_id = db.Column(db.BigInteger, primary_key=True)
    capital_transaction_item_no = db.Column(db.String(48), nullable=False, index=True, server_default=db.FetchedValue(), info='资产编号')
    capital_transaction_asset_id = db.Column(db.BigInteger, server_default=db.FetchedValue(), info='capital_asset表主键ID')
    capital_transaction_period = db.Column(db.SmallInteger, nullable=False, server_default=db.FetchedValue(), info='期数')
    capital_transaction_period_term = db.Column(db.SmallInteger, nullable=False, server_default=db.FetchedValue(), info='该期周期长度')
    capital_transaction_period_type = db.Column(db.Enum('day', 'month'), nullable=False, server_default=db.FetchedValue(), info='该期周期单位')
    capital_transaction_type = db.Column(db.String(50), nullable=False, server_default=db.FetchedValue(), info='例如：principal 本金, interest 利息, factoring 保理, service 平台服务费, interest_subsidy 贴息,service_subsidy 贴补服务费,guarantee_service 担保服务费,guarantee 担保金')
    capital_transaction_amount = db.Column(db.BigInteger, nullable=False, server_default=db.FetchedValue(), info='金额')
    capital_transaction_rate = db.Column(db.Numeric(10, 8), nullable=False, server_default=db.FetchedValue(), info='费率/利率')
    capital_transaction_expect_finished_at = db.Column(db.DateTime, nullable=False, index=True, server_default=db.FetchedValue(), info='预计完成时间')
    capital_transaction_repayment_type = db.Column(db.Enum('acpi', 'averagecapital', 'rtlataio'), nullable=False, server_default=db.FetchedValue(), info='还款类型:acpi-等额本息;averagecapital-等额本金;rtlataio-到期一次性还本付息')
    capital_transaction_create_at = db.Column(db.DateTime, nullable=False, index=True, server_default=db.FetchedValue(), info='创建时间')
    capital_transaction_update_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='更新时间')
    capital_transaction_origin_amount = db.Column(db.BigInteger, nullable=False, server_default=db.FetchedValue(), info='原始金额')
    capital_transaction_user_repay_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='用户提前或正常还款未走资方通道而走我方通道的还款时间')
    capital_transaction_user_repay_channel = db.Column(db.String(50), nullable=False, server_default=db.FetchedValue(), info='代扣渠道 我方通道qsq')
    capital_transaction_actual_finished_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='实际还资方时间')
    capital_transaction_operate_type = db.Column(db.Enum('grant', 'advance', 'normal', 'compensate', 'buyback'), nullable=False, server_default=db.FetchedValue(), info='grant-放款，advance-用户提前还款并且未回购，normal-用户到期日还款并且未回购，compensate-逾期由我方刚兑之后，buyback-回购')



class CapitalWithdraw(db.Model, BaseToDict):
    __tablename__ = 'capital_withdraw'
    __table_args__ = (
        db.Index('idx_capital_withdraw_channel_key', 'capital_withdraw_channel_key', 'capital_withdraw_channel'),
    )

    capital_withdraw_id = db.Column(db.Integer, primary_key=True, info='主键')
    capital_withdraw_channel_key = db.Column(db.String(45), nullable=False, server_default=db.FetchedValue(), info='资金方提现请求流水（和提现回调流水一致）')
    capital_withdraw_item_no = db.Column(db.String(32), nullable=False, index=True, info='资产编号')
    capital_withdraw_idnum = db.Column(db.String(45), nullable=False, info='身份证号码')
    capital_withdraw_card_number = db.Column(db.String(45), info='账户号')
    capital_withdraw_amount = db.Column(db.BigInteger, nullable=False, info='金额(分)')
    capital_withdraw_channel = db.Column(db.String(50), nullable=False, info='资金方渠道')
    capital_withdraw_status = db.Column(db.Enum('ready', 'process', 'success', 'fail'), nullable=False, server_default=db.FetchedValue(), info='状态')
    capital_withdraw_request_data = db.Column(db.Text, nullable=False, info='请求数据')
    capital_withdraw_response_data = db.Column(db.Text, info='响应数据')
    capital_withdraw_create_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='创建时间')
    capital_withdraw_update_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='更新时间')
    capital_withdraw_finish_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='完成时间')
    capital_withdraw_memo = db.Column(db.Text, info='备注')



class CircuitBreakAction(db.Model, BaseToDict):
    __tablename__ = 'circuit_break_action'

    circuit_break_action_id = db.Column(db.BigInteger, primary_key=True, info='主键')
    circuit_break_action_circuit_break_id = db.Column(db.BigInteger, nullable=False, info='熔断记录id')
    circuit_break_action_memo = db.Column(db.String(200), nullable=False, info='备注')
    circuit_break_action_status = db.Column(db.String(20), nullable=False, info='action 状态:unfinished/finished')
    circuit_break_action_type = db.Column(db.String(30), nullable=False, info='action类型')
    circuit_break_action_data = db.Column(db.String(1000), info='挂起条件/告警内容')
    circuit_break_action_create_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='创建时间')
    circuit_break_action_update_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='更新时间')



class CircuitBreakRecord(db.Model, BaseToDict):
    __tablename__ = 'circuit_break_record'

    circuit_break_record_id = db.Column(db.BigInteger, primary_key=True, info='主键')
    circuit_break_record_name = db.Column(db.String(50), nullable=False, info='熔断场景名称')
    circuit_break_record_status = db.Column(db.String(10), nullable=False, info='熔断状态')
    circuit_break_record_trigger_rule = db.Column(db.String(1000), nullable=False, info='熔断触发条件')
    circuit_break_record_create_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='创建时间')
    circuit_break_record_update_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='更新时间')



class GnodeLog(db.Model, BaseToDict):
    __tablename__ = 'gnode_log'
    __table_args__ = (
        db.Index('idx_log_itemno_channel', 'gnode_log_asset_item_no', 'gnode_log_channel'),
        db.Index('idx_gnode_log_node_status', 'gnode_log_node', 'gnode_log_status')
    )

    gnode_log_id = db.Column(db.Integer, primary_key=True, info='自增主键')
    gnode_log_category = db.Column(db.String(32), nullable=False, info='日志分类')
    gnode_log_channel = db.Column(db.String(32), nullable=False, info='资金方编码')
    gnode_log_seq = db.Column(db.String(64), nullable=False, index=True, server_default=db.FetchedValue(), info='日志编码')
    gnode_log_asset_item_no = db.Column(db.String(48), nullable=False, info='资产编码')
    gnode_log_type = db.Column(db.String(32), nullable=False, info='节点日志类型:ACTION/EVENT')
    gnode_log_node = db.Column(db.String(128), nullable=False, info='日志节点')
    gnode_log_desc = db.Column(db.String(128), nullable=False, server_default=db.FetchedValue(), info='日志节点描述')
    gnode_log_status = db.Column(db.Enum('new', 'ready', 'done', 'archived', 'deleted'), nullable=False, server_default=db.FetchedValue(), info='节点数据状态')
    gnode_log_result = db.Column(db.String(128), nullable=False, server_default=db.FetchedValue(), info='事件结果')
    gnode_log_fired_at = db.Column(db.DateTime, nullable=False, index=True, server_default=db.FetchedValue(), info='发生时间')
    gnode_log_update_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='更新时间')
    gnode_log_create_at = db.Column(db.DateTime, nullable=False, index=True, server_default=db.FetchedValue(), info='创建时间')



class Individual(db.Model, BaseToDict):
    __tablename__ = 'individual'

    individual_id = db.Column(db.Integer, primary_key=True)
    individual_id_type = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), info='身份类型(0-未知,1-在职,2-在读,3-待业)')
    individual_credit_type = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), info='信用类型(0-未知,1-芝麻分,2-万象分,3-考拉分,4-星辰分,5-京东分,\\n6-腾讯分)')
    individual_credit_score = db.Column(db.Integer, server_default=db.FetchedValue(), info='信用分数')
    individual_create_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())
    individual_update_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())
    individual_name_encrypt = db.Column(db.String(128), nullable=False, index=True, server_default=db.FetchedValue(), info='姓名加密')
    individual_idnum_encrypt = db.Column(db.String(128), nullable=False, index=True, server_default=db.FetchedValue(), info='身份证号码加密')



class RouterCapitalPlan(db.Model, BaseToDict):
    __tablename__ = 'router_capital_plan'
    __table_args__ = (
        db.Index('router_capital_plan_rule_code_day_unique_index', 'router_capital_plan_label', 'router_capital_plan_date'),
    )

    router_capital_plan_id = db.Column(db.Integer, primary_key=True, info='自增id')
    router_capital_plan_date = db.Column(db.Date, nullable=False, server_default=db.FetchedValue(), info='资金计划日期')
    router_capital_plan_label = db.Column(db.String(64), nullable=False, server_default=db.FetchedValue(), info='资金规则编码 即router_capital_rule_code')
    router_capital_plan_desc = db.Column(db.String(128), nullable=False, server_default=db.FetchedValue(), info='资金计划描述')
    router_capital_plan_amount = db.Column(db.BigInteger, nullable=False, server_default=db.FetchedValue(), info='资金量（单位：分）')
    router_capital_plan_update_memo = db.Column(db.Text, info='更新备注')
    router_capital_plan_create_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='创建时间')
    router_capital_plan_update_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='更新时间')



class RouterCapitalRule(db.Model, BaseToDict):
    __tablename__ = 'router_capital_rule'

    router_capital_rule_id = db.Column(db.Integer, primary_key=True, info='自增id')
    router_capital_rule_code = db.Column(db.String(64), nullable=False, index=True, server_default=db.FetchedValue(), info='规则编码(唯一)')
    router_capital_rule_desc = db.Column(db.String(128), nullable=False, server_default=db.FetchedValue(), info='规则描述')
    router_capital_rule_family = db.Column(db.String(64), nullable=False, server_default=db.FetchedValue(), info='规则分组')
    router_capital_rule_type = db.Column(db.String(32), nullable=False, server_default=db.FetchedValue(), info='规则分类 例如demand,supply')
    router_capital_rule_limit_type = db.Column(db.String(32), nullable=False, server_default=db.FetchedValue(), info='控量类型 strict - 严格控量; nonstrict - 非严格控量')
    router_capital_rule_weight = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), info='规则权重')
    router_capital_rule_allow_overflow_rate = db.Column(db.Numeric(10, 2), nullable=False, server_default=db.FetchedValue(), info='允许路由/进件溢出率')
    router_capital_rule_content = db.Column(db.Text, info='规则内容（JSON字符串）')
    router_capital_rule_status = db.Column(db.Enum('draft', 'release', 'discard'), nullable=False, server_default=db.FetchedValue(), info='规则状态')
    router_capital_rule_create_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='创建时间')
    router_capital_rule_update_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='更新时间')
    router_capital_rule_sort = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), info='规则排序号')


class RouterLoadRecord(db.Model, BaseToDict):
    __tablename__ = 'router_load_record'
    __table_args__ = (
        db.Index('Idx_router_load_record_day_channel_status', 'router_load_record_route_day', 'router_load_record_channel', 'router_load_record_status'),
        db.Index('idx_router_load_record_item_no', 'router_load_record_item_no', 'router_load_record_channel'),
        db.Index('idx_router_load_record_key_channel', 'router_load_record_key', 'router_load_record_channel')
    )

    router_load_record_id = db.Column(db.Integer, primary_key=True, info='主键')
    router_load_record_key = db.Column(db.String(64, 'utf8_bin'), nullable=False, server_default=db.FetchedValue(), info='路由请求唯一标识')
    router_load_record_item_no = db.Column(db.String(48, 'utf8_bin'), nullable=False, server_default=db.FetchedValue(), info='资产编号')
    router_load_record_rule_code = db.Column(db.String(64, 'utf8_bin'), nullable=False, server_default=db.FetchedValue(), info='资金规则编码')
    router_load_record_principal_amount = db.Column(db.BigInteger, nullable=False, server_default=db.FetchedValue(), info='路由金额')
    router_load_record_status = db.Column(db.String(20, 'utf8_bin'), nullable=False, server_default=db.FetchedValue(), info='路由状态：routed-路由，imported-导入，applied-进件到资方，changed-已切资方')
    router_load_record_channel = db.Column(db.String(32, 'utf8_bin'), server_default=db.FetchedValue(), info='资方渠道')
    router_load_record_sub_type = db.Column(db.String(50, 'utf8_bin'), nullable=False, server_default=db.FetchedValue(), info='资产子类型, single | multiple')
    router_load_record_period_count = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), info='资产类型数量')
    router_load_record_period_type = db.Column(db.String(50, 'utf8_bin'), nullable=False, server_default=db.FetchedValue(), info='资产周期类型, month | day')
    router_load_record_period_days = db.Column(db.Integer, server_default=db.FetchedValue(), info='资产周期天数')
    router_load_record_sub_order_type = db.Column(db.String(50, 'utf8_bin'), nullable=False, server_default=db.FetchedValue(), info='子订单类型')
    router_load_record_route_day = db.Column(db.String(10, 'utf8_bin'), nullable=False, server_default=db.FetchedValue(), info='路由日期')
    router_load_record_from_system = db.Column(db.String(50, 'utf8_bin'), nullable=False, server_default=db.FetchedValue(), info='资产来源系统')
    router_load_record_total_record_id = db.Column(db.Integer, info='路由总表记录Id')
    router_load_record_create_at = db.Column(db.DateTime, nullable=False, index=True, server_default=db.FetchedValue(), info='创建日期')
    router_load_record_import_at = db.Column(db.DateTime, nullable=False, index=True, server_default=db.FetchedValue(), info='进件时间')
    router_load_record_update_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='修改时间')
    router_load_record_idnum = db.Column(db.String(32, 'utf8_bin'), index=True, info='身份证号码')



class RouterLoadTotal(db.Model, BaseToDict):
    __tablename__ = 'router_load_total'

    router_load_total_id = db.Column(db.Integer, primary_key=True, info='主键')
    router_load_total_rule_code = db.Column(db.String(64), nullable=False, server_default=db.FetchedValue(), info='资金规则编码')
    router_load_total_count = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), info='路由数量')
    router_load_total_routed_amount = db.Column(db.BigInteger, nullable=False, server_default=db.FetchedValue(), info='路由总金额')
    router_load_total_imported_amount = db.Column(db.BigInteger, nullable=False, server_default=db.FetchedValue(), info='已进件总金额')
    router_load_total_route_day = db.Column(db.String(10), nullable=False, server_default=db.FetchedValue(), info='路由日期')
    router_load_total_refresh_timestamp = db.Column(db.BigInteger, nullable=False, server_default=db.FetchedValue(), info='刷新时间（时间戳）')
    router_load_total_create_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='创建时间')
    router_load_total_update_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='修改时间')



class RouterWeight(db.Model, BaseToDict):
    __tablename__ = 'router_weight'

    router_weight_id = db.Column(db.Integer, primary_key=True, info='自增id')
    router_weight_type = db.Column(db.String(64), nullable=False, server_default=db.FetchedValue(), info='路由结果类型')
    router_weight_code = db.Column(db.String(64), nullable=False, server_default=db.FetchedValue(), info='路由结果编码')
    router_weight_desc = db.Column(db.String(128), nullable=False, info='权重描述')
    router_weight_rule_content = db.Column(db.Text, info='资金规则编码')
    router_weight_value = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), info='权重值')
    router_weight_status = db.Column(db.Enum('active', 'inactive'), nullable=False, server_default=db.FetchedValue(), info='权重状态 active 启用, inactive 不启用')
    router_weight_first_route_status = db.Column(db.Enum('active', 'inactive'), nullable=False, server_default=db.FetchedValue(), info='一次路由启用状态，权重状态 active 启用, inactive 不启用')
    router_weight_second_route_status = db.Column(db.Enum('active', 'inactive'), nullable=False, server_default=db.FetchedValue(), info='二次路由启用状态，权重状态 active 启用, inactive 不启用')
    router_weight_create_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='创建时间')
    router_weight_update_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='更新时间')
    router_weight_create_name = db.Column(db.String(48), nullable=False, server_default=db.FetchedValue(), info='创建人')
    router_weight_update_name = db.Column(db.String(48), nullable=False, server_default=db.FetchedValue(), info='修改人')



class Seed(db.Model, BaseToDict):
    __tablename__ = 'seed'

    seed_type = db.Column(db.String(45), primary_key=True)
    seed_no = db.Column(db.Integer, nullable=False)
    seed_update_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())



class Sendmsg(db.Model, BaseToDict):
    __tablename__ = 'sendmsg'
    __table_args__ = (
        db.Index('Idx_sendmsg_next_run_at_version_priority_status', 'sendmsg_priority', 'sendmsg_status', 'sendmsg_next_run_at', 'sendmsg_version'),
        db.Index('Idx_sendmsg_next_run_at_version_type_status', 'sendmsg_type', 'sendmsg_status', 'sendmsg_next_run_at', 'sendmsg_version')
    )

    sendmsg_id = db.Column(db.Integer, primary_key=True)
    sendmsg_order_no = db.Column(db.String(64), nullable=False, index=True, server_default=db.FetchedValue())
    sendmsg_type = db.Column(db.String(45), nullable=False)
    sendmsg_content = db.Column(db.String, nullable=False)
    sendmsg_memo = db.Column(db.String(2048), nullable=False, server_default=db.FetchedValue())
    sendmsg_tosystem = db.Column(db.String(64), nullable=False, server_default=db.FetchedValue())
    sendmsg_status = db.Column(db.Enum('open', 'running', 'error', 'terminated', 'close'), nullable=False, server_default=db.FetchedValue())
    sendmsg_next_run_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())
    sendmsg_create_at = db.Column(db.DateTime, nullable=False, index=True, server_default=db.FetchedValue())
    sendmsg_update_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())
    sendmsg_version = db.Column(db.SmallInteger, nullable=False, server_default=db.FetchedValue())
    sendmsg_priority = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue())
    sendmsg_retrytimes = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue())
    sendmsg_response_data = db.Column(db.Text)



class Sendsm(db.Model, BaseToDict):
    __tablename__ = 'sendsms'
    __table_args__ = (
        db.Index('idx_sendsms_content_type_create_at', 'sendsms_content_type', 'sendsms_create_at'),
        db.Index('Idx_sendsms_next_run_at_version_type_status', 'sendsms_type', 'sendsms_status', 'sendsms_next_run_at', 'sendsms_version'),
        db.Index('Idx_sendsms_next_run_at_version_priority_status', 'sendsms_priority', 'sendsms_status', 'sendsms_next_run_at', 'sendsms_version')
    )

    sendsms_id = db.Column(db.Integer, primary_key=True)
    sendsms_order_no = db.Column(db.String(64), nullable=False, index=True, server_default=db.FetchedValue())
    sendsms_type = db.Column(db.String(45), nullable=False)
    sendsms_content = db.Column(db.String, nullable=False)
    sendsms_content_type = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), info='短信内容类型: 0 - 普通短信; 1 - 普通告警短信; 2 - 恒丰银行放款账户余额不足告警短信')
    sendsms_memo = db.Column(db.String(2048), nullable=False, server_default=db.FetchedValue())
    sendsms_tosystem = db.Column(db.String(64), nullable=False, server_default=db.FetchedValue())
    sendsms_status = db.Column(db.Enum('open', 'running', 'error', 'terminated', 'close'), nullable=False)
    sendsms_next_run_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())
    sendsms_create_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())
    sendsms_update_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())
    sendsms_version = db.Column(db.SmallInteger, nullable=False, server_default=db.FetchedValue())
    sendsms_priority = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue())
    sendsms_retrytimes = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue())



class Synctask(db.Model, BaseToDict):
    __tablename__ = 'synctask'
    __table_args__ = (
        db.Index('idx_synctask_key_type_sys', 'synctask_key', 'synctask_type', 'synctask_from_system'),
    )

    synctask_id = db.Column(db.Integer, primary_key=True)
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



class Task(db.Model, BaseToDict):
    __tablename__ = 'task'
    __table_args__ = (
        db.Index('Idx_taskrun_at_status_priority', 'task_status', 'task_priority', 'task_next_run_at'),
    )

    task_id = db.Column(db.Integer, primary_key=True)
    task_order_no = db.Column(db.String(64), nullable=False, index=True, server_default=db.FetchedValue())
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



class Withdraw(db.Model, BaseToDict):
    __tablename__ = 'withdraw'

    withdraw_id = db.Column(db.Integer, primary_key=True, info='主键')
    withdraw_merchant_id = db.Column(db.Integer, nullable=False, info='商户编号')
    withdraw_merchant_key = db.Column(db.String(64), nullable=False, unique=True, info='商户订单号')
    withdraw_account = db.Column(db.String(32), nullable=False, info='出款帐号')
    withdraw_amount = db.Column(db.BigInteger, nullable=False, info='金额(分)')
    withdraw_reason = db.Column(db.String(128), nullable=False, info='代付用途')
    withdraw_receiver_type = db.Column(db.Integer, nullable=False, info='收款账户类型(1=对私 2=对公)')
    withdraw_receiver_bankcode = db.Column(db.String(16), nullable=False, info='收款银行缩写')
    withdraw_receiver_bank_branch = db.Column(db.String(128), nullable=False, server_default=db.FetchedValue(), info='收款分行名称')
    withdraw_receiver_bank_subbranch = db.Column(db.String(128), nullable=False, server_default=db.FetchedValue(), info='收款支行名称')
    withdraw_receiver_bank_province = db.Column(db.String(64), nullable=False, server_default=db.FetchedValue(), info='收款分行省份')
    withdraw_receiver_bank_city = db.Column(db.String(64), nullable=False, server_default=db.FetchedValue(), info='收款分行城市')
    withdraw_channel = db.Column(db.String(50), nullable=False, info='代付渠道')
    withdraw_status = db.Column(db.Enum('ready', 'process', 'success', 'fail'), nullable=False, server_default=db.FetchedValue(), info='状态')
    withdraw_type = db.Column(db.String(50), nullable=False, info='类型')
    withdraw_comment = db.Column(db.String(255), nullable=False, server_default=db.FetchedValue(), info='备注')
    withdraw_request_data = db.Column(db.Text, nullable=False, info='请求数据')
    withdraw_response_data = db.Column(db.Text, info='响应数据')
    withdraw_create_at = db.Column(db.DateTime, nullable=False, index=True, server_default=db.FetchedValue(), info='创建时间')
    withdraw_update_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='更新时间')
    withdraw_finish_at = db.Column(db.DateTime, nullable=False, index=True, server_default=db.FetchedValue(), info='完成时间')
    withdraw_asset_item_no = db.Column(db.String(48), nullable=False, index=True, server_default=db.FetchedValue(), info='资产编号')
    withdraw_channel_key = db.Column(db.String(32), info='通道交易流水编号')
    withdraw_version = db.Column(db.String(10))
    withdraw_receiver_name_encrypt = db.Column(db.String(128), nullable=False, server_default=db.FetchedValue(), info='收款账户名称加密')
    withdraw_receiver_account_encrypt = db.Column(db.String(128), nullable=False, index=True, server_default=db.FetchedValue(), info='收款账号加密')
    withdraw_receiver_identity_encrypt = db.Column(db.String(128), nullable=False, index=True, server_default=db.FetchedValue(), info='收款人证件号(对私 - 身份证, 对公 - 组织机构代码证/企业信用代码)加密')



class WithdrawOrder(db.Model, BaseToDict):
    __tablename__ = 'withdraw_order'
    __table_args__ = (
        db.Index('idx_withdraw_item_no_loan_channel_type_cardnum', 'withdraw_order_asset_item_no', 'withdraw_order_asset_loan_channel', 'withdraw_order_type', 'withdraw_order_receiver_cardnum_encrypt'),
    )

    withdraw_order_id = db.Column(db.Integer, primary_key=True, info='主键')
    withdraw_order_no = db.Column(db.String(64), nullable=False, unique=True, info='商户订单号')
    withdraw_order_asset_item_no = db.Column(db.String(48), nullable=False, server_default=db.FetchedValue(), info='资产编号')
    withdraw_order_asset_loan_channel = db.Column(db.String(48), nullable=False, server_default=db.FetchedValue(), info='资产渠道')
    withdraw_order_amount = db.Column(db.BigInteger, nullable=False, info='金额(分)')
    withdraw_order_reason = db.Column(db.String(128), nullable=False, info='代付用途')
    withdraw_order_status = db.Column(db.Enum('ready', 'process', 'success', 'fail'), nullable=False, server_default=db.FetchedValue(), info='状态')
    withdraw_order_type = db.Column(db.String(50), nullable=False, info='类型')
    withdraw_order_payment_subject_key = db.Column(db.String(40), nullable=False, server_default=db.FetchedValue(), info='支付主体key')
    withdraw_order_receiver_cardnum_encrypt = db.Column(db.String(64), nullable=False, index=True, server_default=db.FetchedValue(), info='收款卡密文')
    withdraw_order_receiver_idnum_encrypt = db.Column(db.String(64), nullable=False, index=True, server_default=db.FetchedValue(), info='收款人身份证密文')
    withdraw_order_receiver_mobile_encrypt = db.Column(db.String(64), nullable=False, server_default=db.FetchedValue(), info='收款卡预留手机号密文')
    withdraw_order_receiver_name_encrypt = db.Column(db.String(64), nullable=False, server_default=db.FetchedValue(), info='收款人姓名密文')
    withdraw_order_create_at = db.Column(db.DateTime, nullable=False, index=True, server_default=db.FetchedValue(), info='创建时间')
    withdraw_order_update_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='更新时间')
    withdraw_order_finish_at = db.Column(db.DateTime, nullable=False, index=True, server_default=db.FetchedValue(), info='完成时间')
    withdraw_order_resp_code = db.Column(db.String(64), nullable=False, server_default=db.FetchedValue(), info='代付响应码')
    withdraw_order_resp_message = db.Column(db.String(255), nullable=False, server_default=db.FetchedValue(), info='代付响应信息')
    withdraw_order_withdraw_type = db.Column(db.String(10), info='收款方式： online - 线上收款， offline - 线下收款')
    withdraw_order_extend_info = db.Column(db.String(1024), info='扩展信息')



class WithdrawRecord(db.Model, BaseToDict):
    __tablename__ = 'withdraw_record'

    withdraw_record_id = db.Column(db.Integer, primary_key=True, info='主键')
    withdraw_record_order_no = db.Column(db.String(64), nullable=False, index=True, info='商户订单号')
    withdraw_record_trade_no = db.Column(db.String(64), nullable=False, unique=True, info='商户流水号')
    withdraw_record_channel = db.Column(db.String(50), nullable=False, server_default=db.FetchedValue(), info='代付渠道')
    withdraw_record_status = db.Column(db.Enum('ready', 'process', 'success', 'fail', 'void'), nullable=False, server_default=db.FetchedValue(), info='状态')
    withdraw_record_resp_code = db.Column(db.String(2555), nullable=False, server_default=db.FetchedValue(), info='代付响应码')
    withdraw_record_resp_message = db.Column(db.String(2555), nullable=False, server_default=db.FetchedValue(), info='代付响应信息')
    withdraw_record_finish_at = db.Column(db.DateTime, nullable=False, index=True, server_default=db.FetchedValue(), info='完成时间')
    withdraw_record_channel_key = db.Column(db.String(32), index=True, info='通道交易流水编号')
    withdraw_record_create_at = db.Column(db.DateTime, nullable=False, index=True, server_default=db.FetchedValue(), info='创建时间')
    withdraw_record_update_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='更新时间')
    withdraw_record_withdraw_code = db.Column(db.String(50), info='线下收款时的取款码')



class WithdrawTransfer(db.Model, BaseToDict):
    __tablename__ = 'withdraw_transfer'

    withdraw_transfer_id = db.Column(db.Integer, primary_key=True, info='自增id')
    withdraw_transfer_asset_item_no = db.Column(db.String(48), nullable=False, index=True, server_default=db.FetchedValue(), info='资产编号')
    withdraw_transfer_serial_no = db.Column(db.String(64), nullable=False, index=True, server_default=db.FetchedValue(), info='转账流水号')
    withdraw_transfer_channel = db.Column(db.String(32), nullable=False, server_default=db.FetchedValue(), info='资金方')
    withdraw_transfer_in_account = db.Column(db.String(32), nullable=False, server_default=db.FetchedValue(), info='转入方账户')
    withdraw_transfer_out_account = db.Column(db.String(32), nullable=False, server_default=db.FetchedValue(), info='转出方账户')
    withdraw_transfer_amount = db.Column(db.BigInteger, nullable=False, info='转账金额')
    withdraw_transfer_status = db.Column(db.Enum('process', 'success', 'fail'), nullable=False, server_default=db.FetchedValue(), info='process-转账处理中 success-转账成功 fail-转账失败')
    withdraw_transfer_create_at = db.Column(db.DateTime, nullable=False, index=True, server_default=db.FetchedValue(), info='创建时间')
    withdraw_transfer_update_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='更新时间')
    withdraw_transfer_finish_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='完成时间')
    withdraw_transfer_memo = db.Column(db.String(255), server_default=db.FetchedValue(), info='备注')
