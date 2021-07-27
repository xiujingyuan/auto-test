import unittest
import re
import operator

from jsonpath_ng import jsonpath

from app.common.tools import get_json_path


class Assert(object):

    @classmethod
    def assert_equal(cls, excepts, actual, msg="assert failed"):
        unittest.TestCase().assertEqual(excepts, actual, msg)
        pass

    @classmethod
    def assert_not_equal(cls, excepts, actual, msg="assert failed"):
        unittest.TestCase().assertNotEqual(excepts, actual, msg)
        pass

    @classmethod
    def assert_in(cls, member, container, msg="assert failed"):
        unittest.TestCase().assertIn(member, container, msg)
        pass

    @classmethod
    def assert_not_in(cls, member, container, msg="assert failed"):
        unittest.TestCase().assertNotIn(member, container, msg)
        pass

    @classmethod
    def assert_match(cls, text, expected_regex, msg="assert failed"):
        unittest.TestCase().assertRegex(text, expected_regex, msg)
        pass

    @classmethod
    def assert_not_match(cls, text, expected_regex, msg="assert failed"):
        unittest.TestCase().assertNotRegex(text, expected_regex, msg)
        pass

    @classmethod
    def assert_match_json(cls, except_json, actual_json, msg="assert failed"):
        path_list = get_json_path(except_json)
        for path in path_list:
            if not jsonpath.jsonpath(except_json, path):
                raise Exception("path:%s not fount in json:%s" % (path, str(except_json)))
            if not jsonpath.jsonpath(actual_json, path):
                raise Exception("path:%s not fount in json:%s" % (path, str(actual_json)))
            except_value = jsonpath.jsonpath(except_json, path)[0]
            actual_value = jsonpath.jsonpath(actual_json, path)[0]

            if isinstance(except_value, dict):
                cls.assert_match_json(except_value, actual_value, msg)
            elif isinstance(except_value, list):
                cls.assert_equal(str(sorted(except_value)), str(sorted(actual_value)), msg)
            elif isinstance(except_value, tuple):
                cls.assert_equal(operator.eq(actual_value, except_value), True, msg)
            else:
                if str(except_value) == str(actual_value):
                    continue
                elif str(except_value) in str(actual_value):
                    continue
                elif re.compile(str(except_value)).search(str(actual_value)):
                    continue
                else:
                    raise Exception("\n except: %s \n actual: %s \n msg:%s" % (except_value, actual_value, msg))


if __name__ == "__main__":
    except_jsons = {"a": "a", "b": "b", "c": "c"}
    actual_jsons = {"a": "a", "b": "a", "c": "b"}
    Assert.assert_match_json(except_jsons, actual_jsons, "test")
