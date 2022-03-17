import os
import logging
from logging.handlers import RotatingFileHandler
import stat
basedir = os.path.abspath(os.path.dirname(__file__))


class AutoTestConfig:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
    WTF_CSRF_SECRET_KEY = "my csrf key is easy"
    SSL_DISABLE = False
    DOMAIN = "http://127.0.0.1:6868"
    DB_IP = None
    environment = os.environ.get("environment", 'dev')
    logging.info('environment', environment)
    if environment == 'test':
        DB_IP = '10.1.0.15'
        DEBUG = False
    elif environment == 'dev':
        DB_IP = '127.0.0.1'
        DEBUG = True
    SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://root:Coh8Beyiusa7@{DB_IP}:3306/auto-test?charset=utf8'
    SQLALCHEMY_DICT = {
            'china': {
                "repay": "mysql+pymysql://root:Coh8Beyiusa7@" + DB_IP + ":3306/rbiz{0}",
                "grant": "mysql+pymysql://root:Coh8Beyiusa7@" + DB_IP + ":3306/gbiz{0}",
                "biz_central": "mysql+pymysql://root:Coh8Beyiusa7@" + DB_IP + ":3306/biz{0}"
            },
            'ind': {
                "repay": "mysql+pymysql://biz_test:1Swb3hAN0Hax9p@127.0.0.1:{1}/global_rbiz{0}",
                "grant": "mysql+pymysql://biz_test:1Swb3hAN0Hax9p@127.0.0.1:{1}/global_gbiz{0}",
                "ssh": {
                    "ssh_proxy_host": "47.116.2.104",
                    "ssh_remote_host": "rm-uf60ec1554fou12qk33150.mysql.rds.aliyuncs.com",
                    "ssh_user_name": "ssh-proxy",
                    "ssh_private_key": "./resource/dx_ssh_proxy",
                    "ssh_bind_port": 3331
                }
            },
            'phl': {
                "repay": "mysql+pymysql://troot:QZOzz46rUjs$$PIKL8@127.0.0.1:{1}/phl_rbiz{0}",
                "grant": "mysql+pymysql://troot:QZOzz46rUjs$$PIKL8@127.0.0.1:{1}/phl_gbiz{0}",
                "ssh": {
                    "ssh_proxy_host": "47.116.2.104",
                    "ssh_remote_host": "rm-uf6589ct883rjc052.mysql.rds.aliyuncs.com",
                    "ssh_user_name": "ssh-proxy",
                    "ssh_private_key": "./resource/dx_ssh_proxy",
                    "ssh_bind_port": 3511
                }
            },
            'mex': {
                "repay": "mysql+pymysql://root:QZOzz46rUjs$$PIKL8@127.0.0.1:{1}/mex_rbiz{0}",
                "grant": "mysql+pymysql://root:QZOzz46rUjs$$PIKL8@127.0.0.1:{1}/mex_gbiz{0}",
                "ssh": {
                    "ssh_proxy_host": "47.116.2.104",
                    "ssh_remote_host": "rm-uf6z2o8w9rure4as4.mysql.rds.aliyuncs.com",
                    "ssh_user_name": "ssh-proxy",
                    "ssh_private_key": "./resource/dx_ssh_proxy",
                    "ssh_bind_port": 3521
                }
            },
            'tha': {
                "repay": "mysql+pymysql://root:0Q^0bBURuSvS3#PB@127.0.0.1:{1}/tha_rbiz{0}",
                "grant": "mysql+pymysql://root:0Q^0bBURuSvS3#PB@127.0.0.1:{1}/tha_gbiz{0}",
                "ssh": {
                    "ssh_proxy_host": "47.116.2.104",
                    "ssh_remote_host": "rm-uf6seazei9e71x831.mysql.rds.aliyuncs.com",
                    "ssh_user_name": "ssh-proxy",
                    "ssh_private_key": "./resource/dx_ssh_proxy",
                    "ssh_bind_port": 3511
                }
            }
        }
    # SQLALCHEMY设置配置
    SQLALCHEMY_COMMIT_ON_TEARDOWN = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = False
    SQLALCHEMY_POOL_SIZE = 100
    SQLALCHEMY_MAX_OVERFLOW = 20
    SQLALCHEMY_POOL_TIMEOUT = 10
    mode = 0o0600 | stat.S_IRUSR
    log_base_dir = os.path.dirname(basedir)
    LOG_PATH = os.path.join(log_base_dir, 'logs')
    if not os.path.exists(LOG_PATH):
        os.mkdir(LOG_PATH)
    LOG_PATH_ERROR = os.path.join(LOG_PATH, 'error.log')
    if not os.path.exists(LOG_PATH_ERROR):
        open(LOG_PATH_ERROR, 'w').close()
    LOG_PATH_INFO = os.path.join(LOG_PATH, 'info.log')
    if not os.path.exists(LOG_PATH_INFO):
        open(LOG_PATH_INFO, 'w').close()
    LOG_FILE_MAX_BYTES = 100 * 1024 * 1024

    @staticmethod
    def init_app(app):
        # formatter = logging.Formatter(
        #     '%(asctime)s %(levelname)s %(process)d %(thread)d '
        #     '%(pathname)s %(lineno)s %(message)s')
        # formatter = logging.Formatter("%(asctime)s %(levelname)s %(funcName)s: %(message)s")

        formatter = logging.Formatter(
            '%(asctime)s %(levelname)s %(pathname)s %(funcName)s %(lineno)s %(message)s')

        # FileHandler Info
        file_handler_info = RotatingFileHandler(filename=AutoTestConfig.LOG_PATH_INFO)
        file_handler_info.setFormatter(formatter)
        file_handler_info.setLevel(logging.INFO)
        info_filter = logging.Filter()
        info_filter.filter = lambda record: record.levelno >= logging.INFO
        file_handler_info.addFilter(info_filter)
        app.logger.addHandler(file_handler_info)

        # FileHandler Error
        file_handler_error = RotatingFileHandler(filename=AutoTestConfig.LOG_PATH_ERROR)
        file_handler_error.setFormatter(formatter)
        file_handler_error.setLevel(logging.ERROR)
        error_filter = logging.Filter()
        error_filter.filter = lambda record: record.levelno >= logging.ERROR
        file_handler_error.addFilter(error_filter)
        app.logger.addHandler(file_handler_error)


class InfoFilter(logging.Filter):

    def filter(self, record):
        """only use INFO
        筛选, 只需要 INFO 级别的log
        :param record:
        :return:
        """
        if logging.INFO <= record.levelno <= logging.ERROR:
            # 已经是INFO级别了
            # 然后利用父类, 返回 1
            return super().filter(record)
        else:
            return 0
