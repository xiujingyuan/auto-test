# -*- coding: utf-8 -*-
import json

from requests import HTTPError
from tenacity import retry, stop_after_attempt, wait_fixed
import requests

from app.common.log_util import LogUtil


class Http(object):
    @classmethod
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
            resp = None
        if int(resp.status_code) not in (200, 201):
            LogUtil.log_info("请求报错，url:%s 返回的http_code:%s异常，返回body:%s，请检查" % (url,
                                                                              resp.status_code,
                                                                              resp.content))
            raise HTTPError
        log_info = {
                        "url": url,
                        "method": "post",
                        "request": req_data,
                        "response": json.loads(resp.content)
                    }
        LogUtil.log_info(log_info)
        return json.loads(resp.content)

    @classmethod
    @retry(stop=stop_after_attempt(5), wait=wait_fixed(2))
    def http_get(cls, url, headers=None, cookies=None):
        if headers is None:
            headers = {"Content-Type": "application/json", "Connection": "close"}
        try:
            resp = requests.get(url, headers=headers, cookies=cookies, timeout=150)
        except Exception as e:
            LogUtil.log_info("http request error: %s" % e)
            resp = None
        if int(resp.status_code) not in (200, 201):
            LogUtil.log_info("请求报错，url:%s 返回的http_code:%s异常，请检查" % (url, resp.status_code))
            raise HTTPError
        log_info = {"url": url,
                    "method": "get",
                    "request": None,
                    "response": json.loads(resp.content)}
        LogUtil.log_info(log_info)
        return json.loads(resp.content)

    @classmethod
    @retry(stop=stop_after_attempt(5), wait=wait_fixed(2))
    def http_put(cls, url, req_data, headers):
        if headers is None:
            headers = {"Content-Type": "application/json"}
        try:
            if 'application/json' in str(headers).lower():
                resp = requests.put(url=url, json=req_data, headers=headers, timeout=150)
            else:
                resp = requests.put(url=url, data=req_data, headers=headers, timeout=150)
        except Exception as e:
            LogUtil.log_info("http request error: %s" % e)
            resp = None
        if int(resp.status_code) not in (200, 201):
            LogUtil.log_info("请求报错，url:%s 返回的http_code:%s异常，请检查" % (url, resp.status_code))
            raise HTTPError
        log_info = {"url": url,
                    "method": "put",
                    "request": req_data,
                    "response": json.loads(resp.content)}
        LogUtil.log_info(log_info)
        return json.loads(resp.content)

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
