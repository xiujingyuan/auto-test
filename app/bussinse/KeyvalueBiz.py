# -*- coding: utf-8 -*-
# @Time    : 公元19-04-01 下午2:56
# @Author  : 张廷利
# @Site    : 
# @File    : KeyvalueBiz.py
# @Software: IntelliJ IDEA
import datetime

from app import db
from app.models.KeyvalueModel import KeyvalueModel
from app.common.tools.UnSerializer import UnSerializer
from app.common.tools.Serializer import Serializer


class KeyvalueBiz(UnSerializer, Serializer):

    def sync_keyvalue(self, request):
        request_dict = request.json
        error_message = ""
        keyvalue_key_replace = ""
        keyvalue_value_replace = ""
        keyvalue_list = ""
        update_flag = False
        last_user = 0
        if 'from_env' in request_dict.keys():
            source_env = request_dict['from_env']
        if 'to_env' in request_dict.keys():
            target_env = request_dict['to_env']
        if 'keyvalue_list' in request_dict.keys():
            keyvalue_list = request_dict['keyvalue_list']
        if 'keyvalue_key_replace' in request_dict.keys():
            keyvalue_key_replace = request_dict['keyvalue_key_replace']
        if 'keyvalue_value_replace' in request_dict.keys():
            keyvalue_value_replace = request_dict['keyvalue_value_replace']
        if 'user' in request_dict.keys():
            last_user = request_dict['user']
        if 'update_flag' in request_dict.keys():
            update_flag = request_dict['update_flag']

        if target_env is None or target_env == "":
            error_message = "to env 不能为空"
            return error_message
        if source_env is None or source_env == "":
            error_message = "from env 不能为空"
            return error_message
        # 如果同步到多个环境
        for to_env in target_env:
            # from_env 比to_env 多的数据。
            diff_keyvalue = {}
            if keyvalue_list is None or keyvalue_list == "":
                diff_keyvalue_list = self.get_diff_keyvalue_keys(source_env, to_env)
                diff_keyvalue = self.get_keyvalue_bykey(diff_keyvalue_list, source_env)
            else:
                diff_keyvalue = self.get_keyvalue_bykey(keyvalue_list, source_env)
            # 替换指定的数据的key
            self.replace_target_key(diff_keyvalue, keyvalue_key_replace)
            # 替换指定数据的dvalue
            self.replace_target_value(diff_keyvalue, keyvalue_value_replace)
            # 写回目的库的表
            result={
                "add_keys":[],
                "update_keys":[],
                "msg":error_message
            }
            for keyvalue in diff_keyvalue:
                self.update_or_add_keyvalue(keyvalue, to_env, last_user,result,update_flag)

        return result

    def replace_target_key(self, targets, keyvalue_key_replace):
        if keyvalue_key_replace != "" and keyvalue_key_replace is not None:
            for keyvalue_key in keyvalue_key_replace:
                for key, value in keyvalue_key.items():
                    for target in targets:
                        target.keyvalue_key = target.keyvalue_key.replace(key, value)
            return targets

    def replace_target_value(self, targets, keyvalue_value_replace):
        if keyvalue_value_replace != "" and keyvalue_value_replace is not None:
            for keyvalue_key in keyvalue_value_replace:
                for key, value in keyvalue_key.items():
                    for target in targets:
                        target.keyvalue_value = target.keyvalue_value.replace(key, value)
            return targets

    def get_diff_keyvalue_keys(self, from_env, to_env):
        # 获取两套环境中，from_env 比to_env 多的key
        if from_env is not None:
            from_env_keyvalues = self.get_keyvalue_key_byenv(from_env)
        if to_env is not None:
            to_env_keyvalues = self.get_keyvalue_key_byenv(to_env)
        result = []
        for row in from_env_keyvalues:
            if row not in to_env_keyvalues:
                result.append(row.keyvalue_key)
        return result

    def get_keyvalue_bykey(self, keylists, from_env):
        db.session.connection(execution_options={
            "schema_translate_map": {"db_test": from_env}})
        result = db.session.query(KeyvalueModel). \
            filter(KeyvalueModel.keyvalue_status == 'active'). \
            filter(KeyvalueModel.keyvalue_key.in_(keylists)).all()
        #db.session.close()
        return result

    def get_keyvalue_key_byenv(self, from_env):
        db.session.connection(execution_options={
            "schema_translate_map": {"db_test": from_env}})
        # print(from_env)
        query = db.session.query(KeyvalueModel). \
            filter(KeyvalueModel.keyvalue_status == 'active'). \
            filter(KeyvalueModel.keyvalue_key != ""). \
            filter(KeyvalueModel.keyvalue_key.notlike('%{0}%'.format(from_env))) \
            .with_entities(KeyvalueModel.keyvalue_key)

        result = query.all()
        #db.session.close()

        return result

    def update_or_add_keyvalue(self, key_value, to_env, user, result,update_flag=False):
        new_key_value = KeyvalueModel()
        del key_value.__dict__['_sa_instance_state']
        new_key_value.__dict__.update(key_value.__dict__)
        new_key_value.keyvalue_id = None
        keyvalue_key = new_key_value.keyvalue_key
        if (self.check_keyvalue_key_exists(key_value.keyvalue_key, to_env)):
            if update_flag:
                key_value_dict = key_value.__dict__
                self.update_keyvalue(keyvalue_key, key_value_dict, to_env, user)
                result['update_keys'].append(keyvalue_key)
        else:
            self.add_keyvalue(new_key_value, to_env, user)
            result['add_keys'].append(key_value.keyvalue_key)
        return result

    def update_keyvalue(self, keyvalue_key, keyvalue, to_env, user):
        db.session.connection(execution_options={
            "schema_translate_map": {"db_test": to_env}})
        keyvalue['keyvalue_update_at'] = datetime.datetime.now()
        keyvalue['keyvalue_update_user'] = user
        del keyvalue['keyvalue_id']
        db.session.query(KeyvalueModel).filter(KeyvalueModel.keyvalue_key == keyvalue_key).update(keyvalue)
        db.session.commit()
        #db.session.close()

    def add_keyvalue(self, keyvalue, to_env, user):
        db.session.connection(execution_options={
            "schema_translate_map": {"db_test": to_env}})
        keyvalue.keyvalue_create_at = datetime.datetime.now()
        keyvalue.keyvalue_update_at = datetime.datetime.now()
        keyvalue.keyvalue_create_user = user
        keyvalue.keyvalue_update_user = user
        keyvalue.keyvalue_id = None
        db.session.add(keyvalue)
        db.session.flush()
        db.session.commit()
        #db.session.close()

    def check_keyvalue_key_exists(self, keyvalue_key, env):
        db.session.connection(execution_options={
            "schema_translate_map": {"db_test": env}})
        count = db.session.query(KeyvalueModel).filter(KeyvalueModel.keyvalue_key == keyvalue_key).count()
        #db.session.close()
        if count > 0:
            return True
        else:
            return False
