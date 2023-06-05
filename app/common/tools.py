import collections
import json
from datetime import datetime
from datetime import date as datetime_date
from functools import wraps
import socket
from random import random
import decimal
from functools import reduce

import requests
from dateutil.relativedelta import relativedelta

from app.common.log_util import LogUtil


def get_json_path(source):
    """
    get_path获取到json path的list，然后组装为正在的jsonpath返回
    :param source:
    :return:
    """

    def get_path(source_json):
        paths = []
        if isinstance(source_json, collections.abc.MutableMapping):  # 如果是字典类型
            for k, v in source_json.items():  #
                paths.append([k])  # 先将key添加
                paths += [[k] + x for x in get_path(v)]  # 循环判断value类型
        elif isinstance(source_json, collections.abc.Sequence) and not isinstance(source_json, str):  # 如果是列表或字符串
            for i, v in enumerate(source_json):  # i为顺序，v为值
                paths.append([i])  # 先将key添加
                paths += [[i] + x for x in get_path(v)]  # 循环判断value类型
        return paths

    path_seq = get_path(source)
    path_list = []
    for path in path_seq:
        path_temp = "$"
        for value in path:
            if isinstance(value, str):
                path_temp = path_temp + '.' + str(value)
            elif isinstance(value, int):
                path_temp = path_temp + '[' + str(value) + ']'
            else:
                pass
        path_list.append(path_temp)
    return path_list


class PrintCallLog(object):

    def __call__(self, func):
        @wraps(func)
        def wrapped_function(*args, **kwargs):
            print('======================{0} begin===================='.format(func.__name__))
            ret = func(*args, **kwargs)
            print('======================{0} end===================='.format(func.__name__))
            return ret

        return wrapped_function


class CheckExist(object):

    def __init__(self, *, check=True):
        self.check = check

    def __call__(self, func):

        @wraps(func)
        def wrapped_function(*args, **kwargs):
            print('{0} called begin'.format(func.__name__))
            if func.__name__.startswith("get_") and func.__name__.endswith("_info"):
                prefix = func.__name__[4:-5]
                print(prefix)
                new_kwargs = {}
                for kwarg, k_value in kwargs.items():
                    if prefix not in kwarg and k_value:
                        print(kwarg)
                        new_kwargs['{0}_{1}'.format(prefix, kwarg)] = k_value
                if new_kwargs:
                    kwargs.update(new_kwargs)
                else:
                    raise ValueError('all args is null!')
            ret = func(*args, **kwargs)

            def add(x, y):
                return '{0}, {1}'.format(x, y)

            str_args = ''
            if len(args) > 3:
                str_args = reduce(add, args[2:], )
                print('-------args is {0} begin------'.format(str_args))
            if not ret and self.check:
                raise ValueError('not found the {0} record in {1}!'.format(args[1], args[0].server_name))
            print('{0} called end'.format(func.__name__))
            if str_args:
                print('-------args is {0} end------'.format(str_args))
            return ret
        return wrapped_function


def generate_sql(sql_param, split):
    sql = ""
    if isinstance(sql_param, dict):
        for key, value in sql_param.items():
            if isinstance(value, tuple):
                sql += " {0}={1} and ".format(key, value[0]) if \
                    len(value) == 1 else " {0} in {1} and ".format(key, value)
            elif 'DATE_' in value:
                sql += str(key) + "=" + str(value) + " " + str(split) + " "
            else:
                sql += str(key) + "='" + str(value) + "' " + str(split) + " "
    return sql[:(-len(split) - 1)]


def trans_data(result):
    if isinstance(result, dict):
        result = [result]
    if isinstance(result, (list, tuple)):
        for r in result:
            for key, value in r.items():
                if isinstance(value, datetime):
                    r[key] = value.strftime("%Y-%m-%d %H:%M:%S")
                elif isinstance(value, decimal.Decimal):
                    temp = str(value)
                    tem_value = temp.split(".")
                    if len(tem_value) > 1 and int(tem_value[1]) == 0:
                        r[key] = tem_value[0]
                    else:
                        r[key] = temp
    return result


def get_port():
    port = 0
    for i in range(10):
        ip = '127.0.0.1'
        port = random.randint(20000, 31000)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            result = s.connect_ex((ip, port))
        if result == 0:
            LogUtil.log_info("port:%s already been used" % port)
        else:
            LogUtil.log_info("port:%s already been choiced" % port)
            break
        if i == 9:
            raise Exception("未选到合适的端口")
    return port


def parse_resp_body(resp):
    try:
        content = json.loads(resp.text)
    except Exception as e:
        print(e)
        content = resp.text
    resp = {
        "status_code": resp.status_code,
        "content": content,
        "headers": resp.headers,
        "cookies": requests.utils.dict_from_cookiejar(resp.cookies),
        "reason": resp.reason
    }
    return resp


def get_date(fmt="%Y-%m-%d %H:%M:%S", date=None, timezone=None, is_str=False, **kwargs):
    date = date if date is not None else datetime.now(timezone)
    date = date if isinstance(date, (datetime, datetime_date)) \
        else datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
    new_data = date + relativedelta(**kwargs)
    return new_data.strftime(fmt) if is_str else new_data
