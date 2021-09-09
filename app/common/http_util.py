# -*- coding: utf-8 -*-
import json

from requests import HTTPError
from tenacity import retry, stop_after_attempt, wait_fixed
import requests

from app.common.log_util import LogUtil


def modify_resp(func):
    def wrapper(*args, **kwargs):
        url, req_data, resp = func(*args, **kwargs)
        content = json.loads(resp.content)
        log_info = dict(zip(('url', 'method', 'request', 'response'),
                            (url, 'post', req_data,  content)))
        LogUtil.log_info(log_info)
        if resp.status_code in (200, 201, 400):
            content = content[0] if isinstance(content, list) else content
            if 'code' not in content:
                raise ValueError('request url error {0}'.format(content))
            elif 'kong-api-test.kuainiujinke.com' in url:
                return content
            elif not content['code'] in (0, 200):
                raise ValueError('request run  error {0}, with url: {1}, req_data: {2}'.format(
                    content['message'], url, req_data))
        else:
            raise ValueError('request error, with status code:{0}'.format(resp.status_code))
        return content if resp is not None else resp
    return wrapper


class Http(object):

    @classmethod
    @modify_resp
    @retry(stop=stop_after_attempt(5), wait=wait_fixed(2))
    def http_post(cls, url, req_data, headers=None, cookies=None):
        if headers is None:
            headers = {"Content-Type": "application/json", "Connection": "close"}
        resp = None
        try:
            if 'application/json' in str(headers).lower():
                resp = requests.post(url=url, json=req_data, headers=headers, cookies=cookies, timeout=150)
            elif 'application/x-www-form-urlencoded' in str(headers).lower():
                resp = requests.post(url=url, data=req_data, headers=headers, cookies=cookies, timeout=150)
        except Exception as e:
            LogUtil.log_info("http request error: %s" % e)
        return url, req_data, resp

    @classmethod
    @modify_resp
    @retry(stop=stop_after_attempt(5), wait=wait_fixed(2))
    def http_get(cls, url, headers=None, cookies=None):
        if headers is None:
            headers = {"Content-Type": "application/json", "Connection": "close"}
        try:
            resp = requests.get(url, headers=headers, cookies=cookies, timeout=150)
        except Exception as e:
            LogUtil.log_info("http request error: %s" % e)
        return url, '', resp

    @classmethod
    @modify_resp
    @retry(stop=stop_after_attempt(5), wait=wait_fixed(2))
    def http_put(cls, url, req_data, headers):
        resp = None
        if headers is None:
            headers = {"Content-Type": "application/json"}
        try:
            if 'application/json' in str(headers).lower():
                resp = requests.put(url=url, json=req_data, headers=headers, timeout=150)
            else:
                resp = requests.put(url=url, data=req_data, headers=headers, timeout=150)
        except Exception as e:
            LogUtil.log_info("http request error: %s" % e)
        return url, '', resp

    @classmethod
    def parse_resp_body(cls, method, url, data=None, headers=None, cookies=None, params=None):
        resp = requests.request(method=method, url=url, headers=headers, data=data, cookies=cookies, params=params)
        try:
            content = json.loads(resp.text)
        except Exception as e:
            print(e)
            content = resp.text
        finally:
            resp = {
                "status_code": resp.status_code,
                "content": content,
                "headers": resp.headers,
                "cookies": requests.utils.dict_from_cookiejar(resp.cookies),
                "reason": resp.reason
            }
            return resp
