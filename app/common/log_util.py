
# -*- coding: utf-8 -*-
import os
import logging
from logging.handlers import TimedRotatingFileHandler

LOG_PATH = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))) +\
           '/logs/supervisor/'
LOGGING_FILENAME = "auto_test.log"
LOGGING_SUFFIX = "%Y%m%d"
LOGGING_WHEN = "midnight"
LOGGING_LEVEL = "INFO"
LOGGING_INTERVAL = 1
LOGGING_BACKUPCOUNT = 7
LOGGING_DATEFMT = "%Y-%m-%d %H:%M:%S"
# LOGGING_FMT = "%(message)s %(asctime)s %(levelname)s %(funcName)s"
LOGGING_FMT = "%(message)s"


# 初始化日志对象
def init_logger():
    log = logging.getLogger()
    log.setLevel(logging.INFO)
    # 设置控制台输出
    consolehandler = logging.StreamHandler()
    consolehandler.setLevel(logging.INFO)
    formatter = logging.Formatter(LOGGING_FMT)
    consolehandler.setFormatter(formatter)
    log.addHandler(consolehandler)
    # 设置日志文件输出
    # 日志文件所在的目录
    filename_directory = LOG_PATH
    # 创建日志文件目录
    if not os.path.exists(filename_directory):
        os.makedirs(filename_directory)
    filename = os.path.join(filename_directory, LOGGING_FILENAME)
    filehandler = TimedRotatingFileHandler(filename, when=LOGGING_WHEN, interval=LOGGING_INTERVAL,
                                           backupCount=LOGGING_BACKUPCOUNT)
    filehandler.setLevel(LOGGING_LEVEL)
    filehandler.suffix = LOGGING_SUFFIX
    formatter = logging.Formatter(fmt=LOGGING_FMT, datefmt=LOGGING_DATEFMT)
    filehandler.setFormatter(formatter)
    log.addHandler(filehandler)
    return log


logger = init_logger()


class LogUtil(object):

    @classmethod
    def log(cls, msg):
        logger.info(msg)

    @classmethod
    def log_info(cls, msg):
        logger.info(msg)

    @classmethod
    def log_error(cls, msg):
        logger.error(msg)

    @classmethod
    def log_debug(cls, msg):
        logger.debug(msg)
