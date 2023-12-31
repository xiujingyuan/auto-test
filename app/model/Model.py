# coding: utf-8
from app import db
from app.common.db_util import BaseToDict


class TaskRelativeCase(db.Model, BaseToDict):
    __tablename__ = 'task_relative_case'

    task_relative_case_id = db.Column(db.Integer, primary_key=True, info='自增ID')
    task_relative_case_task_id = db.Column(db.Integer, info='任务id')
    task_relative_case_case_id = db.Column(db.Integer, info='用例id')
    task_relative_case_status = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), info='1:有效，0:无效')
    task_relative_create_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())
    task_relative_update_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())


class CaseTask(db.Model, BaseToDict):
    __tablename__ = 'case_task'

    case_task_id = db.Column(db.Integer, primary_key=True, info='自增ID')
    case_task_name = db.Column(db.String(256), info='任务名称')
    case_task_creator = db.Column(db.String(11), info='创建者')
    case_task_updater = db.Column(db.String(11), info='最后更新人')
    case_task_execute_time = db.Column(db.String(20), info='执行时间')
    case_task_create_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='创建时间')
    case_task_update_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='更新时间')
    case_task_country = db.Column(db.String(10), nullable=False, server_default=db.FetchedValue(), info='国家')
    case_task_program = db.Column(db.String(10), info='系统')
    case_task_type = db.Column(db.Integer, info='任务类型，0:具体时间；1:cron')
    case_task_run_env = db.Column(db.String(1), nullable=False, server_default=db.FetchedValue())
    case_task_is_valid = db.Column(db.BOOLEAN, nullable=False, server_default=db.FetchedValue(), info='任务是否有效')
    case_task_status = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(),
                                 info='0:空闲;1:运行中;2:队列中;3:结束;4:异常')


class TraceInfo(db.Model, BaseToDict):
    __tablename__ = 'trace_info'

    trace_info_id = db.Column(db.Integer, primary_key=True)
    trace_info_trace_id = db.Column(db.Integer, nullable=False, info='关联的taskid或者是synctaskid')
    trace_info_env = db.Column(db.Integer, info='环境')
    trace_info_program = db.Column(db.String(10), nullable=False, info='所属项目，repay，grant，biz-central')
    trace_info_trace_type = db.Column(db.String(30), info='类型')
    trace_info_content = db.Column(db.Text, nullable=False, info='内容')
    trace_info_create_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())
    trace_info_update_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())
    trace_info_creator = db.Column(db.String(10), nullable=False)


class AutoAsset(db.Model, BaseToDict):
    __tablename__ = 'asset'

    asset_id = db.Column(db.Integer, primary_key=True, info='创建资产的ID')
    asset_name = db.Column(db.String(30), info='资产编号')
    asset_period = db.Column(db.String(2, 'utf8_bin'), info='资产期次')
    asset_channel = db.Column(db.String(50), info='放款通道')
    asset_country = db.Column(db.String(11), info='所属国家')
    asset_env = db.Column(db.String(10), nullable=False, server_default=db.FetchedValue(), info='所属环境')
    asset_descript = db.Column(db.String(50), info='资产描述')
    asset_extend = db.Column(db.Text, info='扩展')
    asset_create_owner = db.Column(db.String(11), nullable=False, server_default=db.FetchedValue(), info='资产创建人')
    asset_create_at = db.Column(db.Date, nullable=False, info='资产创建时间')
    asset_update_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='资产更新时间')
    asset_type = db.Column(db.String(1), nullable=False, server_default=db.FetchedValue(), info='0:本地，1:前端本地，2:本地资方，3:前端资方')
    asset_days = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), info='每期天数')
    asset_source_type = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), info='0:自动放款，1:手动添加')


class BackendKeyValue(db.Model, BaseToDict):
    __tablename__ = 'backend_key_value'

    id = db.Column(db.Integer, primary_key=True, info='自增长id')
    backend_key = db.Column(db.String(40), nullable=False, server_default=db.FetchedValue(), info='后台配置key')
    backend_value = db.Column(db.Text, nullable=False, info='后台配置value')
    backend_group = db.Column(db.String(20), nullable=False, server_default=db.FetchedValue(), info='后台配置分组')
    backend_is_active = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), info='后台配置是否有效')
    backend_create_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='后台配置创建时间')
    backend_update_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='后台配置更想时间')


class Menu(db.Model, BaseToDict):
    __tablename__ = 'menu'

    menu_id = db.Column(db.Integer, primary_key=True)
    menu_create_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='创建时间')
    menu_update_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='更新时间')
    menu_icon = db.Column(db.String(30), nullable=False, server_default=db.FetchedValue(), info='图标')
    menu_title = db.Column(db.String(10), nullable=False, server_default=db.FetchedValue(), info='菜单名字')
    menu_index = db.Column(db.String(50), nullable=False, server_default=db.FetchedValue(), info='菜单地址')
    menu_active = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), info='是否激活菜单')
    menu_order = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), info='菜单顺序')
    menu_parent_id = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), info='父菜单menu_id')


class MockConfig(db.Model, BaseToDict):
    __tablename__ = 'mock_config'

    mock_config_id = db.Column(db.Integer, primary_key=True, info='自增长')
    mock_config_desc = db.Column(db.String(100), nullable=False, server_default=db.FetchedValue(), info='mock描述')
    mock_config_key = db.Column(db.String(20), nullable=False, server_default=db.FetchedValue(), info='mock关键字描述')
    mock_config_name = db.Column(db.String(20), nullable=False, server_default=db.FetchedValue(), info='mock的配置文件名称')
    mock_config_program = db.Column(db.String(20), nullable=False, server_default=db.FetchedValue(), info='所属系统')
    mock_config_value = db.Column(db.String(500), nullable=False, server_default=db.FetchedValue(), info='需要替换值的描述')
    mock_config_order = db.Column(db.Integer, server_default=db.FetchedValue(), info='mock显示顺序')
    mock_config_is_collect = db.Column(db.Integer, server_default=db.FetchedValue(), info='mock是否喜爱')
    mock_config_is_active = db.Column(db.Integer, server_default=db.FetchedValue(), info='mock是否激活')
    mock_config_timeout = db.Column(db.Integer, nullable=False, info='替换超时时间')
    mock_config_creater = db.Column(db.String(8), nullable=False, server_default=db.FetchedValue(), info='mock创建人')
    mock_config_updater = db.Column(db.String(8), nullable=False, server_default=db.FetchedValue(), info='mock最后更新人')
    mock_config_create_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='mock创建时间')
    mock_config_update_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='mock更新时间')


class NacosConfig(db.Model, BaseToDict):
    __tablename__ = 'nacos_config'

    nacos_config_id = db.Column(db.Integer, primary_key=True, info='自增长')
    nacos_config_desc = db.Column(db.String(500), nullable=False, server_default=db.FetchedValue(), info='nacos描述')
    nacos_config_key = db.Column(db.String(100), nullable=False, server_default=db.FetchedValue(), info='nacos关键字描述')
    nacos_config_name = db.Column(db.String(100), nullable=False, server_default=db.FetchedValue(), info='nacos的配置文件名称')
    nacos_config_program = db.Column(db.String(20), nullable=False, server_default=db.FetchedValue(), info='所属系统')
    nacos_config_value = db.Column(db.Text, nullable=False, info='需要替换值的描述')
    nacos_config_order = db.Column(db.Integer, server_default=db.FetchedValue(), info='nacos显示顺序')
    nacos_config_is_collect = db.Column(db.Integer, server_default=db.FetchedValue(), info='nacos是否喜爱')
    nacos_config_is_active = db.Column(db.Integer, server_default=db.FetchedValue(), info='nacos是否激活')
    nacos_config_timeout = db.Column(db.Integer, nullable=False, info='替换超时时间')
    nacos_config_creater = db.Column(db.String(8), nullable=False, server_default=db.FetchedValue(), info='nacos创建人')
    nacos_config_updater = db.Column(db.String(8), nullable=False, server_default=db.FetchedValue(), info='nacos最后更新人')
    nacos_config_create_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='nacos创建时间')
    nacos_config_update_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='nacos更新时间')


class RunCaseLog(db.Model, BaseToDict):
    __tablename__ = 'run_case_log'

    run_case_log_id = db.Column(db.Integer, primary_key=True, info='日志自增ID')
    run_case_log_case_id = db.Column(db.Integer, nullable=False, index=True, info='执行用例的用例ID')
    run_case_log_case_run_date = db.Column(db.Date, nullable=False, index=True, info='用例执行日期')
    run_case_log_case_run_item_no = db.Column(db.String(40), nullable=False, server_default=db.FetchedValue(), info='用例相关资产')
    run_case_log_case_run_withhold_no = db.Column(db.String(255), nullable=False, server_default=db.FetchedValue(), info='用例相关代扣就')
    run_case_log_case_run_result = db.Column(db.String(8), nullable=False, server_default=db.FetchedValue(), info='用例执行结果')
    run_case_log_case_fail_type = db.Column(db.String(8), nullable=False, server_default=db.FetchedValue(), info='用例失败类型')
    run_case_log_case_run_error_message = db.Column(db.Text, info='用例异常信息')
    run_case_log_case_run_begin_at = db.Column(db.DateTime, nullable=False, info='用例开始时间')
    run_case_log_case_run_finish_at = db.Column(db.DateTime, nullable=False, info='用例结束时间')
    run_case_log_create_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='日志创建时间')
    run_case_log_update_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='日志更新时间')
    run_case_log_case_run_group_Id = db.Column(db.String(40), nullable=False, index=True, server_default=db.FetchedValue(), info='用例执行批次ID')


class TestCase(db.Model, BaseToDict):
    __tablename__ = 'test_cases'

    test_cases_id = db.Column(db.Integer, primary_key=True)
    test_cases_country = db.Column(db.String(20), nullable=False, index=True, server_default=db.FetchedValue(), info='所在国家')
    test_cases_priority = db.Column(db.Integer, nullable=False, index=True, server_default=db.FetchedValue(), info='优先级')
    test_cases_group = db.Column(db.String(50), nullable=False, index=True, server_default=db.FetchedValue(), info='项目组')
    test_cases_channel = db.Column(db.String(50), nullable=False, index=True, server_default=db.FetchedValue(), info='资方通道')
    test_cases_mock_name = db.Column(db.String(50), nullable=False, index=True, server_default=db.FetchedValue(), info='资方通道')
    test_cases_scene = db.Column(db.String(20), nullable=False, index=True, server_default=db.FetchedValue(), info='用例场景（大）')
    test_cases_asset_info = db.Column(db.Text, nullable=False, info='资产信息')
    test_cases_repay_info = db.Column(db.Text, nullable=False, info='还款信息')
    test_cases_check_capital_notify = db.Column(db.Text, nullable=False, info='capital_notify检测点')
    test_cases_check_capital_tran = db.Column(db.Text, nullable=False, info='capital_tran检测点')
    test_cases_check_central_msg = db.Column(db.Text, nullable=False, info='central_sendmsg检测点')
    test_cases_check_interface = db.Column(db.Text, nullable=False, info='interface检测点')
    test_cases_check_capital_settlement_detail = db.Column(db.Text, nullable=False, info='settlement_detail检测点')
    test_cases_create_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='创建时间')
    test_cases_update_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='创建时间')
    test_cases_owner = db.Column(db.String(20), nullable=False, server_default=db.FetchedValue(), info='创建人')
    test_cases_updater = db.Column(db.String(20), nullable=False, server_default=db.FetchedValue(), info='更新人')
