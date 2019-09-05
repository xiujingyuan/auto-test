# -*- coding: utf-8 -*-
# @ProjectName:    gaea-api$
# @Package:        $
# @ClassName:      InitBiz$
# @Description:    描述
# @Author:         piay
# @CreateDate:     2019/8/30 16.30
# @UpdateUser:     piay
# @UpdateDate:     2019/8/30 16.30
# @UpdateRemark:   更新内容
# @Version:        1.0
import json

import pymysql,time



class Validation(Exception):
    def __new__(cls, *args, **kwargs):
        return Exception.__new__(cls)

    def __init__(self,log):
        self.log =log

    def __str__(self):
        return "执行错误:%s" % self.log

class db_connect():
    err_code = '000000'  # mysql错误码
    _instance = None  # 本来的实例
    _conn = None  # 数据库连接
    _cur = None  # 数据库游标
    error_msg=None

    _TIMEOUT = 10  # 默认超时时间为30s
    _timeout = 0
    def __init__(self):
        try:
            self._conn = pymysql.Connect(
                port=3306,
                host='10.0.1.15',
                passwd='Coh8Beyiusa7',
                db='gbiz1',
                user='root'
            )
            self._cur = self._conn.cursor()
            self._instance = pymysql
        except pymysql.Error as e:


            # 如果没有超过预设时间，则再次尝试连接
            if self._timeout < self._TIMEOUT:
                interval = 5
                self._timeout += interval
                time.sleep(interval)
                self.__init__()
            else:
                self.err_code = e.args[0]
                self.error_msg = 'Mysql error %d:%s' % (e.args[0], e.args[1])


    def do_sql(self,sql,database,table=None):
        if self.err_code!='000000':
            return self.err_code,self.error_msg
        else:
            try:
                use_database_sql='use %s'%str(database);
                self._cur.execute(use_database_sql)
                self._cur.execute(sql)
                self._conn.commit()
                return 0,self._cur.fetchall()
            except Exception as e:
                return self.err_code,str(e)



class Executesql():

    def __init__(self):
        pass

    _res_success_data={
        "code":0,
        "message":"success"
    }

    _res_fail_data={
        "code":1

    }
    def executesql(self,request):
        '''
        传入参数格式：
        {
            "db":"gaea_framework",
            "table":"finlab_cases",
            "values":[
                 "insert xxxxxx",
                 "update xxxxxx"
                    ]
        }
        :param request:
        :return:
        '''

        results={}
        try:
            if isinstance(request,dict)==False:
                data=json.loads(request)
            else:
                data=request
            if 'db' not in data.keys() or data['db'] is None or len(str(data['db']))==0:
                self._res_fail_data['message'] = str(Validation("未传入需要执行的数据库db,请检查"))
                return self._res_fail_data
            database=data['db']
            table=None
            if 'table' in data.keys() and data['table'] is not None and len(str(data['table']))>0:
                table=data['table']


            if 'values' not in data.keys() or data['values'] is None or len(str(data['values']))==0:
                self._res_fail_data['message']=str(Validation('要执行的sql不能为空'))
                return self._res_fail_data
            # 每条结果执行返回对应的结果
            for sql in data['values']:
                cur=db_connect()
                code,res=cur.do_sql(sql,database,table)
                if code==0:
                    self._res_success_data['data']=res
                    results[sql]=self._res_success_data
                else:
                    self._res_fail_data['message']=res
                    results[sql]=self._res_fail_data

            return results


        except Exception as e:
            print(e)
            self._res_fail_data['message']=str(Validation(str(e)))
            return self._res_fail_data

