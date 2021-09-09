import json
from app.common.http_util import Http
from app.common.log_util import LogUtil
import re

BASE_URL = "http://easy-mock.k8s-ingress-nginx.kuainiujinke.com"
ACCOUNT = {
    "user": "carltonliu",
    "password": "lx19891115"
}

MOCK_PROJECT_DICT = {
    "gbiz_auto_test": {
        "name": "gbiz",
        "id": "5f9bfaf562081c0020d7f5a7"
    },
    "global_gbiz_auto_test": {
        "name": "nbfc",
        "id": "5e465f0ed53ef1165b982496"
    },
    "rbiz_auto_test": {
        "name": "rbiz_auto_test",
        "id": "5de5d515d1784d36471d6041"
    },
    "contract": {
        "name": "contract",
        "id": "6007a8b11242fa00160534bb"
    },
    "global_rbiz_auto_test": {
        "name": "global_rbiz_auto_test",
        "id": "5e46037fd53ef1165b98246e"
    },
    "global_payment_auto_test": {
        "name": "global_payment_auto_test",
        "id": "5f9640cc62081c0020d7f560"
    },
    "global_payment_scb_test": {
        "name": "global_payment_auto_test",
        "id": "5f33abd683be280020b70ad8"
    },
    "dcs_auto_test": {
        "name": "dcs",
        "id": "5bd800c7b820c00016b21ddb"
    },
    "old_dcs_auto_test": {
        "name": "dcs",
        "id": "5caeea78c2c04c0020a98498"
    }
}


class EasyMock(object):

    login_url = "{0}/api/u/login".format(BASE_URL)
    get_api_id_url = "{0}/api/mock?project_id={1}&page_size=2000&page_index=1"
    update_url = "{0}/api/mock/update".format(BASE_URL)
    create_url = "{0}/api/mock/create".format(BASE_URL)

    def __init__(self, project, check_req=True, return_req=False):
        """
        :param project: 项目名，easymock_config.mock_project的key
        :param check_req: bool，是否检查_req请求数据
        :param return_req:  bool，是否返回_req请求数据，返回到"origin_req"
        """
        self.token = ""
        self.project = project
        self.project_id = MOCK_PROJECT_DICT[project]['id']
        self.project_name = MOCK_PROJECT_DICT[project]['name']
        self.header = None
        self.login(ACCOUNT['user'], ACCOUNT['password'])
        self.check_req = check_req
        self.return_req = return_req

    def login(self, user, password):
        body = {"name": user,
                "password": password}
        header = {"Content-Type": "application/json"}
        resp = Http.http_post(self.login_url, body, header)
        self.token = "Bearer " + resp["data"]["token"]
        self.header = {"Content-Type": "application/json;charset=UTF-8",
                       "Authorization": self.token}

    def get_api_list(self):
        url = self.get_api_id_url.format(BASE_URL, self.project_id)
        resp = Http.http_get(url,  headers=self.header)
        return resp

    def get_api_info_by_api(self, api, method):
        api_list = self.get_api_list()
        api_info = {}
        for mock in api_list["data"]["mocks"]:
            if mock["url"] == api and (method is None or (method is not None and mock['method'] == method)):
                api_info["id"] = mock["_id"]
                api_info["url"] = mock["url"]
                api_info["method"] = mock["method"]
                api_info["mode"] = ""
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
        api_info["mode"] = mode if isinstance(mode, str) else json.dumps(mode, ensure_ascii=False)
        if self.return_req:
            api_info["mode"] = self.append_origin_req(api_info["mode"])
        resp = Http.http_post(self.update_url, api_info, headers=self.header)
        return resp

    def update_by_api_id(self, api_id, api, mode, method="post"):
        api_list = self.get_api_list()
        api_info = {}
        for mock in api_list["data"]["mocks"]:
            if mock["_id"] == api_id and mock['method'] == method:
                api_info["id"] = api_id
                api_info["url"] = api
                api_info["method"] = mock["method"]
                api_info["mode"] = ""
                api_info["description"] = mock["description"]
                break
        if len(api_info) == 0:
            raise Exception("未找到api")
        api_info["mode"] = mode if isinstance(mode, str) else json.dumps(mode, ensure_ascii=False)
        resp = Http.http_post(self.update_url, api_info, headers=self.header)
        return resp

    def create_project(self, project_id):
        api_list = self.get_api_list()
        for api in api_list["data"]["mocks"]:
            api_info = {"url": "" + api["url"],
                        "method": api["method"],
                        "mode": api["mode"],
                        "description": api["description"],
                        "project_id": project_id}

            Http.http_post(self.create_url, api_info, headers=self.header)

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
