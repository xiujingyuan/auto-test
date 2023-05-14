# coding: utf-8
from app import db
from app.common.db_util import BaseToDict


class ApiLog(db.Model, BaseToDict):
    __tablename__ = 'api_log'
    __bind_key__ = 'jc-mock'

    api_log_id = db.Column(db.Integer, primary_key=True)
    api_log_url = db.Column(db.String(200), nullable=False, index=True, server_default=db.FetchedValue(), info='访问的url')
    api_log_servername = db.Column(db.String(100), nullable=False, server_default=db.FetchedValue())
    api_log_method = db.Column(db.String(10), info='请求method')
    api_log_request_body = db.Column(db.Text, info='请求Body')
    api_log_response_body = db.Column(db.Text, info='返回结果')
    api_log_create_at = db.Column(db.DateTime, nullable=False, index=True, server_default=db.FetchedValue())
    api_log_update_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())
    api_log_user = db.Column(db.String(20), nullable=False, server_default=db.FetchedValue(), info='api调用者')
    api_log_is_success = db.Column(db.Integer, server_default=db.FetchedValue(), info='请求返还是否成功，0:失败，1:成功')
    api_log_ip = db.Column(db.String(20), nullable=False, server_default=db.FetchedValue(), info='api_log_ip')


class AssumptBuildTask(db.Model, BaseToDict):
    __tablename__ = 'assumpt_build_task'
    __bind_key__ = 'jc-mock'

    id = db.Column(db.Integer, primary_key=True, info='自增id')
    build_count = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), info='构建次数')
    build_branch = db.Column(db.String(255, 'utf8_bin'), info='构建分支')
    last_build_user = db.Column(db.String(30, 'utf8_bin'), info='最后构建人')
    last_build_time = db.Column(db.DateTime, info='最后构建时间')
    last_build_status = db.Column(db.Integer, info='最后构建状态0:空闲，1:成功，2:失败3:构建中4:已取消5:等待中')
    last_build_env = db.Column(db.String(50, 'utf8_bin'), info='最后构建环境')
    last_coverage = db.Column(db.Float(5), server_default=db.FetchedValue(), info='最后的覆盖率')
    last_run_id = db.Column(db.String(255, 'utf8_bin'), info='最后执行id')
    build_task_status = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), info='构建任务状态。0:空闲；1:测试中')
    create_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='任务创建时间')
    update_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='任务更新时间')
    program_id = db.Column(db.Integer, info='项目id')
    program_name = db.Column(db.String(30, 'utf8_bin'), info='项目名称')
    gitlab_program_id = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), info='gitlab中的项目id')
    gitlab_program_name = db.Column(db.String(50, 'utf8_bin'), info='最后构建环境')
    auto_report_url = db.Column(db.String(255, 'utf8_bin'), info='自动化报告地址')
    jacoco_url = db.Column(db.String(255, 'utf8_bin'), info='覆盖率地址')
    build_jenkins_jobs = db.Column(db.Text, info='jenkins的job')
    last_build_jenkins_task_id = db.Column(db.Integer, info='最后构建jenkins的id')
    story_id = db.Column(db.String(255, 'utf8_bin'))
    story_full_id = db.Column(db.String(255, 'utf8_bin'))
    story_name = db.Column(db.String(255, 'utf8_bin'), info='需求名称')
    story_url = db.Column(db.String(255, 'utf8_bin'), info='需求地址')
    work_id = db.Column(db.String(30, 'utf8_bin'))
    iteration_id = db.Column(db.String(100, 'utf8_bin'))
    email_id = db.Column(db.String(11), nullable=False, info='触发的邮件id')
    mail_receive_time = db.Column(db.DateTime, server_default=db.FetchedValue(), info='提测邮件时间')
    publish_time = db.Column(db.DateTime, info='需求发布时间')
    case_name = db.Column(db.String(255, 'utf8_bin'), info='用例地址')
    run_pipeline = db.Column(db.Integer, server_default=db.FetchedValue(), info='构建次数')
    build_commit_type = db.Column(db.Integer, server_default=db.FetchedValue(), info='对比commit类型；1:构建时的commit_id;2:最新master的commit_id;3.最新的tag的commit_id')
    master_commit_id = db.Column(db.String(255, 'utf8_bin'), info='该任务第一次构建时master的commit_id')
    branch_commit_id = db.Column(db.String(255, 'utf8_bin'), info='该任务当前待测分支的commit_id')
    auto_queue_id = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), info='自动化任务的id')
    auto_url = db.Column(db.String(255), info='自动化构建地址')
    filter_file_value = db.Column(db.Text(collation='utf8_bin'), info='覆盖率过滤文件配置')



class AssumptBuildTaskLog(db.Model, BaseToDict):
    __tablename__ = 'assumpt_build_task_log'
    __bind_key__ = 'jc-mock'

    id = db.Column(db.Integer, primary_key=True, info='自增id')
    build_task_id = db.Column(db.Integer, info='修改的构建任务id')
    person = db.Column(db.String(11), info='修改人')
    modify_content = db.Column(db.Text, info='修改后值')
    create_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='创建时间')
    update_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='更新时间')
    modify_content_old = db.Column(db.Text, info='修改前值')



class AssumptBuildTaskRun(db.Model, BaseToDict):
    __tablename__ = 'assumpt_build_task_run'
    __bind_key__ = 'jc-mock'

    id = db.Column(db.Integer, primary_key=True, info='自增id')
    build_task_id = db.Column(db.Integer, nullable=False, index=True, info='构建任务id')
    build_task_run_id = db.Column(db.String(255, 'utf8_bin'), index=True, server_default=db.FetchedValue(), info='构建任务的run_id')
    build_user = db.Column(db.String(30, 'utf8_bin'), nullable=False, server_default=db.FetchedValue(), info='构建人')
    build_branch = db.Column(db.String(255, 'utf8_bin'), nullable=False, index=True, server_default=db.FetchedValue(), info='构建分支')
    build_result = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), info='构建结果，0:构建中；2:构建成功；3构建失败')
    build_message = db.Column(db.String(collation='utf8_bin'), info='构建日志')
    build_jenkins = db.Column(db.String(255, 'utf8_bin'), nullable=False, server_default=db.FetchedValue(), info='构建的jenkins任务id')
    build_jenkins_task_id = db.Column(db.Integer, info='构建的jenkins的构建id')
    build_jenkins_queue_id = db.Column(db.Integer, info='构建的jenkins的构建id')
    build_env = db.Column(db.String(50, 'utf8_bin'), info='构建环境')
    build_param = db.Column(db.String(10240), info='构建参数')
    build_program_id = db.Column(db.Integer, info='构建的项目id')
    iteration_id = db.Column(db.String(100), info='迭代id')
    build_time = db.Column(db.DateTime, nullable=False, info='构建时间')
    build_commit_type = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), info='对比commit类型；1:构建时的commit_id;2:最新master的commit_id;3.最新的tag的commit_id')



class AssumptEmail(db.Model, BaseToDict):
    __tablename__ = 'assumpt_email'
    __bind_key__ = 'jc-mock'

    id = db.Column(db.Integer, primary_key=True, info='自增id')
    email_id = db.Column(db.String(11), nullable=False, server_default=db.FetchedValue(), info='邮件ID')
    email_from = db.Column(db.String(255), nullable=False, server_default=db.FetchedValue(), info='发送方')
    email_to = db.Column(db.Text, nullable=False, info='接收方')
    email_content = db.Column(db.String, nullable=False, info='内容')
    email_attach = db.Column(db.String(11), info='附件')
    mail_receive_time = db.Column(db.DateTime, nullable=False, info='邮件接收时间')
    create_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='记录创建时间')
    story_id = db.Column(db.String(255, 'utf8_bin'), info='关联需求id')
    href_value = db.Column(db.Text(collation='utf8_bin'), info='包含的链接')
    subject = db.Column(db.String(255, 'utf8_bin'), info='标题')
    story_full_id = db.Column(db.String(255, 'utf8_bin'), info='关联需求的完整版id')
    work_id = db.Column(db.String(20, 'utf8_bin'), info='关联需求所在的项目id(tapd)')



class BranchCoverage(db.Model, BaseToDict):
    __tablename__ = 'branch_coverage'
    __bind_key__ = 'jc-mock'

    id = db.Column(db.Integer, primary_key=True, info='自增id')
    system = db.Column(db.String(60, 'utf8_bin'), info='项目')
    branch = db.Column(db.String(255, 'utf8_bin'), info='分支')
    tester = db.Column(db.String(60, 'utf8_bin'), info='测试人')
    coverage = db.Column(db.String(20, 'utf8_bin'), info='增加覆盖率')
    create_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='创建时间')
    update_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='更新时间')



class CiAutotestInfo(db.Model, BaseToDict):
    __tablename__ = 'ci_autotest_info'
    __bind_key__ = 'jc-mock'

    ci_autotest_id = db.Column(db.Integer, primary_key=True, info='自增id')
    ci_autotest_pipeline_serial_num = db.Column(db.String(20), info='用例总数')
    ci_autotest_total_num = db.Column(db.String(20), info='用例总数')
    ci_autotest_success_num = db.Column(db.String(20), info='用例成功数')
    ci_autotest_fail_num = db.Column(db.String(20), info='用例失败数')
    ci_autotest_success_rate = db.Column(db.String(20), info='用例失败数')
    ci_autotest_running_time = db.Column(db.String(50), info='用例执行时间')
    ci_autotest_report_address = db.Column(db.String(255), info='报告地址')
    ci_autotest_create_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='创建时间')
    ci_autotest_update_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='更新时间')



class CiConfig(db.Model, BaseToDict):
    __tablename__ = 'ci_config'
    __bind_key__ = 'jc-mock'

    ci_config_id = db.Column(db.Integer, primary_key=True, info='自增id')
    ci_config_name = db.Column(db.String(50), info='流水线名称')
    ci_config_deciption = db.Column(db.String(50), info='流水线描述')
    ci_config_steps = db.Column(db.String(255), info='流水线步骤')
    ci_config_git_project_id = db.Column(db.String(100), info='流水线对应git工程id')



class CiEmail(db.Model, BaseToDict):
    __tablename__ = 'ci_email'
    __bind_key__ = 'jc-mock'

    ci_email_id = db.Column(db.Integer, primary_key=True, info='自增id')
    ci_email_serial_num = db.Column(db.String(50), info='邮件流水号')
    ci_email_recipients = db.Column(db.String(255), info='邮件收件人')
    ci_email_subject = db.Column(db.String(100), info='邮件主题')
    ci_email_status = db.Column(db.String(50), info='邮件状态')
    ci_email_html = db.Column(db.Text(collation='utf8_bin'), info='邮件内容')
    ci_email_create_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='更新时间')



class CiJobInfo(db.Model, BaseToDict):
    __tablename__ = 'ci_job_info'
    __bind_key__ = 'jc-mock'

    ci_job_id = db.Column(db.Integer, primary_key=True, info='自增id')
    ci_job_name = db.Column(db.String(50), info='jenkins job名')
    ci_job_type = db.Column(db.String(50), info='jenkins job类型')
    ci_job_deciption = db.Column(db.String(255), info='jenkins job描述')
    ci_job_address = db.Column(db.String(100), info='jenkins job地址')
    ci_job_default_env = db.Column(db.String(50), info='jenkins job默认运行环境')
    ci_job_system = db.Column(db.String(50), info='jenkins job所属系统')
    ci_job_git_project_id = db.Column(db.Integer, info='jenkins job对应git项目id')
    ci_job_mail_receiver = db.Column(db.String(512), info='jenkins job邮件接收者')
    ci_job_sonar_address = db.Column(db.String(100), info='sonar地址')



class CiLogInfo(db.Model, BaseToDict):
    __tablename__ = 'ci_log_info'
    __bind_key__ = 'jc-mock'

    ci_log_id = db.Column(db.Integer, primary_key=True, info='自增id')
    ci_log_pipeline_serial_num = db.Column(db.String(20), info='日志console地址')
    ci_log_console_address = db.Column(db.String(1024), info='日志console地址')
    ci_log_build_number = db.Column(db.Integer)
    ci_log_console_info = db.Column(db.Text(collation='utf8_bin'), info='具体日志信息')



class CiPipeline(db.Model, BaseToDict):
    __tablename__ = 'ci_pipeline'
    __bind_key__ = 'jc-mock'

    ci_pipeline_id = db.Column(db.Integer, primary_key=True, info='自增id')
    ci_pipeline_serial_num = db.Column(db.String(20), info='流水线序列号')
    ci_pipeline_trigger_type = db.Column(db.String(20), info='触发类型')
    ci_pipeline_trigger_user = db.Column(db.String(20), info='触发人')
    ci_pipeline_trigger_info = db.Column(db.Text(collation='utf8_bin'), info='触发信息')
    ci_pipeline_branch = db.Column(db.String(50), index=True, info='分支')
    ci_pipeline_source_branch = db.Column(db.String(50), info='分支')
    ci_pipeline_step = db.Column(db.String(20), info='当前步骤')
    ci_pipeline_address = db.Column(db.String(255), info='jenkins job地址')
    ci_pipeline_job_id = db.Column(db.Integer, server_default=db.FetchedValue(), info='jenkins job表id')
    ci_pipeline_job_log_id = db.Column(db.Integer, server_default=db.FetchedValue(), info='jenkins日志表id')
    ci_pipeline_autotest_id = db.Column(db.Integer, server_default=db.FetchedValue(), info='自动化表id')
    ci_pipeline_sona_id = db.Column(db.Integer, server_default=db.FetchedValue(), info='sona信息表id')
    ci_pipeline_build_num = db.Column(db.Integer, server_default=db.FetchedValue(), info='jenkins构建序号')
    ci_pipeline_env = db.Column(db.String(20), info='运行环境')
    ci_pipeline_status = db.Column(db.String(20), index=True, info='运行状态')
    ci_pipeline_run_time = db.Column(db.String(50), info='运行时间')
    ci_pipeline_handler_user = db.Column(db.String(255), info='处理人')
    ci_pipeline_handler_info = db.Column(db.String(255), info='处理信息')
    ci_pipeline_handler_times = db.Column(db.String(255), info='处理用时')
    ci_pipeline_create_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='创建时间')
    ci_pipeline_update_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='更新时间')



class CiSonaInfo(db.Model, BaseToDict):
    __tablename__ = 'ci_sona_info'
    __bind_key__ = 'jc-mock'

    ci_sona_id = db.Column(db.Integer, primary_key=True, info='自增id')
    ci_sona_pipeline_serial_num = db.Column(db.String(20), info='ce任务taskid')
    ci_sona_ce_task_id = db.Column(db.String(20), info='ce任务taskid')
    ci_sona_bugs = db.Column(db.String(20), info='bug总数')
    ci_sona_vulnerabilities = db.Column(db.String(20), info='漏洞总数')
    ci_sona_debt = db.Column(db.String(20), info='debt总数')
    ci_sona_code_smells = db.Column(db.String(20), info='怀味道总数')
    ci_sona_coverage = db.Column(db.String(20), info='覆盖率')
    ci_sona_duplicateds = db.Column(db.String(20), info='重复度')
    ci_sona_duplicated_blocks = db.Column(db.String(20), info='重复块')
    ci_sona_create_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='创建时间')
    ci_sona_update_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='更新时间')



class CommonTool(db.Model, BaseToDict):
    __tablename__ = 'common_tools'
    __bind_key__ = 'jc-mock'

    common_tools_id = db.Column(db.Integer, primary_key=True)
    common_tools_title = db.Column(db.String(500), info='工具名称')
    common_tools_address = db.Column(db.String(2500), info='工具地址')
    common_tools_method = db.Column(db.String(50), info='请求方法')
    common_tools_placeholder = db.Column(db.Text, info='工具demo')
    common_tools_description = db.Column(db.String(1000), info='工具描述')
    common_tools_update_time = db.Column(db.DateTime, server_default=db.FetchedValue())
    common_tools_update_user = db.Column(db.String(20))
    common_tools_create_time = db.Column(db.DateTime, server_default=db.FetchedValue())
    common_tools_create_user = db.Column(db.String(20), info='工具开发者')
    common_tools_is_int = db.Column(db.Integer, server_default=db.FetchedValue(), info='是否为联调工具')
    common_tools_req_desc = db.Column(db.String, info='请求参数说明')
    common_tools_resp_desc = db.Column(db.String, info='返回值说明')



class CoverageInfo(db.Model, BaseToDict):
    __tablename__ = 'coverage_info'
    __bind_key__ = 'jc-mock'

    id = db.Column(db.Integer, primary_key=True, info='自增id')
    gitlab_program_id = db.Column(db.Integer, index=True, info='gitlab的id')
    branch = db.Column(db.String(255), index=True, info='基准分支/commit号')
    service_name = db.Column(db.String(50), info='服务名')
    compare_branch = db.Column(db.String(255), index=True, info='对比分支/commit号')
    content = db.Column(db.String(collation='utf8_bin'), info='增量覆盖率内容-原始内容')
    version = db.Column(db.String(20, 'utf8_bin'), info='获取版本号')
    create_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='创建时间')
    update_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='更新时间')
    env = db.Column(db.String(20, 'utf8_bin'), info='执行环境')
    new_coverage = db.Column(db.Integer, server_default=db.FetchedValue(), info='获取覆盖率类型')



class DiffCoverageReport(db.Model, BaseToDict):
    __tablename__ = 'diff_coverage_report'
    __bind_key__ = 'jc-mock'

    id = db.Column(db.Integer, primary_key=True)
    job_record_uuid = db.Column(db.String(80), nullable=False, unique=True, info='请求唯一标识码')
    request_status = db.Column(db.Integer, nullable=False, info='请求执行状态,1=下载代码成功,2=生成diffmethod成功，3=生成报告成功,-1=执行出错')
    line_coverage = db.Column(db.Float(5, True), nullable=False, server_default=db.FetchedValue(), info='行覆盖率')
    line_cover = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), info='覆盖行数')
    line_total = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), info='总行数')
    branch_coverage = db.Column(db.Float(5, True), nullable=False, server_default=db.FetchedValue(), info='分支覆盖率')
    request_desc = db.Column(db.String(80), server_default=db.FetchedValue(), info='执行请求描述')
    giturl = db.Column(db.String(80), nullable=False, info='git 地址')
    now_version = db.Column(db.String(80), nullable=False, info='本次提交的commidId')
    base_version = db.Column(db.String(80), nullable=False, info='比较的基准commitId')
    now_commit_id = db.Column(db.String(80), info='本次提交的commidId')
    diffmethod = db.Column(db.String, info='增量代码的diff方法集合')
    type = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), info='2=增量代码覆盖率,1=全量覆盖率')
    report_url = db.Column(db.String(300), nullable=False, server_default=db.FetchedValue(), info='覆盖率报告url')
    err_msg = db.Column(db.String(1000), nullable=False, server_default=db.FetchedValue(), info='错误信息')
    sub_module = db.Column(db.String(255), nullable=False, server_default=db.FetchedValue(), info='子项目目录名称')
    _from = db.Column('from', db.Integer, nullable=False, server_default=db.FetchedValue(), info='1=单元测试，2=环境部署1=单元测试，2=hu')
    now_local_path = db.Column(db.String(500), nullable=False, server_default=db.FetchedValue())
    base_local_path = db.Column(db.String(500), nullable=False, server_default=db.FetchedValue())
    log_file = db.Column(db.String(255), nullable=False, server_default=db.FetchedValue())
    exclude = db.Column(db.String(255), server_default=db.FetchedValue())
    mvn_extend = db.Column(db.String(255), server_default=db.FetchedValue())
    create_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='创建时间')
    update_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='修改时间')



class DiffDeployInfo(db.Model, BaseToDict):
    __tablename__ = 'diff_deploy_info'
    __bind_key__ = 'jc-mock'

    id = db.Column(db.Integer, primary_key=True)
    job_record_uuid = db.Column(db.String(80), nullable=False, unique=True, info='请求唯一标识码')
    address = db.Column(db.String(100), nullable=False, server_default=db.FetchedValue(), info='HOST')
    port = db.Column(db.Integer, nullable=False, info='端口')
    code_path = db.Column(db.String(1000), nullable=False, server_default=db.FetchedValue(), info='nowVersion代码目录')
    child_modules = db.Column(db.String(2000), nullable=False, server_default=db.FetchedValue(), info='项目子模块名称')



class ErrorLog(db.Model, BaseToDict):
    __tablename__ = 'error_logs'
    __bind_key__ = 'jc-mock'

    error_log_id = db.Column(db.Integer, primary_key=True)
    error_log_msg = db.Column(db.Text(collation='utf8_bin'))
    erro_log_create_at = db.Column(db.DateTime)
    error_log_update_at = db.Column(db.DateTime)



class GitMergeInfo(db.Model, BaseToDict):
    __tablename__ = 'git_merge_info'
    __bind_key__ = 'jc-mock'

    id = db.Column(db.Integer, primary_key=True)
    merge_id = db.Column(db.Integer)
    merge_title = db.Column(db.String(255, 'utf8_bin'))
    source_branch = db.Column(db.String(255, 'utf8_bin'))
    target_branch = db.Column(db.String(255, 'utf8_bin'))
    start_commit_sha = db.Column(db.String(255, 'utf8_bin'))
    end_commit_sha = db.Column(db.String(255, 'utf8_bin'))
    merge_create_user = db.Column(db.String(255, 'utf8_bin'))
    merge_close_user = db.Column(db.String(255, 'utf8_bin'))
    merge_create = db.Column(db.DateTime)
    merge_create_date = db.Column(db.Date)
    git_commit_count = db.Column(db.Integer)
    git_add_lines = db.Column(db.Integer)
    git_remove_lines = db.Column(db.Integer)
    git_changed_file = db.Column(db.Integer)
    gitlab_id = db.Column(db.Integer)
    gitlab_name = db.Column(db.String(100, 'utf8_bin'))
    program_id = db.Column(db.Integer)
    create_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())
    update_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())



class GitTagInfo(db.Model, BaseToDict):
    __tablename__ = 'git_tag_info'
    __bind_key__ = 'jc-mock'

    id = db.Column(db.Integer, primary_key=True, info='记录自增id')
    tag_id = db.Column(db.String(50), nullable=False, server_default=db.FetchedValue(), info='gitlab中对应的分支名')
    tag_name = db.Column(db.String(50), nullable=False, server_default=db.FetchedValue(), info='gitlab中对应的分支名')
    tag_gitlab_id = db.Column(db.Integer, nullable=False, info='分支总的提交次数')
    tag_create = db.Column(db.DateTime, nullable=False, info='记录创建时间')
    tag_create_date = db.Column(db.Date, nullable=False, info='统计时间2')
    tag_message = db.Column(db.String(255, 'utf8_bin'))
    tag_commit_id = db.Column(db.String(50, 'utf8_bin'), nullable=False, info='分支删除的代码行数')
    tag_commit_message = db.Column(db.String(255, 'utf8_bin'), info='分支总修改的文件数')
    create_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='记录创建时间')
    update_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='记录更新时间')
    is_effective = db.Column(db.Integer, server_default=db.FetchedValue(), info='1:生效，0:失效')
    program_id = db.Column(db.Integer, nullable=False, info='测试平台项目id')



class GitlabProgram(db.Model, BaseToDict):
    __tablename__ = 'gitlab_programs'
    __bind_key__ = 'jc-mock'

    id = db.Column(db.Integer, primary_key=True, info='自增id')
    git_program_id = db.Column(db.Integer, nullable=False, info='git上的项目的id')
    git_program_name = db.Column(db.String(255, 'utf8_bin'), nullable=False, server_default=db.FetchedValue(), info='git上的项目的名称')
    create_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='创建时间')
    update_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='更新时间')



class JenkinsJob(db.Model, BaseToDict):
    __tablename__ = 'jenkins_jobs'
    __bind_key__ = 'jc-mock'

    jenkins_id = db.Column(db.Integer, primary_key=True, info='自增id')
    jenkins_job_name = db.Column(db.String(100, 'utf8_bin'), info='jenkins任务名')
    jenkins_url = db.Column(db.String(200, 'utf8_bin'), info='jenkins的地址')
    jenkinis_params = db.Column(db.Text(collation='utf8_bin'), info='jenkins的参数')
    jenkinis_create_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='jenkins创建时间')
    jenkinis_update_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='jenkins更新时间')
    gitlab_program_id = db.Column(db.Integer, info='gitlab中的项目id')
    gitlab_program_http_url = db.Column(db.String(100, 'utf8_bin'), info='gitlab中的项目url')
    program_id = db.Column(db.Integer, info='项目id')
    service_name = db.Column(db.String(255, 'utf8_bin'), info='提测邮件服务名')
    jacoco_url = db.Column(db.String(200, 'utf8_bin'), info='jacoco_url的地址')
    git_report_name = db.Column(db.String(200, 'utf8_bin'), info='git_report的名字')
    git_module = db.Column(db.Text(collation='utf8_bin'), info='git模块信息')
    is_active = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), info='该jenkins任务是否启用，0=不启用')
    change_ip = db.Column(db.Integer, server_default=db.FetchedValue(), info='是否需求要更jacoco的ip')



class KeyValue(db.Model, BaseToDict):
    __tablename__ = 'key_value'
    __bind_key__ = 'jc-mock'

    id = db.Column(db.Integer, primary_key=True, info='自增id')
    key = db.Column(db.String(100), nullable=False, server_default=db.FetchedValue(), info='key')
    value = db.Column(db.Text, info='value')
    memo = db.Column(db.Text, info='备注')
    status = db.Column(db.Enum('active', 'inactive'), nullable=False, server_default=db.FetchedValue(), info='状态')
    create_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='创建时间')
    update_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='更新时间')



class LinkType(db.Model, BaseToDict):
    __tablename__ = 'link_types'
    __bind_key__ = 'jc-mock'

    link_type_id = db.Column(db.Integer, primary_key=True)
    link_type_name = db.Column(db.String(255, 'utf8_bin'))
    link_type_create_at = db.Column(db.DateTime)



class Link(db.Model, BaseToDict):
    __tablename__ = 'links'
    __bind_key__ = 'jc-mock'

    link_id = db.Column(db.Integer, primary_key=True)
    link_title = db.Column(db.String(255, 'utf8_bin'))
    link_url = db.Column(db.String(255, 'utf8_bin'))
    link_type = db.Column(db.ForeignKey('link_types.link_type_id'), index=True)
    link_pwd = db.Column(db.String(255, 'utf8_bin'))
    link_user = db.Column(db.String(255, 'utf8_bin'))
    link_click_count = db.Column(db.Integer, server_default=db.FetchedValue())
    link_create_at = db.Column(db.DateTime)
    link_update_at = db.Column(db.DateTime)

    link_type1 = db.relationship('LinkType', primaryjoin='Link.link_type == LinkType.link_type_id', backref='links')



class Menu(db.Model, BaseToDict):
    __tablename__ = 'menu'
    __bind_key__ = 'jc-mock'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    parent = db.Column(db.ForeignKey('menu.id', ondelete='SET NULL', onupdate='CASCADE'), index=True)
    route = db.Column(db.String(256))
    order = db.Column(db.Integer)
    data = db.Column(db.Text)
    is_active = db.Column(db.Integer, server_default=db.FetchedValue())

    parent1 = db.relationship('Menu', remote_side=[id], primaryjoin='Menu.parent == Menu.id', backref='menus')



class Mock(db.Model, BaseToDict):
    __tablename__ = 'mocks'
    __bind_key__ = 'jc-mock'

    mock_id = db.Column(db.Integer, primary_key=True)
    mock_name = db.Column(db.String(255, 'utf8_bin'))
    mock_desc = db.Column(db.String(255, 'utf8_bin'))
    mock_url = db.Column(db.String(255, 'utf8_bin'))
    mock_method = db.Column(db.String(255, 'utf8_bin'))
    mock_response = db.Column(db.Text(collation='utf8_bin'))
    mock_is_active = db.Column(db.Integer)
    mock_system = db.Column(db.ForeignKey('link_types.link_type_id'), index=True)
    mock_create_at = db.Column(db.DateTime)
    mock_update_at = db.Column(db.DateTime)

    link_type = db.relationship('LinkType', primaryjoin='Mock.mock_system == LinkType.link_type_id', backref='mocks')



class PageView(db.Model, BaseToDict):
    __tablename__ = 'page_views'
    __bind_key__ = 'jc-mock'

    id = db.Column(db.Integer, primary_key=True)
    domain = db.Column(db.String(255, 'utf8_bin'))
    url = db.Column(db.String(255, 'utf8_bin'))
    timestamp = db.Column(db.DateTime)
    title = db.Column(db.String(255, 'utf8_bin'))
    ip = db.Column(db.String(255, 'utf8_bin'))
    referrer = db.Column(db.String(255, 'utf8_bin'))
    user_agent = db.Column(db.String(255, 'utf8_bin'))
    headers = db.Column(db.Text(collation='utf8_bin'))
    params = db.Column(db.Text(collation='utf8_bin'))



class ProgramBusines(db.Model, BaseToDict):
    __tablename__ = 'program_business'
    __bind_key__ = 'jc-mock'

    business_id = db.Column(db.Integer, primary_key=True, info='项目-业务id')
    program_id = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), info='项目id')
    business_name = db.Column(db.String(255), nullable=False, server_default=db.FetchedValue(), info='业务名称')
    create_at = db.Column(db.DateTime, server_default=db.FetchedValue(), info='创建时间')
    create_autor = db.Column(db.String(50), nullable=False, server_default=db.FetchedValue(), info='创建人')
    update_at = db.Column(db.DateTime, server_default=db.FetchedValue(), info='更新时间')
    business_cname = db.Column(db.String(200, 'utf8_bin'), info='业务名称（中文）')



class QualityInfo(db.Model, BaseToDict):
    __tablename__ = 'quality_info'
    __bind_key__ = 'jc-mock'

    id = db.Column(db.Integer, primary_key=True, info='自增长，主键')
    task_id = db.Column(db.Integer, nullable=False, info='提测任务id')
    story_change_count = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), info='需求变更次数')
    smoke_count = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), info='冒烟次数')
    reason = db.Column(db.Text(collation='utf8_bin'), info='原因')
    quality_info_create_at = db.Column(db.DateTime, server_default=db.FetchedValue(), info='创建时间')
    quality_info_update_at = db.Column(db.DateTime, server_default=db.FetchedValue(), info='更新时间')
    operator = db.Column(db.String(20, 'utf8_bin'), nullable=False, server_default=db.FetchedValue(), info='操作人')
    level = db.Column(db.Integer, info='提测质量等级0:欠佳1:良好2:优')



class Role(db.Model, BaseToDict):
    __tablename__ = 'roles'
    __bind_key__ = 'jc-mock'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64, 'utf8_bin'), unique=True)
    default = db.Column(db.Integer, index=True)
    permissions = db.Column(db.Integer)



class SonarInfo(db.Model, BaseToDict):
    __tablename__ = 'sonar_info'
    __bind_key__ = 'jc-mock'

    id = db.Column(db.Integer, primary_key=True, info='自增id')
    program_id = db.Column(db.Integer, info='项目id')
    sonar_program_key = db.Column(db.String(50, 'utf8_bin'), info='项目在sonar的项目key')
    sonar_program_name = db.Column(db.String(50, 'utf8_bin'), info='项目在sonar的项目key')
    sonar_branch = db.Column(db.String(100, 'utf8_bin'), info='新增分支名')
    sonar_key = db.Column(db.String(20, 'utf8_bin'), info='项目在sonar的项目key')
    sonar_bugs = db.Column(db.Integer, info='master拥有的bugs')
    sonar_reliability_rating = db.Column(db.String(4, 'utf8_bin'), info='master拥有的bugs等级')
    sonar_vulnerabilities = db.Column(db.Integer, info='master拥有的漏洞')
    sonar_security_rating = db.Column(db.String(4, 'utf8_bin'), info='master拥有的漏洞等级')
    sonar_sqale_index = db.Column(db.Integer, info='master拥有的债务（单位分钟）')
    sonar_sqale_rating = db.Column(db.String(4, 'utf8_bin'), info='master拥有的债务等级')
    sonar_code_smells = db.Column(db.Integer, info='master拥有的坏味道')
    sonar_coverage = db.Column(db.Float, info='master拥有的覆盖率')
    sonar_lines_to_cover = db.Column(db.Float, info='master拥有的覆盖率')
    sonar_duplicated_blocks = db.Column(db.Integer, info='master拥有的重复块')
    sonar_duplicated_lines = db.Column(db.Float, info='master拥有的重复率')
    sonar_duplicated_lines_density = db.Column(db.Float, info='master拥有的重复率')
    sonar_new_bugs = db.Column(db.Integer, info='新增的bugs')
    sonar_new_reliability_rating = db.Column(db.String(4, 'utf8_bin'), info='新增的bugs等级')
    sonar_new_vulnerabilities = db.Column(db.Integer, info='新增的漏洞')
    sonar_new_security_rating = db.Column(db.String(4, 'utf8_bin'), info='新增的漏洞等级')
    sonar_new_technical_debt = db.Column(db.Integer, info='新增的债务（单位分钟）')
    sonar_new_maintainability_rating = db.Column(db.String(4, 'utf8_bin'), info='新增的债务等级')
    sonar_new_code_smells = db.Column(db.Integer, info='新增的坏味道')
    sonar_new_coverage = db.Column(db.Float, info='新增的覆盖率')
    sonar_new_lines_to_cover = db.Column(db.Integer, info='新增的覆盖率的新增行数')
    sonar_new_duplicated_lines = db.Column(db.Float, info='新增的重复率')
    sonar_new_duplicated_lines_density = db.Column(db.Float, info='新增的重复率')
    sonar_new_lines = db.Column(db.Integer, info='新增的重复率的新增行数')
    sonar_branch_time = db.Column(db.DateTime, nullable=False, info='统计分支开始时间')
    sonar_branch_month = db.Column(db.String(2), nullable=False, server_default=db.FetchedValue(), info='统计分支月')
    sonar_branch_year = db.Column(db.String(4), nullable=False, server_default=db.FetchedValue(), info='统计分支年')
    sonar_req = db.Column(db.Text, nullable=False, info='请求结果')
    create_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='创建时间')
    update_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='更新时间')



class SysOrganization(db.Model, BaseToDict):
    __tablename__ = 'sys_organization'
    __bind_key__ = 'jc-mock'

    sys_organization_id = db.Column(db.Integer, primary_key=True)
    sys_organization_name = db.Column(db.String(30, 'utf8_bin'), nullable=False, server_default=db.FetchedValue())
    sys_organization_desc = db.Column(db.String(255, 'utf8_bin'))
    sys_organization_create_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())
    sys_organization_update_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())
    sys_organization_parent_id = db.Column(db.Integer)
    sys_del_flag = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue())



class SysProgram(db.Model, BaseToDict):
    __tablename__ = 'sys_program'
    __bind_key__ = 'jc-mock'

    sys_program_id = db.Column(db.Integer, primary_key=True)
    sys_program_name = db.Column(db.String(30, 'utf8_bin'), nullable=False)
    sys_program_desc = db.Column(db.String(255, 'utf8_bin'))
    sys_program_group_id = db.Column(db.ForeignKey('sys_organization.sys_organization_id'), index=True)
    sys_program_create_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())
    sys_program_update_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())
    sys_program_parent_id = db.Column(db.Integer)
    sys_tapd_name = db.Column(db.String(30, 'utf8_bin'), info='tapd上的项目名')
    sys_jacoco_name = db.Column(db.String(30, 'utf8_bin'), info='jacoco报告目录名')
    sys_env_params = db.Column(db.String(30), info='当前项目使用的环境变量名称')
    tapd_work_ids = db.Column(db.String(255, 'utf8_bin'), info='项目对应的tapd的workspace_id')
    sys_sonar_key = db.Column(db.String(1024), info='sonar对应的项目key')
    sys_sonar_type = db.Column(db.String(10), nullable=False, server_default=db.FetchedValue(), info='默认scan，scan-new为10.1.1.39的sonar')
    sys_is_active = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), info='1:生效，0:失效')
    git_program_ids = db.Column(db.String(512), info='sonar对应的项目key')

    sys_program_group = db.relationship('SysOrganization', primaryjoin='SysProgram.sys_program_group_id == SysOrganization.sys_organization_id', backref='sys_programs')



class TapdBugDetail(db.Model, BaseToDict):
    __tablename__ = 'tapd_bug_detail'
    __bind_key__ = 'jc-mock'

    id = db.Column(db.Integer, primary_key=True, info='记录自增id')
    bug_id = db.Column(db.String(25), nullable=False, server_default=db.FetchedValue(), info='tapd中的缺陷id')
    bug_name = db.Column(db.String(255), nullable=False, server_default=db.FetchedValue(), info='tapd中的缺陷名字')
    bug_workspace_id = db.Column(db.Integer, nullable=False, info='tapd中的缺陷所在项目id')
    bug_iteration_id = db.Column(db.String(25, 'utf8_bin'), nullable=False, server_default=db.FetchedValue(), info='tapd中的缺陷所在迭代')
    bug_story_id = db.Column(db.String(25, 'utf8_bin'), info='需求id')
    program_id = db.Column(db.Integer, nullable=False, info='测试平台项目id')
    bug_create = db.Column(db.DateTime, nullable=False, info='tapd中的缺陷创建时间')
    bug_create_date = db.Column(db.Date, nullable=False, info='tapd中的缺陷创建时间2')
    bug_status = db.Column(db.String(20), nullable=False, server_default=db.FetchedValue(), info='tapd中的缺陷状态')
    bug_severity = db.Column(db.String(20), nullable=False, info='tapd中的缺陷状态')
    find_version = db.Column(db.String(20, 'utf8_bin'), info='发现版本')
    bug_url = db.Column(db.String(255, 'utf8_bin'), nullable=False, server_default=db.FetchedValue(), info='tapd中的缺陷的ur地址')
    is_effective = db.Column(db.Integer, server_default=db.FetchedValue(), info='1:生效，0:失效')
    create_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='记录创建时间')
    update_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='记录更新时间')
    bug_dev = db.Column(db.String(20), server_default=db.FetchedValue(), info='tapd中的缺陷开发者')
    bug_tester = db.Column(db.String(20), info='tapd中的缺陷开发者')
    bug_source = db.Column(db.String(20), server_default=db.FetchedValue(), info='tapd中的缺陷开发者')
    bug_reject_time = db.Column(db.DateTime, info='tapd中的缺陷创建时间')
    bug_reopen_time = db.Column(db.DateTime, info='tapd中的缺陷创建时间')



class TapdCaseDetail(db.Model, BaseToDict):
    __tablename__ = 'tapd_case_detail'
    __bind_key__ = 'jc-mock'

    id = db.Column(db.Integer, primary_key=True, info='记录自增id')
    case_id = db.Column(db.String(25), nullable=False, server_default=db.FetchedValue(), info='tapd中的用例id')
    case_name = db.Column(db.String(255), nullable=False, server_default=db.FetchedValue(), info='tapd中的用例名字')
    case_workspace_id = db.Column(db.Integer, nullable=False, info='tapd中的用例所在项目id')
    case_iteration_id = db.Column(db.String(100), info='迭代id')
    case_story_id = db.Column(db.String(100), info='关联需求id')
    program_id = db.Column(db.Integer, nullable=False, info='测试平台项目id')
    case_create = db.Column(db.DateTime, nullable=False, info='tapd中的用例创建时间')
    case_create_date = db.Column(db.Date, nullable=False, info='tapd中的用例创建时间2')
    case_precondition = db.Column(db.Text(collation='utf8_bin'), info='前置条件')
    case_steps = db.Column(db.Text(collation='utf8_bin'), info='用例步骤')
    case_expectation = db.Column(db.Text(collation='utf8_bin'), info='预期结果')
    case_status = db.Column(db.String(20), nullable=False, server_default=db.FetchedValue(), info='tapd中的用例状态')
    case_priority = db.Column(db.String(25, 'utf8_bin'), info='用例等级')
    case_type = db.Column(db.String(25, 'utf8_bin'), info='用例类型')
    case_url = db.Column(db.String(255, 'utf8_bin'), nullable=False, server_default=db.FetchedValue(), info='tapd中的用例的ur地址')
    case_category_id = db.Column(db.String(100, 'utf8_bin'), nullable=False, server_default=db.FetchedValue(), info='用例所在目录id')
    case_creator = db.Column(db.String(20, 'utf8_bin'), info='tapd中用例的创建者')
    is_pass = db.Column(db.Integer, info='是否通过，0:失败，1:通过')
    create_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='记录创建时间')
    update_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='记录更新时间')



class TapdKeyValue(db.Model, BaseToDict):
    __tablename__ = 'tapd_key_value'
    __bind_key__ = 'jc-mock'

    id = db.Column(db.Integer, primary_key=True, info='自增长id')
    key = db.Column(db.String(30), nullable=False, server_default=db.FetchedValue(), info='key')
    type = db.Column(db.String(30), nullable=False, server_default=db.FetchedValue(), info='key的类型：map,iteartion')
    value = db.Column(db.Text, nullable=False, info='对应的tapd值')
    old_value = db.Column(db.Text, nullable=False, info='更新钱的value的值')
    workspace_id = db.Column(db.String(11), nullable=False, server_default=db.FetchedValue(), info='tapd对应的项目id')
    create_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='创建时间')
    update_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='更新时间')



class TapdStoryDetail(db.Model, BaseToDict):
    __tablename__ = 'tapd_story_detail'
    __bind_key__ = 'jc-mock'

    id = db.Column(db.Integer, primary_key=True, info='记录自增id')
    story_id = db.Column(db.String(25), nullable=False, unique=True, server_default=db.FetchedValue(), info='tapd中的需求id')
    story_name = db.Column(db.String(255), nullable=False, server_default=db.FetchedValue(), info='tapd中的需求名字')
    story_workspace_id = db.Column(db.Integer, nullable=False, info='tapd中的需求所在项目id')
    story_iteration_id = db.Column(db.String(100, 'utf8_bin'), nullable=False, info='tapd中的需求所在迭代')
    program_id = db.Column(db.Integer, nullable=False, info='测试平台项目id')
    story_create = db.Column(db.DateTime, nullable=False, info='tapd中的需求创建时间')
    story_create_date = db.Column(db.Date, nullable=False, info='tapd中的需求创建时间2')
    story_completed = db.Column(db.DateTime, info='tapd中的需求创建时间')
    story_status = db.Column(db.String(20), nullable=False, server_default=db.FetchedValue(), info='tapd中的需求状态')
    story_url = db.Column(db.String(255, 'utf8_bin'), nullable=False, server_default=db.FetchedValue(), info='tapd中的需求的ur地址')
    is_effective = db.Column(db.Integer, server_default=db.FetchedValue(), info='1:生效，0:失效')
    create_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='记录创建时间')
    update_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='记录更新时间')



class TapdTestPlanDetail(db.Model, BaseToDict):
    __tablename__ = 'tapd_test_plan_detail'
    __bind_key__ = 'jc-mock'

    id = db.Column(db.Integer, primary_key=True, info='记录自增id')
    test_plan_id = db.Column(db.String(25), nullable=False, server_default=db.FetchedValue(), info='tapd中的测试计划id')
    test_plan_name = db.Column(db.String(255), nullable=False, server_default=db.FetchedValue(), info='tapd中的测试计划名字')
    test_plan_workspace_id = db.Column(db.Integer, nullable=False, info='tapd中的测试计划所在项目id')
    test_plan_iteration_id = db.Column(db.String(100, 'utf8_bin'), nullable=False, info='tapd中的测试计划所在迭代')
    test_plan_story_id = db.Column(db.String(100, 'utf8_bin'), nullable=False, server_default=db.FetchedValue(), info='tapd中的测试计划关联需求')
    program_id = db.Column(db.Integer, nullable=False, info='测试平台项目id')
    test_plan_create = db.Column(db.DateTime, nullable=False, info='tapd中的测试计划创建时间')
    test_plan_create_date = db.Column(db.Date, nullable=False, info='tapd中的测试计划创建时间2')
    test_plan_status = db.Column(db.String(20), nullable=False, server_default=db.FetchedValue(), info='tapd中的测试计划状态')
    test_plan_url = db.Column(db.String(255, 'utf8_bin'), nullable=False, server_default=db.FetchedValue(), info='tapd中的测试计划的ur地址')
    create_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='记录创建时间')
    update_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='记录更新时间')



class TestCase(db.Model, BaseToDict):
    __tablename__ = 'test_case'
    __bind_key__ = 'jc-mock'

    case_id = db.Column(db.Integer, primary_key=True, info='自增id')
    case_name = db.Column(db.String(20, 'utf8_bin'), info='用例名称')
    case_module = db.Column(db.String(20, 'utf8_bin'), info='用例模块')
    case_system = db.Column(db.String(20, 'utf8_bin'), nullable=False, info='用例系统')
    program_id = db.Column(db.BigInteger, nullable=False, info='用例系统ID')
    create_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())



class TestEnv(db.Model, BaseToDict):
    __tablename__ = 'test_env'
    __bind_key__ = 'jc-mock'

    id = db.Column(db.Integer, primary_key=True, info='自增id')
    program_id = db.Column(db.Integer, info='项目id')
    env_id = db.Column(db.String(20, 'utf8_bin'), info='环境id')
    run_branch = db.Column(db.String(100, 'utf8_bin'), info='当前运行分支')
    create_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='创建时间')
    update_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='更新时间')
    service_names = db.Column(db.String(255), info='使用过的服务名即Jenkins名字')



class TestTask(db.Model, BaseToDict):
    __tablename__ = 'test_tasks'
    __bind_key__ = 'jc-mock'

    task_id = db.Column(db.Integer, primary_key=True, info='任务id')
    task_title = db.Column(db.String(255, 'utf8_bin'), info='任务标题')
    task_desc = db.Column(db.Text(collation='utf8_bin'), info='任务描述')
    task_system = db.Column(db.String(11, 'utf8_bin'), info='任务所属系统')
    task_business = db.Column(db.String(255, 'utf8_bin'), info='任务所属业务')
    task_create_user = db.Column(db.String(25, 'utf8_bin'), info='任务创建人')
    task_last_user = db.Column(db.String(25, 'utf8_bin'), info='任务最后修改人')
    task_create_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='任务创建时间')
    task_update_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='任务更新时间')
    task_last_run_time = db.Column(db.DateTime, info='任务最后执行时间')
    task_last_run_id = db.Column(db.String(50, 'utf8_bin'), info='任务最后执行id')
    task_version = db.Column(db.BigInteger, nullable=False, info='任务版本号')
    task_status = db.Column(db.Integer, info='任务状态：0:空闲；1:运行中 ')
    task_last_result = db.Column(db.Integer, info='最近一次任务运行状态0:失败；1:成功')
    task_run_time = db.Column(db.Integer, server_default=db.FetchedValue(), info='任务累计运行次数')
    task_type = db.Column(db.Integer, server_default=db.FetchedValue(), info='用例集类型1:正常,0:调试')
    task_last_run_env = db.Column(db.String(30, 'utf8_bin'), info='任务最后执行环境')



class TestTasksCase(db.Model, BaseToDict):
    __tablename__ = 'test_tasks_cases'
    __bind_key__ = 'jc-mock'

    id = db.Column(db.Integer, primary_key=True, info='自增id')
    task_id = db.Column(db.Integer, info='任务id')
    case_id = db.Column(db.Integer, info='用例id')
    task_version = db.Column(db.BigInteger, nullable=False, info='任务版本')
    create_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())



class TestTasksRun(db.Model, BaseToDict):
    __tablename__ = 'test_tasks_run'
    __bind_key__ = 'jc-mock'

    run_id = db.Column(db.Integer, primary_key=True, info='任务执行id')
    task_id = db.Column(db.Integer, nullable=False, info='任务id')
    run_task_id = db.Column(db.String(255, 'utf8_bin'), nullable=False, server_default=db.FetchedValue(), info='执行任务的任务id')
    run_result = db.Column(db.String, info='执行结果')
    run_begin = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='执行开始时间')
    run_end = db.Column(db.DateTime, info='执行结束时间')
    run_status = db.Column(db.Integer, server_default=db.FetchedValue(), info='执行状态')
    run_jenkins_task_id = db.Column(db.Integer, info='jenkins任务id')
    run_env_num = db.Column(db.String(30), server_default=db.FetchedValue(), info='本次运行环境')
    run_jenkins_job = db.Column(db.String(255, 'utf8_bin'), server_default=db.FetchedValue(), info='本次运行的jenkins任务')



class UserGroup(db.Model, BaseToDict):
    __tablename__ = 'user_group'
    __bind_key__ = 'jc-mock'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, index=True)
    group_Id = db.Column(db.Integer, index=True)
    create_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())
    update_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())



class UserLink(db.Model, BaseToDict):
    __tablename__ = 'user_link'
    __bind_key__ = 'jc-mock'

    user_link_id = db.Column(db.Integer, primary_key=True)
    user_link_link_id = db.Column(db.ForeignKey('links.link_id'), index=True)
    user_link_user_id = db.Column(db.ForeignKey('users.id'), index=True)
    user_link_link_count = db.Column(db.Integer, server_default=db.FetchedValue())
    user_link_create_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())
    user_link_update_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())

    user_link_link = db.relationship('Link', primaryjoin='UserLink.user_link_link_id == Link.link_id', backref='user_links')
    user_link_user = db.relationship('User', primaryjoin='UserLink.user_link_user_id == User.id', backref='user_links')



class User(db.Model, BaseToDict):
    __tablename__ = 'users'
    __bind_key__ = 'jc-mock'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64, 'utf8_bin'), unique=True)
    username = db.Column(db.String(64, 'utf8_bin'), unique=True)
    role_id = db.Column(db.ForeignKey('roles.id'), index=True)
    password_hash = db.Column(db.String(128, 'utf8_bin'))
    confirmed = db.Column(db.Integer)
    name = db.Column(db.String(64, 'utf8_bin'))
    location = db.Column(db.String(64, 'utf8_bin'))
    about_me = db.Column(db.Text(collation='utf8_bin'))
    member_since = db.Column(db.DateTime)
    last_seen = db.Column(db.DateTime)
    avatar_hash = db.Column(db.String(32, 'utf8_bin'))
    timestamp = db.Column(db.DateTime)
    avatar = db.Column(db.String(255, 'utf8_bin'))

    role = db.relationship('Role', primaryjoin='User.role_id == Role.id', backref='users')
