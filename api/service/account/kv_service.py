# -*- coding: utf-8 -*-

"""
kv_service
~~~~~~~~~~~~

键值对配置信息,当做通用数据字典使用

:copyright: (c) 2017 smpcode
:authors: smpcode
:version: 1.0 of 2017-05-04

"""
import logging as log
import functools

from common import errors
from model.mysql.auth_models import (
    AuthKVDB,
)


class KVService:

    """通用的KV对配置,其中Value为字典类型
    """
    support_methods = frozenset(['GET', 'SET', 'DELETE', 'SERARCH'])
    method_prefix = "do_"

    def __init__(self, database):
        self.database = database
        self.kv_model = AuthKVDB.use_db(database)

    def _wrap(self, method, *args, **kwargs):
        '''打包pipeline的方法

        :param: method: 要执行的方法
        :param args: 执行方法的参数
        :param kwargs: 字典参数
        '''
        log.debug("execute method:%s, args=%s, kwargs=%s",
                  method, args, kwargs)
        if method.upper() not in self.support_methods:
            raise errors.ForbiddenError()

        real_method = self.method_prefix + method
        func = getattr(self.kv_model, real_method)
        return func(*args, **kwargs)

    def __getattr__(self, method):
        """代理kv_model的方法,执行get,set,delete,search操作
        """
        return functools.partial(self._wrap, method)
