import json
from jsonpath_ng import parse

from app.common.http_util import Http
from app.common.log_util import LogUtil
from app.model.Model import NacosConfig

NACOS_DOMAIN_DICT = {
    "china": "nacos.k8s-ingress-nginx.kuainiujinke.com",
    "tha": "nacos-test-tha.starklotus.com",
    "phl": "nacos-test-phl.starklotus.com",
    "mex": "nacos-test-mex.starklotus.com",
    "ind": "nacos-test-ind.starklotus.com",
    "pak": "nacos-test-pak.starklotus.com"
}


class Nacos(object):

    login_url = "http://{0}/nacos/v1/auth/login"
    get_config_id_url = "http://{0}/nacos/v1/cs/configs?search=accurate&dataId={1}&group=&appName=&config_tags=" \
              "&pageNo=1&pageSize=10&tenant={2}&namespaceId={3}"
    update_config_url = "http://{0}/nacos/v1/cs/configs"
    get_config_content_url = "http://{0}/nacos/v1/cs/configs?search=accurate&dataId={1}&group=&appName=&config_tags=" \
              "&pageNo=1&pageSize=10&tenant={2}&namespaceId={2}"
    get_config_url = "http://{0}/nacos/v1/cs/configs"

    def __init__(self, country, tenant, username="nacos", password="nacos"):
        self.username = username
        self.password = password

        self.domain = NACOS_DOMAIN_DICT[country]
        self.cookies = None
        self.authorization = None
        self.tenant = tenant
        self.old_value = {}

    def login(self):
        try:
            url = self.login_url.format(self.domain)
            req_body = {
                "username": self.username,
                "password": self.password,
                "namespaceId": ""
            }
            resp = Http.parse_resp_body('post', url, data=req_body,
                                        headers={"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"})
            response_headers = resp["headers"]
            self.authorization = response_headers["Authorization"]
            self.cookies = resp["cookies"]
        except Exception as e:
            print(e)
            pass

    def get_config_id(self, config_name):
        url = self.get_config_id_url.format(self.domain, config_name, self.tenant, self.tenant)
        resp = Http.parse_resp_body('get', url, headers={"Authorization": self.authorization},
                                    cookies=self.cookies)
        config_id = resp['content']["pageItems"][0]["id"]
        return config_id

    def update_nacos_config(self, nacos_config_key):
        """
        根据传递的nacos_config的key来查询需要ginger的nacos的配置名和期望的值，实现页面可以随意配置
        :param nacos_config_key: 在数据库nacos_config里的配置的key，比如update_repay_paysvr_by_mock,
        update_repay_paysvr_by_gate
        :return: 无
        """
        get_config = NacosConfig.query.filter(NacosConfig.nacos_config_key == nacos_config_key).first()
        nacos_config_value = json.loads(get_config.nacos_config_value)
        self.update_config_by_json_path(get_config.nacos_config_name, nacos_config_value)

    def update_config(self, config_name, content, group="KV", types="json"):
        configs_id = self.get_config_id(config_name)
        url = self.update_config_url.format(self.domain)
        req_body = {
            "dataId": config_name,
            "group": group,
            "content": content,
            "appName": None,
            "desc": None,
            "config_tags": None,
            "tenant": self.tenant,
            "createTime": "1581592882000",
            "modifyTime": "1581592882000",
            "createUser": None,
            "createIp": "118.242.27.98",
            "use": None,
            "effect": None,
            "schema": None,
            "configTags": None,
            "md5": "be65d4de7d98e9877adbfd2416069e05",
            "id": configs_id,
            "type": types,
        }
        Http.http_post(url, req_body,
                       headers={"content-type": "application/x-www-form-urlencoded",
                                "Authorization": self.authorization},
                       cookies=self.cookies)

    def get_config_content(self, config_name, group='KV'):
        """
        获取给定配置文件的id
        :param config_name:配置文件的id
        :param group:配置文件类型，KV，SYSTEM
        :return:返回配置文件的内容
        """
        config_ret = self.get_config(config_name, group)
        return json.loads(config_ret['content'])

    def get_config(self,  config_name, group='KV'):
        url = self.get_config_url.format(self.domain)
        headers = {"Authorization": self.authorization}
        params = {
            "dataId": config_name,
            "group": group,
            "namespaceId": self.tenant,
            "tenant": self.tenant,
            "show": "all"
        }
        resp = Http.parse_resp_body('get', url, params=params, headers=headers, cookies=self.cookies)
        return resp["content"]

    def incremental_update_config(self, config_name, group, **kwargs):
        config = self.get_config(config_name, group)
        if config['type'] == "json":
            content = json.loads(config['content'])
            for key, value in kwargs.items():
                content[key] = value
        else:
            # TODO:其他类型增量更新config
            content = config['content']
        self.update_config(config_name, content, group)

    def update_config_by_json_path(self, config_name, json_path_dict, group='KV'):
        # $.store.book [0].title  ----json path
        config = self.get_config(config_name, group)
        if not config['type'] == "json":
            raise TypeError("need type = json, but {0} type found".format(config['type']))
        if not isinstance(json_path_dict, dict):
            raise TypeError("need dict, but {0} type found".format(type(json_path_dict)))
        content = json.loads(config['content'])
        for json_path, new_value in json_path_dict.items():
            json_path_expr = parse(json_path)
            a = json_path_expr.find(content)
            if not a:
                LogUtil.log_error('not fount the json path: {0} in {1}'.format(json_path, config_name))
            else:
                if config_name in self.old_value:
                    self.old_value[config_name].update({json_path: a[0].value})
                else:
                    self.old_value[config_name] = {json_path: a[0].value}
                json_path_expr.update(content, new_value)
        content = json.dumps(content)
        LogUtil.log_info(content)
        LogUtil.log_info(self.old_value)
        self.update_config(config_name, content, group)

