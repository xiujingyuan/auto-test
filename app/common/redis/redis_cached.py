#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
 @author: snow
 @software: PyCharm
 @time: 2019/08/22
 @file: redis_cached.py
 @site:
 @email:
"""

import json

from flask import current_app
from sqlalchemy import or_

from app.models.CaseModel import Case


def update_case_redis(cases, type="add"):
    if current_app.app_redis.exists("gaea_all_cases"):
        ret = json.loads(current_app.app_redis.get("gaea_all_cases"))
        print(ret)
        if type == "delete":
            for case in cases:
                if not case.case_exec_group_priority or case.case_exec_group_priority == "main":
                    case_serialize = case.serialize()
                    old_case = {"case_id": case_serialize["case_id"], "case_name": case_serialize["case_name"]}
                    ret.remove(old_case)
        else:
            for case in cases:
                if not case.case_exec_group_priority or case.case_exec_group_priority == "main":
                    case_serialize = case.serialize()
                    ret.append({"case_id": case_serialize["case_id"],
                                "case_name": case_serialize["case_name"],
                                "case_from_system": case_serialize["case_from_system"],
                                "case_category": case_serialize["case_category"],
                                "case_belong_business": case_serialize["case_belong_business"]
                                })
        current_app.app_redis.set("gaea_all_cases", json.dumps(ret, ensure_ascii=False))
    else:
        ret = []
        all_cases = Case.query.filter(or_(Case.case_exec_group_priority == "main", Case.case_exec_group_priority == "")).filter(Case.case_is_exec == 1)
        for all_case in all_cases:
            case_serialize = all_case.serialize()
            ret.append({"case_id": case_serialize["case_id"],
                        "case_name": case_serialize["case_name"],
                        "case_from_system": case_serialize["case_from_system"],
                        "case_category": case_serialize["case_category"],
                        "case_belong_business": case_serialize["case_belong_business"]
                        })
        current_app.app_redis.set("gaea_all_cases", json.dumps(ret, ensure_ascii=False))
