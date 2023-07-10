# -*- coding: utf-8 -*-
import json

from requests import HTTPError
from tenacity import retry, stop_after_attempt, wait_fixed
import requests

from app.common.log_util import LogUtil

JSON_HEADER = {"Content-Type": "application/json", "Connection": "close"}
WWW_FORM_HEADER = {"Content-Type": "application/x-www-form-urlencoded", "Connection": "close"}
FORM_HEADER = {"Content-Type": "multipart/form-data", "Connection": "close"}


def modify_resp(func):
    def wrapper(*args, **kwargs):
        url, req_data, resp = func(*args, **kwargs)
        if 'status_code' not in dir(resp) or resp.status_code not in (200, 201, 400):
            raise ValueError('request run status_code error: {0} #==# with url: {1} #==# req_data: {2}'.format(
                resp.status_code, url, json.dumps(req_data, ensure_ascii=False)))
        if url.startswith("https://openapitest.qinjia001.com"):
            return resp.content
        if url.startswith('https://biz-gateway-proxy.k8s-ingress-nginx.kuainiujinke.com/biz-filegate/'):
            return resp.content
        content = json.loads(resp.content)
        log_info = dict(zip(('url', 'method', 'request', 'response'),
                            (url, 'post', req_data, content)))
        LogUtil.log_info(log_info)
        content = content[0] if isinstance(content, list) else content
        if url.endswith("nacos/v1/cs/configs"):
            return content
        if 'code' not in content:
            raise ValueError('request run code error: {0} #==# with url: {1} #==# req_data: {2}'.format(
                content, url, json.dumps(req_data, ensure_ascii=False)))
        elif 'kong-api-test.kuainiujinke.com' in url:
            return content
        elif not content['code'] in (0, 200):
            if not '任务正在执行，请稍后重试' == content['message']:
                raise ValueError('request run content code error: {0} #==# with url: {1} #==# req_data: {2}'.format(
                    content['message'], url, json.dumps(req_data, ensure_ascii=False)))
        return content if resp is not None else resp

    return wrapper


class Http(object):

    @classmethod
    @modify_resp
    @retry(stop=stop_after_attempt(5), wait=wait_fixed(2))
    def http_post(cls, url, req_data, headers=None, cookies=None):
        headers = JSON_HEADER if headers is None else headers
        resp = None
        try:
            if 'application/json' in str(headers).lower():
                resp = requests.post(url=url, json=req_data, headers=headers, cookies=cookies, timeout=150)
            elif 'application/x-www-form-urlencoded' in str(headers).lower():
                resp = requests.post(url=url, data=req_data, headers=headers, cookies=cookies, timeout=150)
            elif 'multipart/form-data' in str(headers).lower():
                resp = requests.post(url, headers=headers, cookies=cookies, data=req_data, files=[])
        except Exception as e:
            LogUtil.log_info("http request error: %s" % e)
        return url, req_data, resp

    @classmethod
    @modify_resp
    @retry(stop=stop_after_attempt(5), wait=wait_fixed(2))
    def http_delete(cls, url, req_data, headers=None, cookies=None):
        headers = JSON_HEADER if headers is None else headers
        resp = None
        try:
            if 'application/json' in str(headers).lower():
                resp = requests.delete(url=url, json=req_data, headers=headers, cookies=cookies, timeout=150)
            elif 'application/x-www-form-urlencoded' in str(headers).lower():
                resp = requests.delete(url=url, data=req_data, headers=headers, cookies=cookies, timeout=150)
            elif 'multipart/form-data' in str(headers).lower():
                resp = requests.delete(url, headers=headers, cookies=cookies, data=req_data, files=[])
        except Exception as e:
            LogUtil.log_info("http request error: %s" % e)
        return url, req_data, resp

    @classmethod
    @modify_resp
    @retry(stop=stop_after_attempt(5), wait=wait_fixed(2))
    def http_get(cls, url, req_data=None, headers=None, cookies=None):
        headers = JSON_HEADER if headers is None else headers
        try:
            if 'multipart/form-data' in str(headers).lower():
                for key in headers:
                    if key.lower() == "content-type":
                        headers[key] += ";boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW"
                        break
                payload = """------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data;"""
                for index, item in enumerate(req_data):
                    req_data_value = req_data[item] if isinstance(req_data[item], str) else req_data[item]
                    # print(item, req_data_value, type(req_data_value))
                    if index == len(req_data) - 1:
                        payload += """  name=\"{0}\"\r\n\r\n{1}\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW--""".format(
                            item, req_data_value)
                    else:
                        payload += """  name=\"{0}\"\r\n\r\n{1}\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; """.format(
                            item, req_data_value)
                print(payload, type(payload))
                resp = requests.get(url, headers=headers, data=payload)
            else:
                resp = requests.get(url, headers=headers, cookies=cookies, timeout=150)
        except Exception as e:
            LogUtil.log_info("http request error: %s" % e)
            resp = str(e)
        return url, 'success', resp

    @classmethod
    @modify_resp
    @retry(stop=stop_after_attempt(5), wait=wait_fixed(2))
    def http_put(cls, url, req_data, headers):
        resp = None
        headers = JSON_HEADER if headers is None else headers
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
