# coding: utf-8
from flask_sqlalchemy import SQLAlchemy
from app.common.db_util import BaseToDict

db = SQLAlchemy()



class Company(db.Model, BaseToDict):
    __tablename__ = 'company'

    company_id = db.Column(db.Integer, primary_key=True, info='主键')
    company_type = db.Column(db.String(64), nullable=False, info='类别')
    company_sign = db.Column(db.String(64), nullable=False, index=True, info='签章名称')
    company_name = db.Column(db.String(64), nullable=False, index=True, info='简称(云智等)')
    company_full_name = db.Column(db.String(64), nullable=False, server_default=db.FetchedValue(), info='公司全称')
    company_platform = db.Column(db.String(64), nullable=False, server_default=db.FetchedValue(), info='所属平台别名')
    company_platform_name = db.Column(db.String(64), nullable=False, server_default=db.FetchedValue(), info='所属平台名称')
    company_platform_subject = db.Column(db.String(64), nullable=False, server_default=db.FetchedValue(), info='所属平台运营主体简称(云智等)')
    company_create_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())
    company_update_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())



class Contract(db.Model, BaseToDict):
    __tablename__ = 'contract'
    __table_args__ = (
        db.Index('idx_contract_asset_item_no_contract_type', 'contract_asset_item_no', 'contract_type'),
    )

    contract_id = db.Column(db.Integer, primary_key=True)
    contract_create_at = db.Column(db.DateTime, nullable=False, index=True, server_default=db.FetchedValue(), info='创建时间')
    contract_asset_item_no = db.Column(db.String(48), nullable=False, server_default=db.FetchedValue(), info='资产编号')
    contract_type = db.Column(db.Integer, nullable=False)
    contract_status = db.Column(db.Enum('VOID', 'SUCCESS', 'SIGN_APPLY'), nullable=False, server_default=db.FetchedValue(), info='状态：SIGN_APPLY-签约中，SUCCESS-签约成功')
    contract_type_text = db.Column(db.String(255), nullable=False, server_default=db.FetchedValue())
    contract_url = db.Column(db.String(1000), nullable=False, server_default=db.FetchedValue())
    contract_from_system = db.Column(db.String(24), nullable=False, server_default=db.FetchedValue(), info='合同来源系统')
    contract_code = db.Column(db.String(25), nullable=False, server_default=db.FetchedValue(), info='合同编号')
    contract_apply_id = db.Column(db.String(64), nullable=False, server_default=db.FetchedValue(), info='申请签约ID')
    contract_flow_key = db.Column(db.String(64), nullable=False, server_default=db.FetchedValue(), info='签约系统流程key')
    contract_ref_item_no = db.Column(db.String(48), nullable=False, index=True, server_default=db.FetchedValue(), info='关联资产编号')
    contract_sign_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info=' 合同签约时间')
    contract_update_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='更新时间')
    contract_sign_opportunity = db.Column(db.String(32), nullable=False, server_default=db.FetchedValue(), info='签约时机（AssetImport-资产生成时, AssetWithdrawSuccess-放款到卡成功时,AssetReorganized-展期时,BeforeImport-进件前签约,PayoffAsset-结清时,Diversion-导流时,BeforeRegister-开户前，BeforeApply-进件资方前,AfterApplySuccess-进件资方成功，BindSuccess-绑卡成功,FoxContractSign-贷后法催协议签署')
    contract_provider = db.Column(db.String(48), nullable=False, server_default=db.FetchedValue(), info='合同签约商')
    contract_subject = db.Column(db.String(48), nullable=False, server_default=db.FetchedValue(), info='公司主体')
    contract_channel = db.Column(db.String(32), nullable=False, server_default=db.FetchedValue(), info='放款渠道')
    contract_version = db.Column(db.SmallInteger, nullable=False, server_default=db.FetchedValue(), info='合同配置版本')



class Contract2021(db.Model, BaseToDict):
    __tablename__ = 'contract_2021'
    __table_args__ = (
        db.Index('idx_contract_asset_item_no_contract_type', 'contract_asset_item_no', 'contract_type'),
    )

    contract_id = db.Column(db.Integer, primary_key=True)
    contract_asset_item_no = db.Column(db.String(48), nullable=False, server_default=db.FetchedValue(), info='资产编号')
    contract_type = db.Column(db.Integer, nullable=False)
    contract_type_text = db.Column(db.String(255), nullable=False, server_default=db.FetchedValue())
    contract_url = db.Column(db.String(1000), nullable=False, server_default=db.FetchedValue())
    contract_status = db.Column(db.Enum('VOID', 'SUCCESS', 'SIGN_APPLY'), nullable=False, server_default=db.FetchedValue(), info='状态：SIGN_APPLY-签约中，SUCCESS-签约成功')
    contract_from_system = db.Column(db.String(24), nullable=False, server_default=db.FetchedValue(), info='合同来源系统')
    contract_code = db.Column(db.String(25), nullable=False, server_default=db.FetchedValue(), info='合同编号')
    contract_apply_id = db.Column(db.String(64), nullable=False, server_default=db.FetchedValue(), info='申请签约ID')
    contract_flow_key = db.Column(db.String(64), nullable=False, server_default=db.FetchedValue(), info='签约系统流程key')
    contract_create_at = db.Column(db.DateTime, nullable=False, index=True, server_default=db.FetchedValue())
    contract_sign_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info=' 合同签约时间')
    contract_update_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='更新时间')
    contract_ref_item_no = db.Column(db.String(48), nullable=False, index=True, server_default=db.FetchedValue(), info='关联资产编号')
    contract_sign_opportunity = db.Column(db.String(32), nullable=False, server_default=db.FetchedValue(), info='签约时机（AssetImport-资产生成时, AssetWithdrawSuccess-放款到卡成功时,AssetReorganized-展期时,BeforeImport-进件前签约,PayoffAsset-结清时,Diversion-导流时,BeforeRegister-开户前，BeforeApply-进件资方前,ContractDownload-进件资方成功，BindSuccess-绑卡成功,FoxContractSign-贷后法催协议签署')
    contract_provider = db.Column(db.String(48), nullable=False, server_default=db.FetchedValue(), info='合同签约商')
    contract_subject = db.Column(db.String(48), nullable=False, server_default=db.FetchedValue(), info='公司主体')
    contract_channel = db.Column(db.String(32), nullable=False, server_default=db.FetchedValue(), info='放款渠道')
    contract_version = db.Column(db.SmallInteger, nullable=False, server_default=db.FetchedValue(), info='合同配置版本')



class Contract2022(db.Model, BaseToDict):
    __tablename__ = 'contract_2022'
    __table_args__ = (
        db.Index('idx_contract_asset_item_no_contract_type', 'contract_asset_item_no', 'contract_type'),
    )

    contract_id = db.Column(db.Integer, primary_key=True)
    contract_asset_item_no = db.Column(db.String(48), nullable=False, server_default=db.FetchedValue(), info='资产编号')
    contract_type = db.Column(db.Integer, nullable=False)
    contract_type_text = db.Column(db.String(255), nullable=False, server_default=db.FetchedValue())
    contract_url = db.Column(db.String(1000), nullable=False, server_default=db.FetchedValue())
    contract_status = db.Column(db.Enum('VOID', 'SUCCESS', 'SIGN_APPLY'), nullable=False, server_default=db.FetchedValue(), info='状态：SIGN_APPLY-签约中，SUCCESS-签约成功')
    contract_from_system = db.Column(db.String(24), nullable=False, server_default=db.FetchedValue(), info='合同来源系统')
    contract_code = db.Column(db.String(25), nullable=False, server_default=db.FetchedValue(), info='合同编号')
    contract_apply_id = db.Column(db.String(64), nullable=False, server_default=db.FetchedValue(), info='申请签约ID')
    contract_flow_key = db.Column(db.String(64), nullable=False, server_default=db.FetchedValue(), info='签约系统流程key')
    contract_create_at = db.Column(db.DateTime, nullable=False, index=True, server_default=db.FetchedValue())
    contract_sign_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info=' 合同签约时间')
    contract_update_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='更新时间')
    contract_ref_item_no = db.Column(db.String(48), nullable=False, index=True, server_default=db.FetchedValue(), info='关联资产编号')
    contract_sign_opportunity = db.Column(db.String(32), nullable=False, server_default=db.FetchedValue(), info='签约时机（AssetImport-资产生成时, AssetWithdrawSuccess-放款到卡成功时,AssetReorganized-展期时,BeforeImport-进件前签约,PayoffAsset-结清时,Diversion-导流时,BeforeRegister-开户前，BeforeApply-进件资方前,ContractDownload-进件资方成功，BindSuccess-绑卡成功,FoxContractSign-贷后法催协议签署')
    contract_provider = db.Column(db.String(48), nullable=False, server_default=db.FetchedValue(), info='合同签约商')
    contract_subject = db.Column(db.String(48), nullable=False, server_default=db.FetchedValue(), info='公司主体')
    contract_channel = db.Column(db.String(32), nullable=False, server_default=db.FetchedValue(), info='放款渠道')
    contract_version = db.Column(db.SmallInteger, nullable=False, server_default=db.FetchedValue(), info='合同配置版本')



class Contract2023(db.Model, BaseToDict):
    __tablename__ = 'contract_2023'
    __table_args__ = (
        db.Index('idx_contract_asset_item_no_contract_type', 'contract_asset_item_no', 'contract_type'),
    )

    contract_id = db.Column(db.Integer, primary_key=True)
    contract_asset_item_no = db.Column(db.String(48), nullable=False, server_default=db.FetchedValue(), info='资产编号')
    contract_type = db.Column(db.Integer, nullable=False)
    contract_type_text = db.Column(db.String(255), nullable=False, server_default=db.FetchedValue())
    contract_url = db.Column(db.String(1000), nullable=False, server_default=db.FetchedValue())
    contract_status = db.Column(db.Enum('VOID', 'SUCCESS', 'SIGN_APPLY'), nullable=False, server_default=db.FetchedValue(), info='状态：SIGN_APPLY-签约中，SUCCESS-签约成功')
    contract_from_system = db.Column(db.String(24), nullable=False, server_default=db.FetchedValue(), info='合同来源系统')
    contract_code = db.Column(db.String(25), nullable=False, server_default=db.FetchedValue(), info='合同编号')
    contract_apply_id = db.Column(db.String(64), nullable=False, server_default=db.FetchedValue(), info='申请签约ID')
    contract_flow_key = db.Column(db.String(64), nullable=False, server_default=db.FetchedValue(), info='签约系统流程key')
    contract_create_at = db.Column(db.DateTime, nullable=False, index=True, server_default=db.FetchedValue())
    contract_sign_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info=' 合同签约时间')
    contract_update_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='更新时间')
    contract_ref_item_no = db.Column(db.String(48), nullable=False, index=True, server_default=db.FetchedValue(), info='关联资产编号')
    contract_sign_opportunity = db.Column(db.String(32), nullable=False, server_default=db.FetchedValue(), info='签约时机（AssetImport-资产生成时, AssetWithdrawSuccess-放款到卡成功时,AssetReorganized-展期时,BeforeImport-进件前签约,PayoffAsset-结清时,Diversion-导流时,BeforeRegister-开户前，BeforeApply-进件资方前,ContractDownload-进件资方成功，BindSuccess-绑卡成功,FoxContractSign-贷后法催协议签署')
    contract_provider = db.Column(db.String(48), nullable=False, server_default=db.FetchedValue(), info='合同签约商')
    contract_subject = db.Column(db.String(48), nullable=False, server_default=db.FetchedValue(), info='公司主体')
    contract_channel = db.Column(db.String(32), nullable=False, server_default=db.FetchedValue(), info='放款渠道')
    contract_version = db.Column(db.SmallInteger, nullable=False, server_default=db.FetchedValue(), info='合同配置版本')



class ContractBind(db.Model, BaseToDict):
    __tablename__ = 'contract_bind'

    contract_bind_id = db.Column(db.Integer, primary_key=True, info='主键')
    contract_bind_config_id = db.Column(db.Integer, nullable=False, info='合同配置ID')
    contract_bind_type = db.Column(db.Integer, nullable=False, index=True, info='合同类型编码')
    contract_bind_rule = db.Column(db.String(1024), nullable=False, server_default=db.FetchedValue(), info='合同绑定条件（SpEl）')
    contract_bind_sign_type = db.Column(db.String(32), nullable=False, server_default=db.FetchedValue(), info='签约方式（OUR_SIGN-仅需我方签约,BOTH_SIGN-我方和资方双方都需要签约, CAPITAL_DOWN-资方下载, IMPORT-其他系统导入, NO_SIGN-无签章）')
    contract_bind_sign_opportunity = db.Column(db.String(32), nullable=False, server_default=db.FetchedValue(), info='签约时机（AssetImport-资产生成时, AssetWithdrawSuccess-放款到卡成功时,AssetReorganized-展期时,BeforeImport-进件前签约,PayoffAsset-结清时,Diversion-导流时,BeforeRegister-开户前,BeforeApply-进件资方前,BindSuccess-绑卡成功,FoxContractSign-贷后法催协议签署')
    contract_bind_create_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())
    contract_bind_update_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())
    contract_bind_valid_start_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='配置有效期起始时间')
    contract_bind_valid_end_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='配置有效期终止时间')
    contract_bind_config_version = db.Column(db.SmallInteger, nullable=False, info='合同配置版本')



class ContractConfig(db.Model, BaseToDict):
    __tablename__ = 'contract_config'

    contract_config_id = db.Column(db.Integer, primary_key=True, info='主键')
    contract_config_type = db.Column(db.Integer, nullable=False, index=True, info='合同类型编码')
    contract_config_type_text = db.Column(db.String(64), nullable=False, info='合同类型描述')
    contract_config_tmp_key = db.Column(db.String(64), nullable=False, server_default=db.FetchedValue(), info='签约系统模板key')
    contract_config_tmp_version = db.Column(db.SmallInteger, nullable=False, server_default=db.FetchedValue(), info='签约系统模板版本号')
    contract_config_tmp_desc = db.Column(db.String(64), nullable=False, server_default=db.FetchedValue(), info='签约系统模板描述')
    contract_config_params = db.Column(db.Text, info='合同参数')
    contract_config_storage = db.Column(db.String(256), nullable=False, server_default=db.FetchedValue(), info='合同存储位置（存储规则）')
    contract_config_create_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())
    contract_config_update_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())
    contract_config_version = db.Column(db.SmallInteger, nullable=False, info='合同配置版本')



class ContractEnc(db.Model, BaseToDict):
    __tablename__ = 'contract_enc'
    __table_args__ = (
        db.Index('idx_contract_asset_item_no_contract_type', 'contract_asset_item_no', 'contract_type'),
    )

    contract_id = db.Column(db.Integer, primary_key=True)
    contract_asset_item_no = db.Column(db.String(48), nullable=False, server_default=db.FetchedValue(), info='资产编号')
    contract_type = db.Column(db.Integer, nullable=False)
    contract_type_text = db.Column(db.String(255), nullable=False, server_default=db.FetchedValue())
    contract_url = db.Column(db.String(1000), nullable=False, server_default=db.FetchedValue())
    contract_status = db.Column(db.Enum('VOID', 'SUCCESS', 'SIGN_APPLY'), nullable=False, server_default=db.FetchedValue(), info='状态：SIGN_APPLY-签约中，SUCCESS-签约成功')
    contract_from_system = db.Column(db.String(24), nullable=False, server_default=db.FetchedValue(), info='合同来源系统')
    contract_code = db.Column(db.String(25), nullable=False, server_default=db.FetchedValue(), info='合同编号')
    contract_apply_id = db.Column(db.String(64), nullable=False, server_default=db.FetchedValue(), info='申请签约ID')
    contract_flow_key = db.Column(db.String(64), nullable=False, server_default=db.FetchedValue(), info='签约系统流程key')
    contract_create_at = db.Column(db.DateTime, nullable=False, index=True, server_default=db.FetchedValue())
    contract_sign_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info=' 合同签约时间')
    contract_update_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='更新时间')
    contract_ref_item_no = db.Column(db.String(48), nullable=False, index=True, server_default=db.FetchedValue(), info='关联资产编号')
    contract_sign_opportunity = db.Column(db.String(32), nullable=False, server_default=db.FetchedValue(), info='签约时机（AssetImport-资产生成时, AssetWithdrawSuccess-放款到卡成功时,AssetReorganized-展期时,BeforeImport-进件前签约,PayoffAsset-结清时,Diversion-导流时,BeforeRegister-开户前，BeforeApply-进件资方前,ContractDownload-进件资方成功，BindSuccess-绑卡成功,FoxContractSign-贷后法催协议签署')
    contract_provider = db.Column(db.String(48), nullable=False, server_default=db.FetchedValue(), info='合同签约商')
    contract_subject = db.Column(db.String(48), nullable=False, server_default=db.FetchedValue(), info='公司主体')
    contract_channel = db.Column(db.String(32), nullable=False, server_default=db.FetchedValue(), info='放款渠道')
    contract_version = db.Column(db.SmallInteger, nullable=False, server_default=db.FetchedValue(), info='合同配置版本')



class ContractEnc1(db.Model, BaseToDict):
    __tablename__ = 'contract_enc1'
    __table_args__ = (
        db.Index('idx_contract_asset_item_no_contract_type', 'contract_asset_item_no', 'contract_type'),
    )

    contract_id = db.Column(db.Integer, primary_key=True, info='id')
    contract_asset_item_no = db.Column(db.String(48), nullable=False, server_default=db.FetchedValue(), info='资产编号')
    contract_type = db.Column(db.Integer, nullable=False, info='合同类型编码')
    contract_type_text = db.Column(db.String(255), nullable=False, server_default=db.FetchedValue(), info='合同类型描述')
    contract_url = db.Column(db.String(1000), nullable=False, server_default=db.FetchedValue(), info='合同地址')
    contract_status = db.Column(db.Enum('VOID', 'SUCCESS', 'SIGN_APPLY'), nullable=False, server_default=db.FetchedValue(), info='状态：SIGN_APPLY-签约中，SUCCESS-签约成功')
    contract_from_system = db.Column(db.String(24), nullable=False, server_default=db.FetchedValue(), info='合同来源系统')
    contract_code = db.Column(db.String(25), nullable=False, server_default=db.FetchedValue(), info='合同编号')
    contract_apply_id = db.Column(db.String(64), nullable=False, server_default=db.FetchedValue(), info='申请签约ID')
    contract_flow_key = db.Column(db.String(64), nullable=False, server_default=db.FetchedValue(), info='签约系统流程key')
    contract_create_at = db.Column(db.DateTime, nullable=False, index=True, server_default=db.FetchedValue(), info='创建时间')
    contract_sign_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info=' 合同签约时间')
    contract_update_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='更新时间')
    contract_ref_item_no = db.Column(db.String(48), nullable=False, index=True, server_default=db.FetchedValue(), info='关联资产编号')
    contract_sign_opportunity = db.Column(db.String(32), nullable=False, server_default=db.FetchedValue(), info='签约时机（AssetImport-资产生成时, AssetWithdrawSuccess-放款到卡成功时,AssetReorganized-展期时,BeforeImport-进件前签约,PayoffAsset-结清时,Diversion-导流时,BeforeRegister-开户前，BeforeApply-进件资方前,ContractDownload-进件资方成功，BindSuccess-绑卡成功,FoxContractSign-贷后法催协议签署')
    contract_provider = db.Column(db.String(48), nullable=False, server_default=db.FetchedValue(), info='合同签约商')
    contract_subject = db.Column(db.String(48), nullable=False, server_default=db.FetchedValue(), info='公司主体')
    contract_channel = db.Column(db.String(32), nullable=False, server_default=db.FetchedValue(), info='放款渠道')
    contract_version = db.Column(db.SmallInteger, nullable=False, server_default=db.FetchedValue(), info='合同配置版本')



class ContractMigration(db.Model, BaseToDict):
    __tablename__ = 'contract_migration'
    __table_args__ = (
        db.Index('idx_contract_migration_item_no_contract_type', 'contract_migration_item_no', 'contract_migration_contract_type'),
    )

    contract_migration_id = db.Column(db.Integer, primary_key=True)
    contract_migration_contract_id = db.Column(db.Integer, nullable=False, index=True, info='合同ID')
    contract_migration_contract_code = db.Column(db.String(48), nullable=False, server_default=db.FetchedValue(), info='合同编号')
    contract_migration_item_no = db.Column(db.String(48), nullable=False, server_default=db.FetchedValue(), info='资产编号')
    contract_migration_contract_type = db.Column(db.Integer, nullable=False, info='合同类型')
    contract_migration_contract_type_text = db.Column(db.String(128), nullable=False, server_default=db.FetchedValue(), info='合同描述')
    contract_migration_status = db.Column(db.Integer, nullable=False, info='状态：0-初始化;1-已迁移;2-已验证;3-已完成;4-异常')
    contract_migration_source_url = db.Column(db.String(1000), nullable=False, server_default=db.FetchedValue(), info='迁移前：合同链接）')
    contract_migration_source_storage_name = db.Column(db.String(48), nullable=False, server_default=db.FetchedValue(), info='迁移前：存储名')
    contract_migration_source_digest = db.Column(db.String(32), info='迁移前：md5摘要')
    contract_migration_target_url = db.Column(db.String(1000), info='迁移后：合同链接')
    contract_migration_target_storage_name = db.Column(db.String(48), info='迁移后：存储名')
    contract_migration_target_digest = db.Column(db.String(32), info='迁移后：md5摘要')
    contract_migration_batch_no = db.Column(db.String(128), info='批次号，例如：migration_20220105')
    contract_migration_memo = db.Column(db.String(1024), info='备注')
    contract_migration_create_at = db.Column(db.DateTime, nullable=False, index=True, server_default=db.FetchedValue())
    contract_migration_update_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='更新时间')



class Log(db.Model, BaseToDict):
    __tablename__ = 'log'

    log_id = db.Column(db.Integer, primary_key=True)
    log_level = db.Column(db.Enum('INFO', 'ERROR'), nullable=False, server_default=db.FetchedValue(), info='日志级别')
    log_key = db.Column(db.String(64), nullable=False, index=True, server_default=db.FetchedValue(), info='关键词')
    log_key1 = db.Column(db.String(64), nullable=False, index=True, server_default=db.FetchedValue(), info='关键词1')
    log_key2 = db.Column(db.String(64), nullable=False, index=True, server_default=db.FetchedValue(), info='关键词2')
    log_name = db.Column(db.String(64), nullable=False, server_default=db.FetchedValue(), info='日志名称')
    log_target = db.Column(db.Text, info='记录日志对象')
    log_arg = db.Column(db.Text, info='参数')
    log_message = db.Column(db.Text, info='日志信息')
    log_create_at = db.Column(db.DateTime, nullable=False, index=True, server_default=db.FetchedValue(), info='创建时间')



class Sendmsg(db.Model, BaseToDict):
    __tablename__ = 'sendmsg'
    __table_args__ = (
        db.Index('Idx_sendmsg_next_run_at_version_priority_status', 'sendmsg_status', 'sendmsg_priority', 'sendmsg_next_run_at'),
    )

    sendmsg_id = db.Column(db.Integer, primary_key=True)
    sendmsg_order_no = db.Column(db.String(64), nullable=False, index=True, server_default=db.FetchedValue())
    sendmsg_type = db.Column(db.String(45), nullable=False)
    sendmsg_status = db.Column(db.Enum('open', 'running', 'error', 'terminated', 'close'), nullable=False)
    sendmsg_next_run_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())
    sendmsg_content = db.Column(db.String, nullable=False)
    sendmsg_memo = db.Column(db.String(2048), nullable=False, server_default=db.FetchedValue())
    sendmsg_tosystem = db.Column(db.String(64), nullable=False, server_default=db.FetchedValue())
    sendmsg_create_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())
    sendmsg_update_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())
    sendmsg_version = db.Column(db.SmallInteger, nullable=False, server_default=db.FetchedValue())
    sendmsg_priority = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue())
    sendmsg_retrytimes = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue())
    sendmsg_response_data = db.Column(db.Text)



class ShortMap(db.Model, BaseToDict):
    __tablename__ = 'short_map'

    short_map_id = db.Column(db.Integer, primary_key=True)
    short_map_key = db.Column(db.String(128), nullable=False, unique=True, server_default=db.FetchedValue(), info='短链接')
    short_map_value = db.Column(db.String(1024), nullable=False, server_default=db.FetchedValue(), info='映射值')
    short_map_expire_at = db.Column(db.DateTime, nullable=False, index=True, info='过期时间')
    short_map_create_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='创建时间')
    short_map_update_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='更新时间')



class Synctask(db.Model, BaseToDict):
    __tablename__ = 'synctask'
    __table_args__ = (
        db.Index('idx_synctask_type_status_update_at', 'synctask_type', 'synctask_status', 'synctask_update_at'),
        db.Index('idx_synctask_key', 'synctask_key', 'synctask_type', 'synctask_from_system'),
        db.Index('idx_synctask_update_at_status', 'synctask_status', 'synctask_update_at')
    )

    synctask_id = db.Column(db.Integer, primary_key=True)
    synctask_type = db.Column(db.String(100), info='任务类型')
    synctask_key = db.Column(db.String(50), info='任务键值')
    synctask_from_system = db.Column(db.String(50), info='任务来源系统')
    synctask_request_data = db.Column(db.String, info='任务数据，Json格式')
    synctask_response_data = db.Column(db.Text, info='任务执行完车后，返回结果数据，Json格式')
    synctask_memo = db.Column(db.Text, info='任务执行中出现异常时,纪录异常日志')
    synctask_status = db.Column(db.Enum('open', 'running', 'terminated', 'close', 'error'), nullable=False, server_default=db.FetchedValue(), info='任务状态，初始状态Open， 执行中为runing, 错误为error，执行完成为close,执行错误次数达上限为terminated')
    synctask_create_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='创建时间')
    synctask_update_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='更新时间')
    synctask_order_no = db.Column(db.String(64), nullable=False, server_default=db.FetchedValue(), info='业务主键')
    synctask_last_run_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='最后执行时间')
    synctask_retrytimes = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue())



class Task(db.Model, BaseToDict):
    __tablename__ = 'task'
    __table_args__ = (
        db.Index('Idx_task_next_run_at_version_priority_status', 'task_status', 'task_priority', 'task_next_run_at'),
    )

    task_id = db.Column(db.Integer, primary_key=True)
    task_order_no = db.Column(db.String(64), nullable=False, index=True, server_default=db.FetchedValue())
    task_type = db.Column(db.String(45), nullable=False)
    task_status = db.Column(db.Enum('open', 'running', 'error', 'terminated', 'close'), nullable=False)
    task_next_run_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())
    task_request_data = db.Column(db.Text, nullable=False)
    task_response_data = db.Column(db.Text, nullable=False)
    task_memo = db.Column(db.String(2048), nullable=False, server_default=db.FetchedValue())
    task_create_at = db.Column(db.DateTime, nullable=False, index=True, server_default=db.FetchedValue())
    task_update_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())
    task_version = db.Column(db.SmallInteger, nullable=False, server_default=db.FetchedValue())
    task_priority = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue())
    task_retrytimes = db.Column(db.SmallInteger, nullable=False, server_default=db.FetchedValue())
