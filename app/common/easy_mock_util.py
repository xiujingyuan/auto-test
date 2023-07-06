import json
import time
from random import random

from app.common.http_util import Http
from app.common.log_util import LogUtil
import re
from jsonpath_ng import parse
import datetime
from dateutil.relativedelta import relativedelta

BASE_URL = "https://easy-mock.k8s-ingress-nginx.kuainiujinke.com"
CD_BIZ_PROJECT_ID = '5b555fbc3a0f770020651dda'
ACCOUNT = {
    "user": "carltonliu",
    "password": "lx19891115"
}


def check_login(func):
    def wrapper(self, *kw, **kwargs):
        if not self.token or not self.header:
            self.login(ACCOUNT['user'], ACCOUNT['password'])
        ret = func(self, *kw, **kwargs)
        return ret
    return wrapper


def check_project_id(func):
    def wrapper(self, *args, **kwargs):
        if self.project_id is None:
            self.project_id = self.get_project_id(self.project_name)
        ret = func(self, *args, **kwargs)
        return ret
    return wrapper


class EasyMock(object):

    login_url = "{0}/api/u/login".format(BASE_URL)
    get_api_id_url = "{0}/api/mock?project_id={1}&page_size=2000&page_index=1"
    get_project_id_url = "{0}/api/project?page_size=300&page_index=1&keywords=&type=&group={1}&filter_by_author=0"
    update_url = "{0}/api/mock/update".format(BASE_URL)
    delete_url = "{0}/api/project/delete".format(BASE_URL)
    create_api_url = "{0}/api/mock/create".format(BASE_URL)
    create_project_url = "{0}/api/project/create".format(BASE_URL)

    def __init__(self, mock_name, check_req=True, return_req=False):
        """
        :param project: 项目名，easymock_config.mock_project的key
        :param check_req: bool，是否检查_req请求数据
        :param return_req:  bool，是否返回_req请求数据，返回到"origin_req"
        """
        self.token = ""
        self.project_name = mock_name
        self.project_id = None
        self.header = None
        self.check_req = check_req
        self.return_req = return_req

    @staticmethod
    def get_date(fmt="%Y-%m-%d %H:%M:%S", date=None, timezone=None, is_str=False, **kwargs):
        date = date if date is not None else datetime.datetime.now(timezone)
        new_data = date + relativedelta(**kwargs)
        return new_data.strftime(fmt) if is_str else new_data

    @staticmethod
    def cal_days(str1, str2):
        date1 = datetime.datetime.strptime(str1[0:10], "%Y-%m-%d") if isinstance(str1, str) else str1
        date2 = datetime.datetime.strptime(str2[0:10], "%Y-%m-%d") if isinstance(str2, str) else str2
        date1 = date1.date() if isinstance(date1, datetime.datetime) else date1
        date2 = date2.date() if isinstance(date2, datetime.datetime) else date2
        num = (date2 - date1).days
        return num

    @staticmethod
    def __create_req_key__(item_no, prefix=''):
        return "{0}{1}_{2}".format(prefix, item_no, int(time.time()))

    @staticmethod
    def __get_new_value__(content, json_path_dict):
        replace_dict = {}
        # 查找function
        for index in range(content.count('function')):
            a_index = content.find('function')
            b_index = content.find('}', content.find('})') + 1)
            spect_str = content[a_index:b_index + len('}')]
            spect_key = '"spect_str_' + str(index) + '"'
            replace_dict[spect_key] = spect_str
            content = content.replace(spect_str, spect_key)
        content = json.loads(content)
        # 替换key
        for json_path, new_value in json_path_dict.items():
            json_path_expr = parse(json_path)
            b = json_path_expr.find(content)
            if not b:
                LogUtil.log_error('not fount the json path: {0} in {1}'.format(json_path, content))
            else:
                json_path_expr.update(content, new_value)
        # 替换回function
        content = json.dumps(content, ensure_ascii=False)
        for replace_key, replace_value in replace_dict.items():
            content = content.replace(replace_key, replace_value)
        return content

    def login(self, user, password):
        body = {"name": user,
                "password": password}
        header = {"Content-Type": "application/json"}
        resp = Http.http_post(self.login_url, body, header)
        self.token = "Bearer " + resp["data"]["token"]
        self.header = {"Content-Type": "application/json;charset=UTF-8",
                       "Authorization": self.token}

    @check_login
    def get_api_list(self, project_id):
        url = self.get_api_id_url.format(BASE_URL, project_id)
        resp = Http.http_get(url,  headers=self.header)
        return resp

    @check_project_id
    def get_api_info_by_api(self, api, method):
        api_list = self.get_api_list(self.project_id)
        api_info = {}
        for mock in api_list["data"]["mocks"]:
            print(mock["url"] == api and (method is None or (method is not None and mock['method'] == method)), mock["url"], mock["url"] == api, method)
            if mock["url"] == api and (method is None or (method is not None and mock['method'] == method)):
                api_info["id"] = mock["_id"]
                api_info["url"] = mock["url"]
                api_info["method"] = mock["method"]
                api_info["mode"] = mock["mode"]
                api_info["description"] = mock["description"]
                break
        if len(api_info) == 0:
            raise Exception("未找到api")
        return api_info

    def update(self, api, mode, method=None):
        """
        mode支持传入两种方式，json和str，传入json后内部会自己转为str
        :param api: 需要修改的api的url
        :param mode:需要替换的参数
        :param method 方法类型
        :return:
        """
        api_info = self.get_api_info_by_api(api, method)
        if 'function' in api_info['mode']:
            pass
        api_info["mode"] = mode if isinstance(mode, str) else json.dumps(mode, ensure_ascii=False)
        if self.return_req:
            api_info["mode"] = self.append_origin_req(api_info["mode"])
        resp = Http.http_post(self.update_url, api_info, headers=self.header)
        return resp

    def update_by_json_path(self, api, json_path_dict, method=None):
        """
        :param api: 需要修改的api的url
        :param json_path_dict:jsonpath的字典
        :param method 方法类型
        :return:
        """
        api_info = self.get_api_info_by_api(api, method)
        new_value = self.__get_new_value__(api_info['mode'], json_path_dict)
        api_info['mode'] = new_value
        if self.return_req:
            api_info["mode"] = self.append_origin_req(api_info["mode"])
        resp = Http.http_post(self.update_url, api_info, headers=self.header)
        return resp

    def update_by_value(self, api, value, method=None):
        """
        :param api: 需要修改的api的url
        :param value:jsonpath的字典
        :param method 方法类型
        :return:
        """
        api_info = self.get_api_info_by_api(api, method)
        api_info['mode'] = json.dumps(value, ensure_ascii=False) if not isinstance(value, str) else value
        resp = Http.http_post(self.update_url, api_info, headers=self.header)
        return resp

    def update_by_api_id(self, api_id, api, mode, method="post"):
        api_list = self.get_api_list(self.project_id)
        api_info = {}
        for mock in api_list["data"]["mocks"]:
            if mock["_id"] == api_id and mock['method'] == method:
                api_info["id"] = api_id
                api_info["url"] = api
                api_info["method"] = mock["method"]
                api_info["mode"] = ""
                api_info["description"] = mock["description"]
                break
        if not api_info:
            raise Exception("未找到api")
        api_info["mode"] = mode if isinstance(mode, str) else json.dumps(mode, ensure_ascii=False)
        resp = Http.http_post(self.update_url, api_info, headers=self.header)
        return resp

    @check_login
    def get_project_id_list(self, group=''):
        group = group if group else CD_BIZ_PROJECT_ID
        resp = Http.http_get(self.get_project_id_url.format(BASE_URL, group), headers=self.header)
        return resp

    @check_login
    def get_project_id(self, name, group='', is_del=False):
        project_id_list = self.get_project_id_list(group=group)

        def find_project_id():
            for project in project_id_list["data"]:
                if project['name'] == name:
                    return project['_id']
            return None

        finial = find_project_id()
        if is_del and finial is None:
            raise ValueError("not found the project's id with name:{0}".format(name))
        if finial is None:
            self.create_project(name, group=group)
            project_id_list = self.get_project_id_list(group=group)
            finial = find_project_id()
            if finial is None:
                raise ValueError("not found the project's id with name:{0}".format(name))
            return finial
        return finial

    @check_project_id
    def get_mock_base_url(self):
        return '{0}/mock/{1}/{2}'.format(BASE_URL, self.project_id, self.project_name)

    @check_login
    def create_project(self, name, group='', desc='', url=''):
        """
        创建新项目
        :param name: 新建项目名字
        :param group: 默认CD-BIZ项目组
        :param desc: 项目描述
        :param url:项目地址
        :return:
        """
        project_info = {
            "id": "",
            "name": name,
            "group": group if group else CD_BIZ_PROJECT_ID,
            "swagger_url": "",
            "description": desc,
            "url": "/{0}".format(url if url else name),
            "members": []
        }
        ret = Http.http_post(self.create_project_url, project_info, headers=self.header)
        return ret

    def delete_project(self, project_name):
        self.project_id = self.get_project_id(project_name, is_del=True)
        req = {'id': self.project_id}
        ret = Http.http_post(self.delete_url, req, headers=self.header)
        return ret

    def copy_increment_project(self, source_project_name, to_project_name):
        self.project_name = source_project_name
        self.project_id = self.get_project_id(self.project_name)
        source_api_list = self.get_api_list(self.project_id)
        if not source_api_list:
            raise ValueError("the source project's api list is empty with name is :{0}".format(source_project_name))
        project_name = to_project_name
        to_project_id = self.get_project_id(project_name)
        to_api_list = self.get_api_list(to_project_id)
        to_api_url = tuple(map(lambda x: x['url'], to_api_list["data"]["mocks"]))
        for api in source_api_list["data"]["mocks"]:
            if api['url'] not in to_api_url:
                api_info = {"url": "" + api["url"],
                            "method": api["method"],
                            "mode": api["mode"],
                            "description": api["description"],
                            "project_id": to_project_id}
                Http.http_post(self.create_api_url, api_info, headers=self.header)

    def copy_project(self, source_project_name, to_project_name, new_group=''):
        """
        复制当期项目的mock到新项目
        :param source_project_name: 来源项目名字
        :param to_project_name: 目标项目名字
        :param new_group: 新项目所在组,默认cd_biz
        :return:
        """
        self.project_name = source_project_name
        self.project_id = self.get_project_id(self.project_name)
        api_list = self.get_api_list(self.project_id)
        if not api_list:
            raise ValueError("the source project's api list is empty with name is :{0}".format(source_project_name))
        new_project_id = self.get_project_id(to_project_name, group=new_group)
        for api in api_list["data"]["mocks"]:
            api_info = {"url": "" + api["url"],
                        "method": api["method"],
                        "mode": api["mode"],
                        "description": api["description"],
                        "project_id": new_project_id}
            Http.http_post(self.create_api_url, api_info, headers=self.header)

    @staticmethod
    def append_origin_req(data):
        """
        把最后一个'}'替换成追加了_req数据的串
        :param data:
        :return:
        """
        req_data = ', "origin_req":{' \
                   '"_req.url":function({_req}){return _req.url},' \
                   '"_req.path":function({_req}){return _req.path},' \
                   '"_req.body":function({_req}){return _req.body},' \
                   '"_req.query":function({_req}){return _req.query}' \
                   '}}'
        replace_reg = re.compile("\\}$")
        data = replace_reg.sub(req_data, data)
        return data

    @staticmethod
    def get_str_by_type(key):
        return '"%s"' % key if type(key) == str else key

    def get_mock_result_with_check(self, origin_data, check_point_dict):
        """
        带检查点的mock结果
        :param origin_data: 正常的响应数据
        :param check_point_dict: 检查点
         - GET请求，推荐检查 path + query；
         - POST请求，推荐检查 path + body；
        eg.
        {
            "path": "/mock/5f9bfaf562081c0020d7f5a7/gbiz/tongrongmiyang/tongrongmiyang/loanApply",
            "body": {
                "loanOrder.termNo": 6,
                "loanOrder.account": "4000.00"
            },
            "query": {
                "loanOrder.termNo": 6,
                "loanOrder.account": "4000.00"
            }
        }
        :return: 需要检查请求参数时，返回带检查点的响应式mock结果；无需检查请求参数时，返回原始数据
        """
        # 需要检查_req参数，组装function
        if self.check_req:
            demo = """function({_req}) {
                    if (%s) {
                      return %s
                    } else {
                      return "REQ_CHECK_FAILED: %s"
                    }
                  }"""
            if_condition = "true"
            fail_message = ""
            for k, v in check_point_dict.items():
                if type(v) == str:
                    if_condition += " && _req.%s === %s" % (k, self.get_str_by_type(v))
                    fail_message += "%s: expect[%s], actual[\" + %s + \"]; " % (k, v, "_req.%s" % (k))
                elif type(v) == dict:
                    for key, value in v.items():
                        if_condition += " && _req.%s.%s === %s" % (k, key, self.get_str_by_type(value))
                        fail_message += "%s.%s: expect[%s], actual[\" + %s + \"]; " % (
                            k, key, value, "_req.%s.%s" % (k, key))
            result = demo % (
                if_condition, origin_data if isinstance(origin_data, int) else self.get_str_by_type(origin_data),
                fail_message)
            return result
        # 不需要检查_req，返回原始数据
        else:
            return self.get_str_by_type(origin_data)


if __name__ == "__main__":
    test = EasyMock('rbiz_manual_test')
    print(test.copy_increment_project('rbiz_manual_test', 'rbiz_auto_test'))
    # test.delete_project('test51213')

