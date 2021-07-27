
import traceback
import pymysql
import json
from dbutils.pooled_db import PooledDB
from sshtunnel import SSHTunnelForwarder

from app.common.log_util import LogUtil
from app.common.tools import get_port, trans_data, generate_sql


class DataBase(object):
    ssh_runnel = []
    pools = {}
    log = LogUtil()

    def __init__(self, system, num, country, run_env):
        """
        初始化database
        :param system:系统简称
        :param num: 环境1,2,3,4,testing, stating
        :param country: 国家 china, tha, phl
        :param run_env: 运行环境
        """
        self.system = system
        self.num = num
        self.country = country
        self.config_key = self.system if self.country == 'china' else '{0}_{1}'.format(self.system, self.country)
        self.server_name = self.config_key + str(self.num)
        # philippines china thailand india
        self.environment = run_env

    def __connect(self, host, user, password, database, port):
        pool = PooledDB(pymysql, 5,
                        host=host,
                        user=user,
                        passwd=password,
                        db=database,
                        port=port)
        DataBase.pools[self.server_name] = pool
        self.log.log_info("connect to %s with port %s" % (self.server_name, port))

    def connect(self):
        if self.server_name not in DataBase.pools.keys():
            file_name = '' if self.environment == 'test' else 'dev'
            with open("./resource/{1}/database_{0}.config".format(file_name, self.country)) as fd:
                configs = fd.read()
            configs = json.loads(configs)

            if self.config_key not in configs:
                raise ValueError('not found the {0} key in the configs'.format(self.config_key))
            host = configs[self.config_key]["host"]
            user = configs[self.config_key]["username"]
            password = configs[self.config_key]["password"]
            database = configs[self.config_key]["database"].format(self.num)
            port = configs[self.config_key]["port"]
            self.__connect(host, user, password, database, port)
            if "ssh" in configs[self.config_key]:
                ssh = configs[self.config_key]["ssh"]
                port = get_port()
                server = SSHTunnelForwarder(
                    ssh_address_or_host=(ssh["ssh_proxy_host"], 22),
                    ssh_username=ssh["ssh_user_name"],
                    ssh_pkey=ssh["ssh_private_key"],
                    remote_bind_address=(ssh["ssh_remote_host"], 3306),
                    local_bind_address=('127.0.0.1', port))
                server.start()
                DataBase.ssh_runnel.append(server)
        return DataBase.pools[self.server_name].connection()

    def do_sql(self, sql, last_id=False):
        try:
            connection = self.connect()
            cursor = connection.cursor(pymysql.cursors.DictCursor)
            cursor.execute(sql)
            connection.commit()
            if last_id:
                cursor.execute("select last_insert_id();")
            result = cursor.fetchall()
            log_info = {"db": self.server_name,
                        "sql request": sql
                        }
            self.log.log_info(log_info)
            return result[0]['last_insert_id()'] if last_id else trans_data(result)
        except Exception as e:
            self.log.log_info("数据库执行异常，sql：%s" % sql)
            self.log.log_info("数据库执行异常：%s" % str(e))
            traceback.print_exc()

    def query(self, sql):
        return self.do_sql(sql)

    def delete(self, sql):
        return self.do_sql(sql)

    def update(self, sql):
        return self.do_sql(sql)

    def insert(self, sql):
        return self.do_sql(sql)

    def insert_data(self, table_name, **kwargs):
        sql = "insert into %s set %s" % (table_name, generate_sql(kwargs, ","))
        return self.do_sql(sql)

    def update_data(self, table_name, where_key, where_value, **kwargs):
        sql = "update %s set %s" % (table_name, generate_sql(kwargs, ","))
        sql += "where {0}={1}".format(where_key, where_value)
        return self.do_sql(sql)

    def get_data(self, table_name, query_key=None, order_by=None, limit=None, **kwargs):
        sql = "select * from %s where %s" % (table_name, generate_sql(kwargs, "and"))
        if query_key is not None:
            sql += generate_sql(query_key, 'and')
        if order_by is not None:
            sql += ' order by {0} desc'.format(order_by)
        if limit is not None:
            sql += ' limit {0}'.format(limit)
        data_list = self.do_sql(sql)
        return data_list

    def delete_data(self, table_name, **kwargs):
        sql = "delete from %s where %s" % (table_name, generate_sql(kwargs, "and"))
        return self.do_sql(sql)

    @classmethod
    def close_connects(cls):
        if DataBase is not None:
            for db, pool in DataBase.pools.items():
                pool.connection().close()
                pool.close()
                cls.log.log_info("关闭数据库链接：%s" % db)
            DataBase.pools.clear()
            for server in DataBase.ssh_runnel:
                cls.log.log_info("关闭隧道：%s" % server.local_bind_addresses)
                server.close()
                cls.log.log_info("关闭隧道成功")
            DataBase.ssh_runnel.clear()

    def __del__(self):
        self.close_connects()



