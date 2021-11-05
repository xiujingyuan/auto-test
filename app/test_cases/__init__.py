# 自动化用例
from app.test_cases.china.biz_central import BizCentralTest


class TestCaseFactory(object):

    @classmethod
    def get_test_case(cls, country, env, environment, program):
        program == '{0}_test'.format(program).title()
        program = program.replace("_", '')
        return eval(program)(country, env, environment)
