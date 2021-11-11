# 自动化用例
from datetime import datetime

import traceback
from dateutil.relativedelta import relativedelta

from app import db
from app.model.Model import TestCase, RunCaseLog


def run_case_prepare(func):
    def wrapper(self, case, **kwargs):
        try:
            self.run_case_log.run_case_log_case_id = case.test_cases_id
            self.run_case_log.run_case_log_case_run_date = self.get_date(fmt="%Y-%m-%d")
            self.run_case_log.run_case_log_case_run_begin_at = self.get_date()
            # 资产准备
            func(self, case, **kwargs)
        except CaseException as e:
            self.set_case_fail('case', str(e))
        except Exception as e:
            print(e)
            self.set_case_fail('system', str(traceback.format_exc()))
        else:
            self.set_case_success()
        finally:
            self.run_case_log = RunCaseLog()

    return wrapper


class CaseException(Exception):
    pass


class BaseAutoTest(object):
    def __init__(self, env, environment):
        self.env = env
        self.environment = environment
        self.run_case_log = RunCaseLog()
        self.item_no = None

    @staticmethod
    def get_date(fmt="%Y-%m-%d %H:%M:%S", timezone=None, **kwargs):
        return (datetime.now(timezone) + relativedelta(**kwargs)).strftime(fmt)

    @staticmethod
    def get_case_list(case_id_list, case_group, case_scene):
        cases = []
        if case_id_list:
            cases = TestCase.query.filter(TestCase.test_cases_id.in_(tuple(case_id_list))).all()
        elif case_group:
            cases = TestCase.query.filter(TestCase.test_cases_group == case_group).all()
        elif case_scene:
            cases = TestCase.query.filter(TestCase.test_cases_scene == case_scene).all()
        return cases

    def run_cases(self, case_id_list, case_group, case_scene):
        cases = self.get_case_list(case_id_list, case_group, case_scene)
        for case in cases:
            try:
                self.run_single_case(case)
            except Exception as e:
                print(e)
                continue

    def set_case_success(self):
        self.run_case_log.run_case_log_case_run_finish_at = self.get_date()
        self.run_case_log.run_case_log_case_run_result = 'success'
        db.session.add(self)
        db.session.flush()

    def set_case_fail(self, fail_type, error_message):
        self.run_case_log.run_case_log_case_run_finish_at = self.get_date()
        self.run_case_log.run_case_log_case_run_result = 'fail'
        self.run_case_log.run_case_log_case_fail_type = fail_type
        self.run_case_log.run_case_log_case_run_error_message = error_message
        db.session.add(self.run_case_log)
        db.session.flush()

    @run_case_prepare
    def run_single_case(self, case):
        pass
