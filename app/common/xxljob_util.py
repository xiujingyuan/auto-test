# -*- coding: utf-8 -*-
import json
import os
from app.common.http_util import Http


HEADERS = {"content-type": "application/x-www-form-urlencoded"}
HEADERS_JSON = {"content-type": "application/json"}

XXL_JOB_DICT = {
    "china": {
        'url': 'http://biz-test-job.k8s-ingress-nginx.kuainiujinke.com/xxl-job-admin',
        'username': 'admin',
        'password': '123456',
        'repay': {
            "1": 53,
            "2": 122,
            "3": 55,
            "4": 55,
            "5": 56,
            "6": 57,
            "7": 58,
            "8": 59,
            "9": 60,
        },
        'biz-central': {
            "1": 130,
            "2": 131,
            "3": 132,
            "4": 133,
            "9": 134,
        }
    },
    "india": {
        'url': 'http://biz-xxl-job-admin.c99349d1eb3d045a4857270fb79311aa0.cn-shanghai.alicontainer.com/xxl-job-admin',
        'username': 'admin',
        'password': 'MTIzNDU2',
        'repay': {
            "1": 2
        }
    },
    "tha": {
        'url': 'http://biz-job-tha.c99349d1eb3d045a4857270fb79311aa0.cn-shanghai.alicontainer.com/xxl-job-admin',
        'username': 'admin',
        'password': '123456',
        'repay': {
            "1": 4
        }
    },
    "phl": {
        'url': 'http://biz-job-phl.c99349d1eb3d045a4857270fb79311aa0.cn-shanghai.alicontainer.com/xxl-job-admin',
        'username': 'admin',
        'password': '123456',
        'repay': {
            "1": 4
        }
    }
}


class XxlJob(object):

    def __init__(self, country, program, env):
        self.user_name = XXL_JOB_DICT[country]['username']
        self.password = XXL_JOB_DICT[country]['password']
        self.cookie = None
        self.base_url = XXL_JOB_DICT[country]['url']
        self.country = country
        self.program = program
        self.job_group = XXL_JOB_DICT[country][program][env]
        self.login_url = os.path.join(self.base_url, 'login')
        self.page_list_url = os.path.join(self.base_url, 'jobinfo/pageList')
        self.trigger_url = os.path.join(self.base_url, 'jobinfo/trigger')
        self.update_url = os.path.join(self.base_url, 'jobinfo/update')

    def login(self):
        req_body = {
            "userName": self.user_name,
            "password": self.password
        }
        resp = Http.parse_resp_body(method='post', url=self.login_url, headers=HEADERS, data=req_body)
        self.cookie = resp["cookies"]

    def get_page_list(self, job_group):
        req_body = {
            "jobDesc": "",
            "jobGroup": job_group,
            "executorHandler": "",
            "jobAuthor": "",
            "jobParam": "",
            "shCommand": "",
            "systemName": "",
            "triggerStatus": -1,
            "start": 0,
            "length": 200
        }
        resp = Http.parse_resp_body(method='post', url=self.page_list_url, headers=HEADERS,
                                    data=req_body, cookies=self.cookie)
        return resp

    def get_job_info(self, executor_handler):
        page_list = self.get_page_list(self.job_group)['content']['data']
        job_page = []
        for page in page_list:
            if page["executorHandler"] == executor_handler:
                job_page.append(page)
        return job_page

    def trigger_job(self, executor_handler, executor_param=None):
        self.login()
        job_info = self.get_job_info(executor_handler)
        if not job_info:
            raise Exception("没有查询到对应的executorHandler")
        for job in job_info:
            if executor_param is not None and executor_param:
                job["executorParam"] = executor_param if isinstance(executor_param, str) \
                    else json.dumps(executor_param, ensure_ascii=False)
            req_body = {
                "id": job["id"],
                "executorParam": job["executorParam"]
            }
            resp = Http.parse_resp_body(method='post', url=self.trigger_url, headers=HEADERS,
                                        data=req_body, cookies=self.cookie)
            if resp['content']["code"] != 200:
                raise Exception("触发job失败")

    def update_job(self, executor_handler, executor_param):
        self.login()
        job_info = self.get_job_info(self.job_group, executor_handler)
        if not job_info:
            raise Exception("没有查询到对应的executorHandler")
        for job in job_info:
            job["executorParam"] = executor_param if isinstance(executor_param, str) else \
                json.dumps(executor_param, ensure_ascii=False)
            update_job_info, header = self.get_job_info_dict(job_info)
            resp = Http.parse_resp_body(method='post', url=self.update_url, headers=header,
                                        data=update_job_info, cookies=self.cookie)
            if resp['content']["code"] != 200:
                raise Exception("更新job失败")

    def get_job_info_dict(self, job_info):
        update_job_info, header = {
            "id": job_info["id"],
            "jobCron": job_info["jobCron"],
            "jobDesc": job_info["jobDesc"],
            "author": job_info["author"],
            "executorRouteStrategy": job_info["executorRouteStrategy"],
            "executorHandler": job_info["executorHandler"],
            "executorParam": job_info["executorParam"],
            "executorBlockStrategy": job_info["executorBlockStrategy"],
            "sliceTotal": job_info["sliceTotal"]
        }, HEADERS
        if self.country in ('china', 'india'):
            update_job_info["notification"] = job_info["notification"]
            update_job_info["executorFailStrategy"] = job_info["executorFailStrategy"]
            update_job_info["systemName"] = job_info["systemName"]
            header = HEADERS_JSON
        else:
            update_job_info["cronGen_display"] = job_info["jobCron"]
            update_job_info["jobGroup"] = job_info["jobGroup"]
            update_job_info["alarmEmail"] = job_info["alarmEmail"]
            update_job_info["executorFailRetryCount"] = job_info["executorFailRetryCount"]
            update_job_info["executorTimeout"] = job_info["executorTimeout"]
        return update_job_info, header

    def trigger_job_for_id(self, job_id, job_param):
        self.login()
        req_body = {
            "id": job_id,
            "executorParam": job_param
        }
        resp = Http.parse_resp_body(method='post', url=self.trigger_url, headers=HEADERS,
                                    data=req_body, cookies=self.cookie)
        if resp['content']["code"] != 200:
            raise Exception("触发job失败")


if __name__ == '__main__':
    xxl_job = XxlJob(54, "refreshLateFeeV1", xxl_job_type="xxl_job")
    xxl_job.trigger_job()
    xxl_job = XxlJob(2, "withholdAutoV1", xxl_job_type="global_yindu_xxl_job")
    xxl_job.trigger_job()
    xxl_job.update_job("xxx")
    xxl_job = XxlJob(2, "withholdAutoV1", password="123456", xxl_job_type="global_xxl_job_new")
    xxl_job.trigger_job("xxxx")
    xxl_job.update_job("xxxx")
