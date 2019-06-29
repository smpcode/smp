# -*- coding: utf-8 -*-

"""
base
~~~~~~~~~~~~

redis 操作记录的基础模板

:copyright: (c) 2019 smpcode
:authors: smpcode
:version: 1.0 of 2019-04-24

"""
import six
from redis import Redis as _RedisClient

from common.errors import ConfigError

if not isinstance(b'', type('')):
    def u(s):
        return s
    unicode_type = str
    basestring_type = str
else:
    def u(s):
        return s.decode('unicode_escape')
    # These names don't exist in py3, so use noqa comments to disable
    # warnings in flake8.
    unicode_type = unicode  # noqa
    basestring_type = basestring  # noqa

class Client(object):

    host = '127.0.0.1'
    port = 6379
    db = 0

    def __init__(self, host=None, port=None, db=0,
                 transaction=False, **kwargs):
        self.host = host or self.host
        self.port = port or self.port
        self.transaction = transaction  # codis不支持事务机制
        self.db = db or self.db
        # 将redis的超时设置统一处理
        socket_timeout = kwargs.get("socket_timeout", 0.2)
        socket_connect_timeout = kwargs.get("socket_connect_timeout", 0.2)
        # 使用长连接
        socket_keepalive = kwargs.get("socket_keepalive", True)
        retry_on_timeout = kwargs.get("retry_on_timeout", True)
        if six.PY3:
            kwargs["encoding"] = "utf-8"
            kwargs["decode_responses"] = True
        self.api = _RedisClient(self.host,
                                self.port,
                                self.db,
                                socket_timeout=socket_timeout,
                                socket_connect_timeout=socket_connect_timeout,
                                socket_keepalive=socket_keepalive,
                                retry_on_timeout=retry_on_timeout,
                                connection_pool=None,
                                ** kwargs)

class Key(unicode_type):

    """使用[]操作来拼接redis的key
    默认下划线分隔符
    """

    def __getitem__(self, key):
        if not isinstance(key, basestring_type):
            key = str(key)
        if not self:
            return Key(key)
        return Key(u"{}:{}".format(self, key))

REDISDB = Client()

class NSCModel(object):

    """基于服务发现的Model基类
    Attributes:
        client_name: 选择redis
        db_num: 使用db编号
    """
    client_name = ""
    db_num = 0
    prefix = ""

    @property
    def db(self):
        """基于服务发现获取指定redis服务
        TODO(smpcode): 添加服务发现方式获取
        """
        return REDISDB

    @property
    def key(self):
        """构造redis的key
        """
        return Key(self.prefix)


class BaseModel(NSCModel):

    """redis所有model的基类
    :param client_name: 选择redis
    :param db_name: 使用哪个db
    :param prefix: rediskey的前缀
    """

    client_name = ""
    db_num = 0
    prefix = "hr"
