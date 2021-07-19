#!/usr/bin/python
# -*- coding: UTF-8 -*-
import requests
from elasticsearch import Elasticsearch
from tenacity import retry, wait_fixed, stop_after_attempt
import common.global_const as gc
from biztest.util.tools.tools import get_date

from app.common.http_util import Http
from app.common.log_util import LogUtil


class ES(object):
    tag_delimiter_mapping = {
        ".": "__"
    }

    def __init__(self, service_name, service_index=None):
        self.service = service_name
        self.es = Elasticsearch(gc.ES_URL)
        self.index = service_index if index else 'jaeger-span-*'

    @staticmethod
    def parse_tag(tag):
        for key, value in ES.tag_delimiter_mapping.items():
            if key in tag:
                tag = tag.replace(key, value)
        return tag

    @staticmethod
    def deparse_tag(tag):
        for key, value in ES.tag_delimiter_mapping.items():
            if value in tag:
                tag = tag.replace(value, key)
        return tag

    @staticmethod
    def search_trace_body(service_name, operation_type, order, **kwargs):
        """
        组装查询语句：根据service、操作、标签搜索
        :param service_name:
        :param operation_type:
        :param order:
        :param kwargs:
        :return:
        """
        body = {
            "sort": {"startTime": {"order": order}},
            "query": {
                "bool": {
                    "must": [
                        {"match": {"process.serviceName": service_name}},
                        {"match": {"operationName": operation_type}}
                    ]
                }
            }
        }
        for tag_key, tag_value in kwargs.items():
            tag_key = ES.deparse_tag(tag_key)
            body["query"]["bool"]["must"].append({
                "nested": {
                    "path": "tags",
                    "query": {
                        "bool": {
                            "must": [
                                {"match": {"tags.key": tag_key}},
                                {"match": {"tags.value": tag_value}}
                            ]
                        }
                    }
                }
            })
        return body

    @staticmethod
    def search_span_body(service_name, trace_id, operation_lt, order):
        """
        组装查询语句：根据service、trace_id和具体操作列表搜索
        :param service_name:
        :param trace_id:
        :param operation_lt:
        :param order:
        :return:
        """
        body = {
            "sort": {"startTime": {"order": order}},
            "query": {
                "bool": {
                    "must": [
                        {"match": {"process.serviceName": service_name}},
                        {"match": {"traceID": trace_id}},
                        {
                            "nested": {
                                "path": "references",
                                "query": {
                                    "bool": {
                                        "must": [
                                            {"match": {"references.spanID": trace_id}}
                                        ]
                                    }
                                }
                            }
                        }
                    ],
                    "should": [
                        {"match": {"operationName": x}} for x in operation_lt
                    ],
                    "minimum_should_match": 1
                }
            }
        }
        return body

    @retry(stop=stop_after_attempt(10), wait=wait_fixed(3))
    def get_request_log(self, operation_type, child_operation_lt, order='desc', operation_index=0, **kwargs):
        """
        从es获取请求日志，获取多条
        :param order_no: 资产编号
        :param operation_type: 业务节点
        :param child_operation_lt: 子业务节点list
        :param order: 按时间排序 desc/asc
        :param operation_index: 业务节点索引号
        :return: 请求日志json：
        {
            '子业务节点1': [{
                'http_status_code': 200,
                'http_path': '',
                'http_url': '',
                'http_method': ''
                'feign_request': '',
                'feign_response': ''
            },
            ...]
        }
        """
        ret_data_dt = {x:[] for x in child_operation_lt}
        # 1.查到trace_id
        resp = self.es.search(index=self.index, body=self.search_trace_body(self.service, operation_type, order,
                                                                            **kwargs))
        LogUtil.log_info("hits trace: %s" % resp)
        trace_id = resp['hits']['hits'][operation_index]['_source']['traceID']
        # 2.查询具体span
        resp = self.es.search(index=self.index, body=self.search_span_body(self.service, trace_id, child_operation_lt,
                                                                           order))
        LogUtil.log_info("hits spans: %s" % resp)
        hits_spans = resp['hits']['hits']
        for span in hits_spans:
            req_dt = {}
            for tag in span['_source']['tags']:
                req_dt[ES.parse_tag(tag['key'])] = tag['value']
            for log in span['_source']['logs']:
                req_dt[ES.parse_tag(log['fields'][0]['key'])] = log['fields'][0]['value']
            ret_data_dt[span['_source']['operationName']].append(req_dt)
        LogUtil.log_info("hits es log: %s" % ret_data_dt)
        return ret_data_dt

    @classmethod
    def clear_log(cls, last_day):
        for i in range(last_day, last_day+3):
            date = get_date(day=-i, fmt="%Y-%m-%d")
            Http.http_delete("http://biz-elasticsearch.k8s-ingress-nginx.kuainiujinke.com/*{}*".format(date))


if __name__ == '__main__':
    index = "jaeger-span-2021-03-11"
    service = "repay1"
    order_no = "10025423"
    operation = "execute_combine_withhold"
    child_operation_lt = ["/mock/5de5d515d1784d36471d6041/rbiz_auto_test/gbiz/user-id-query",
                          "/mock/5de5d515d1784d36471d6041/rbiz_auto_test/lanzhou/repaymentApply"]
    es = ES(service)
    req2 = es.get_request_log(order_no, operation, child_operation_lt, order='desc', operation_index=0)
