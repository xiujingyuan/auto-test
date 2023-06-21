#!/usr/bin/python
# -*- coding: UTF-8 -*-
import datetime
import json

from elasticsearch import Elasticsearch

from app.common.http_util import Http
from app.common.tools import get_date


class ES(object):
    tag_delimiter_mapping = {
        ".": "__"
    }

    def __init__(self, services, indexs="jaeger-span-*"):
        """
        初始化
        :param services:
        :param indexs:
        """
        self.services = services
        self.es_url = "https://biz-elasticsearch.k8s-ingress-nginx.kuainiujinke.com"
        self.es = Elasticsearch(self.es_url)
        self.index = indexs

    @staticmethod
    def parse_tag(tag):
        for key, value in ES.tag_delimiter_mapping.items():
            if key in tag:
                tag = tag.replace(key, value)
        return tag

    @staticmethod
    def de_parse_tag(tag):
        for key, value in ES.tag_delimiter_mapping.items():
            if value in tag:
                tag = tag.replace(value, key)
        return tag

    @staticmethod
    def search_trace_body(services, operate, order, query_start=None, query_end=None, **tags):
        """
        组装查询语句：根据service、操作、标签搜索
        :param services:
        :param operate:
        :param order:
        :param query_start:
        :param query_end:
        :return:
        """
        body = {
            "sort": {"startTime": {"order": order}},
            "query": {
                "bool": {
                    "must": [
                        {"match": {"process.serviceName": services}},
                        {"match": {"operationName": operate}}
                    ]
                }
            }
        }
        for tag_key, tag_value in tags.items():
            tag_key = ES.de_parse_tag(tag_key)
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
            if query_start is not None and query_end is not None:
                body["query"]["bool"]["filter"] = [
                    {
                        "range": {
                            "timestamp": {
                                "gte": get_date(date=query_start, fmt="%Y-%m-%d'T'%H:%M:%S'Z'", is_str=True),
                                "lte": get_date(date=query_end, fmt="%Y-%m-%d'T'%H:%M:%S'Z'", is_str=True)
                            }
                        }
                    }
                ]
        return body

    @staticmethod
    def search_all_child_body(services, trace_id, order):
        body = {
            "sort": {"startTime": {"order": order}},
            "query": {
                "bool": {
                    "must": [
                        {"match": {"process.serviceName": services}},
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
                        {"match_all": {}}
                    ],
                    "minimum_should_match": 1
                }
            }
        }
        return body

    @staticmethod
    def search_span_body(services, trace_id, operation_lt, order):
        """
        组装查询语句：根据service、trace_id和具体操作列表搜索
        :param services:
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
                        {"match": {"process.serviceName": services}},
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

    def get_request_log(self, operate, child_operate_lt, order='desc', operation_index=0, **tags):
        """
        从es获取请求日志，获取多条
        :param operate: 业务节点
        :param child_operate_lt: 子业务节点list
        :param order: 按时间排序 desc/asc
        :param operation_index: 业务节点索引号
        :param tags：搜索条件比如 orderNo=xxxxxx, reqDto__key=xxxxxx
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
        ret_data_dt = {}
        # 1.查到trace_id
        param = self.search_trace_body(self.services, operate, order, **tags)
        resp = self.es.search(index=self.index, body=param)
        print("hits trace: %s" % resp)
        hits = resp['hits']['hits']
        if hits:
            trace_id = hits[operation_index]['_source']['traceID']
            # 2.查询具体span
            # param = self.search_span_body(self.services, trace_id, child_operate_lt, order)
            param = self.search_all_child_body(self.services, trace_id, order)
            resp = self.es.search(index=self.index, body=param)
            print("hits spans: %s" % resp)

            for span in hits:
                operate_name = span['_source']['operationName']
                if operate_name not in hits:
                    ret_data_dt[operate_name] = []
                req_dt = {}
                for tag in span['_source']['tags']:
                    req_dt[tag['key']] = tag['value']
                for log in span['_source']['logs']:
                    req_dt[log['fields'][0]['key']] = log['fields'][0]['value']
                ret_data_dt[operate_name].append(req_dt)

            print("hits es log: %s" % ret_data_dt)
            return ret_data_dt
        return None

    def get_request_child_info(self, operate, query_start, query_end, order='desc', operation_index=0, **tags):
        """
        获取请求地址，参数和返回
        :param operate:
        :param query_start:
        :param query_end:
        :param order:
        :param operation_index:
        :param tags:
        :return:
        """
        ret_data_dt = {}
        # 1.查到trace_id
        param = self.search_trace_body(self.services, operate, order, query_start, query_end, **tags)
        resp = self.es.search(index=self.index, body=param)
        hits = resp['hits']['hits']

        if not hits:
            return None
        for hit in hits:
            print("hits trace: %s" % hit)
            trace_id = hit['_source']['traceID']
            hit_ret_data_dt = {'task_info': {}}
            operate_time = datetime.datetime.fromtimestamp(
                hit['_source']['startTimeMillis'] / 1000).strftime('%Y-%m-%d %H:%M:%S')
            hit_ret_data_dt['task_info']["count"] = 1
            hit_ret_data_dt['task_info']['operate_time'] = operate_time
            hit_ret_data_dt['task_info']['http.path'] = "本地"
            hit_ret_data_dt['task_info']['host'] = "本地"
            hit_ret_data_dt['task_info']['path'] = "本地"
            hit_ret_data_dt['task_info']['http.url'] = "本地"
            hit_ret_data_dt['task_info']['request'] = hit['_source']['logs'][0]['fields'][0]['value']
            hit_ret_data_dt['task_info']['response'] = hit['_source']['logs'][-1]['fields'][0]['value']
            hit_ret_data_dt['task_info']['trace_url'] = f"https://biz-tracing.k8s-ingress-nginx.kuainiujin" \
                                                        f"ke.com/trace/{trace_id}/"
            # 2.查询具体span
            param = self.search_all_child_body(self.services, trace_id, order)
            resp = self.es.search(index=self.index, body=param)
            for span in resp['hits']['hits']:
                operate_name = span['_source']['operationName']
                if operate_name == 'Batch':
                    continue
                if operate_name.startswith('/kv/nacos/'):
                    continue
                if operate_name.startswith('/decrypt/'):
                    continue
                if operate_name.startswith('/encrypt/'):
                    continue
                if operate_name.startswith('/alert'):
                    continue
                req_dt = {'operate_time': operate_time}
                for tag in span['_source']['tags']:
                    tag_key = tag['key']
                    tag_value = tag['value']
                    if tag_key == 'http.url':
                        index = 6 if '/mock/' in tag_value else 3
                        req_dt['path'] = '/' + '/'.join(tag_value.split("/")[index:])
                        req_dt['host'] = tag_value.replace(req_dt['path'], '')
                    req_dt[tag_key] = tag_value
                for log in span['_source']['logs']:
                    log_key = log['fields'][0]['key']
                    log_value = log['fields'][0]['value']
                    if log_key in ('feign.request', 'feign.response', 'http.request', 'http.response'):
                        try:
                            log_value = json.dumps(json.loads(log_value), ensure_ascii=False)
                        except json.decoder.JSONDecodeError as e:
                            pass

                    log_key = log_key.replace("feign.", "") if log_key in ('feign.request', 'feign.response') else log_key
                    log_key = log_key.replace("http.", "") if log_key in ('http.request', 'http.response') else log_key
                    req_dt[log_key] = log_value
                if 'http.path' not in req_dt:
                    continue
                operate_name = operate_name if operate_name == 'task_info' else operate_name.split('/')[-1]
                if operate_time not in hits:
                    hit_ret_data_dt[operate_name] = {'count': 1}
                req_dt["trace_url"] = f"https://biz-tracing.k8s-ingress-nginx.kuainiujinke.com/trace/{trace_id}/"
                hit_ret_data_dt[operate_name].update(req_dt)
            if hit_ret_data_dt:
                ret_data_dt[operate_time] = hit_ret_data_dt
        return ret_data_dt

    @classmethod
    def clear_log(cls, last_day):
        for i in range(last_day, last_day+5):
            date = get_date(day=-i, fmt="%Y-%m-%d")
            Http.http_delete("https://biz-elasticsearch.k8s-ingress-nginx.kuainiujinke.com/*{}*".format(date))


if __name__ == '__main__':
    service = "repay2"
    order_no = "10071889"
    operation = "execute_combine_withhold"
    es = ES(service)
    req2 = es.get_request_child_info(operation, order='desc', operation_index=0, orderNo=order_no)
    print(req2)
