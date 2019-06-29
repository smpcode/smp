# -*- coding: utf-8 -*-

"""
database
~~~~~~~~~~~~

数据库基础层封装，增加多个DB支持，增加读写分离支持
数据库支持一主多从架构

:copyright: (c) 2017 smpcode
:authors: smpcode
:version: 1.0 of 2017-04-28

"""

# pylint: disable=invalid-name
import logging
import peewee
from peewee import Field
from peewee import OperationalError

from common.errors import DatabaseError
from common.db.hook import Model as _Model
from common.utils import load_class

TYPE_MAP = {
    'char': 'CharField',
    'varchar': 'CharField',
    'enum': 'CharField',
    'text': 'TextField',
    'longtext': 'TextField',
    'mediumtext': 'TextField',
    'datetime': 'DateTimeField',
    'integer': 'IntegerField',
    'bool': 'BooleanField',
    'boolean': 'BooleanField',
    'int': 'IntegerField',
    'mediumint': 'IntegerField',
    'smallint': 'IntegerField',
    'float': 'FloatField',
    'real': 'FloatField',
    'bigint': 'BigIntegerField',
    'double': 'DoubleField',
    'numeric': 'DecimalField',
    'decimal': 'DecimalField',
    'timestamp': 'DateTimeField',
    'date': 'DateField',
    'time': 'TimeField',
    'tinyint': 'IntegerField',
    'blob': 'BlobField',
    'mediumblob': 'BlobField',
    'longblob': 'BlobField',
}


MAX_CONNECTIONS = 10
# 一小时
STALE_TIMEOUT = 3600


class EnumField(Field):
    """自定义枚举类型字段, peewee中不提供枚举类型
    """
    db_field = 'enum'

    def __init__(self, enum_value=None, *args, **kwargs):
        """枚举初始化
        """
        self.enum_value = enum_value
        super(EnumField, self).__init__(*args, **kwargs)

    def get_modifiers(self):
        """使用传递的枚举值
        """
        return self.enum_value and [self.enum_value] or None


class Database(object):

    '''db封装,自动查找数据库
    '''
    engine_map = {
        'mysql': 'common.db.retrydb.RetryDB',  # 增加重连机制
        'mysqlpool': 'playhouse.pool.PooledMySQLDatabase',
    }
    current_user = None

    def __init__(self, nsc, namespace, db_name, db_user, db_password, engine='mysql', **connect_kwargs):
        self.nsc = nsc  # 服务发现客户端
        self.namespace = namespace  # 服务发现地址
        self.use_engine = engine
        self.db_name = db_name
        self.db_user = db_user
        self.db_password = db_password
        self.engine = self.engine_map[engine]
        self.connect_kwargs = connect_kwargs
        self.load_database()
        self.master_database.field_overrides.update({'enum': 'enum'})  # 增加枚举类型

    def load_database(self):
        '''加载数据库配置
        '''
        try:
            self.database_class = load_class(self.engine)
            assert issubclass(self.database_class, peewee.Database)
        except ImportError:
            raise DatabaseError('Unable to import: "%s"' % self.engine)
        except AttributeError:
            raise DatabaseError(
                'Database engine not found: "%s"' % self.engine)
        except AssertionError:
            raise DatabaseError(
                'Database engine not a subclass of peewee.Database: "%s"' % self.engine)

        master_conf = self.get_master_conf()
        self.master_database = self._connect(
            master_conf, **self.connect_kwargs)
        slave_conf = self.get_slave_conf()
        self.slaves_database = [self._connect(
            slave, **self.connect_kwargs) for slave in slave_conf]

    def get_master_conf(self):
        """通过服务发现获取主库配置
        """
        master_conf = self.nsc.get_master_service(self.namespace)
        return dict(
            host=master_conf['host'],
            port=int(master_conf['port']),
            db=self.db_name,
            user=self.db_user,
            password=self.db_password
        )

    def get_slave_conf(self):
        """通过服务发现获取从数据库配置列表
        """
        slave_conf = []
        slave_list = self.nsc.get_slave_service(self.namespace)
        for slave in slave_list:
            slave_conf.append(dict(host=slave['host'],
                                   port=int(slave['port']),
                                   db=self.db_name,
                                   user=self.db_user,
                                   password=self.db_password))
        return slave_conf

    def _connect(self, config, **kwargs):
        '''解析配置
        '''
        kwargs.update(config)
        if self.use_engine == 'mysqlpool':
            kwargs['max_connections'] = MAX_CONNECTIONS
            kwargs['stale_timeout'] = STALE_TIMEOUT
        return self.database_class(kwargs.pop('db'), **kwargs)

    def connect(self, retry_num=3):
        '''主从建立连接,如果连接关闭重试
        '''
        # 重试四次
        for _ in range(retry_num):
            try:
                if self.master_database.is_closed():
                    self.master_database.get_conn().ping(True)
                    for slave in self.slaves_database:
                        if slave.is_closed():
                            slave.get_conn().ping(True)
                break
            except OperationalError as err:
                logging.error("connect to database failed, err=%s", err)
                self.close()

    def close(self):
        '''关闭连接
        '''
        try:
            self.master_database.close()
            for slave in self.slaves_database:
                slave.close()
        except:
            pass

    def insert_many(self, model, data):
        """批量插入
        :param model: model class
        :param data: data that need to insert
        :type data: list
        """
        with self.master_database.atomic():
            try:
                model.insert_many(data).upsert().execute()
            except KeyError as error:
                logging.error('insert many failed for %s', error)
                return False
        return True
