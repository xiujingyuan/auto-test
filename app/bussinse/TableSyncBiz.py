# -*- coding: utf-8 -*-
# @Time    : 公元19-04-15 下午2:56
# @Author  : 张廷利
# @Site    : 
# @File    : TableSync.py
# @Software: IntelliJ IDEA
import json

from app import db

class TableSyncBiz(object):


    def sync_tables(self,request):
        request_dict = request.json
        error_message = ""
        update_flag = False
        last_user = 0
        if 'from_env' in request_dict.keys():
            source_env = request_dict['from_env']
        if 'to_env' in request_dict.keys():
            target_env = request_dict['to_env']
        if 'table_list' in request_dict.keys():
            table_list = request_dict['table_list']
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
        result={
            "add_tables":[],
            "update_tables":[],
            "msg":error_message
        }

        if table_list is None or table_list == "" or len(table_list)==0:
            self.get_diff_tables(source_env,target_env,result)
        else:
            self.get_special_diff_tables(source_env,target_env,table_list,result)
        return result


    def get_special_diff_tables(self,source_env,target_envs,origin_table_list,result):
        source_tables,source_tables_list,source_table_fields = self.get_special_tables(source_env,origin_table_list)
        for target_env in target_envs:
            target_tables,target_tables_list,target_table_fields = self.get_special_tables(target_env,origin_table_list)
            target_lost_table_list = self.get_diff_tablename(source_tables_list,target_tables_list)
            target_need_update_tables = self.get_add_field_tables(source_table_fields,target_table_fields)
            self.add_table_to_target_env(target_lost_table_list,source_env,target_env,result)
            self.add_field_to_target_table(target_need_update_tables,source_env,target_env,result)
        return result



    def get_diff_tables(self,source_env,target_envs,result):
        source_tables,source_tables_list,source_table_fields = self.get_tables(source_env)

        for target_env in target_envs:
            target_tables,target_tables_list,target_table_fields = self.get_tables(target_env)

            target_lost_table_list = self.get_diff_tablename(source_tables_list,target_tables_list)
            target_need_update_tables = self.get_add_field_tables(source_table_fields,target_table_fields)

            self.add_table_to_target_env(target_lost_table_list,source_env,target_env,result)
            self.add_field_to_target_table(target_need_update_tables,source_env,target_env,result)
        return




    def add_field_to_target_table(self,target_need_update_tables,from_env,to_env,result):
        try:
            if target_need_update_tables is None:
                return
            #sql= ""ALTER TABLE "+ table+ key + oField +" " +originalField['Type']"
            sql = "ALTER TABLE {0}.{1} ADD {2} {3} "
            for table_name,fields in target_need_update_tables.items():
                for field_type in fields:
                    for filed,type in field_type.items():
                        exec_sql = sql.format(to_env,table_name,filed,type[0])
                        if type[1] is not None:
                            if type[1]=="YES":
                                exec_sql = exec_sql +" null"
                            elif type[1]=="NO":
                                exec_sql = exec_sql +" not null"

                        #系统参数就不要引号，非系统参数就要引号，不想弄这么复杂，就不要默认值同步了
                        #exec_sql = exec_sql +" default " + type[2] +";"
                        if type[0].upper() in ['TIMESTAMP','DATETIME','DATE','TIME']:
                            exec_sql = exec_sql +" default " + type[2] +";"
                        elif type[2] is None and type[1]=="YES":
                            exec_sql = exec_sql +" default null;"
                        elif type[2] is not None:
                            exec_sql = exec_sql +" default '" + type[2] +"';"
                        result['update_tables'].append(exec_sql)
                        db.session.execute("use {0}".format(to_env));
                        db.session.execute(exec_sql)

        finally:
            db.session.commit();
            db.session.execute('use gaea_framework;')



    def add_table_to_target_env(self,target_lost_table_list,from_env,to_env,result):
        try:
            if target_lost_table_list is None:
                return

            sql= "create table {0}.{1} like {2}.{3};"
            for table_name in target_lost_table_list:
                exec_sql = sql.format(to_env,table_name,from_env,table_name)
                result['add_tables'].append(exec_sql)
                db.session.execute("use {0}".format(to_env));
                db.session.execute(exec_sql)

        finally:
            db.session.commit();
            db.session.execute('use gaea_framework;')



    def get_add_field_tables(self,source_tables,target_tables):
        diff_field_table ={}
        for source_table_name,source_fields  in source_tables.items():
            if source_table_name in target_tables.keys():
                target_fields = target_tables[source_table_name]
                target_single_fields = self.get_target_field(target_fields)
                diff_fields =[]
                for filed in source_fields:
                    for key ,value in filed.items():

                        if key not in target_single_fields:
                            diff_fields.append(filed)
                if len(diff_fields)==0:
                    continue
                else:
                    diff_field_table[source_table_name] = diff_fields

        return diff_field_table



    def get_target_field(self,target_fields):
        fields =[]
        for field in target_fields:
            for field_name,type in field.items():
                fields.append(field_name)

        return fields

    def get_diff_tablename(self,source,target):
        diff_tables =[]
        for t in source:
            if t not in target:
                diff_tables.append(t)
        return diff_tables



    def get_special_tables(self,env,origin_table_list):
        db.session.execute("use {0} ".format(env))
        result = {}
        table_list =[]
        table_field ={}
        for table in origin_table_list:
            #表结构最权限信息
            t_structor={}
            #字段加字段类型
            t_f_structor=[]

            t_structor[table]=[]
            try:
                temp = db.session.execute("desc `{0}`".format(table))
            except Exception as e:
                print(e)
                continue

            for t in temp:
                row ={}
                row[t[0]] = t[1:]
                field={}
                field[t[0]]=[t[1],t[2],t[4]]
                t_f_structor.append(field)
                t_structor[table].append(row)
            result[table] = t_structor
            table_field[table] = t_f_structor
            table_list.append(table)
        return result,table_list,table_field


    def get_tables(self,env):
        try:
            result = {}
            table_field ={}
            table_list =[]
            db.session.execute("use {0} ".format(env))
            origin_table_list = db.session.execute("show tables;")
            for table in origin_table_list:
                table_name = table[0]
                #表结构最权限信息
                t_structor={}
                #字段加字段类型
                t_f_structor=[]

                t_structor[table_name]=[]
                temp = db.session.execute("desc `{0}`".format(table_name))
                for t in temp:
                    row ={}
                    row[t[0]] = t[1:]
                    field={}
                    field[t[0]]=[t[1],t[2],t[4]]
                    t_f_structor.append(field)
                    t_structor[table_name].append(row)
                table_list.append(table_name)
                result[table_name] = t_structor
                table_field[table_name] = t_f_structor
            return result,table_list,table_field
        finally:
            db.session.execute('use gaea_framework;')
            #db.session.close()