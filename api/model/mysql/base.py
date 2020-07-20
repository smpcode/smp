# -*- coding: utf-8 -*-

"""
base
~~~~~~~~~~~~

peewee base model

:copyright: (c) 2019 smpcode
:authors: smpcode
:version: 1.0 of 2019-04-28

"""
# pylint: disable=protected-access,unsubscriptable-object
import logging as log
from datetime import datetime

from peewee import DoesNotExist
from playhouse.read_subordinate import ReadSubordinateModel
# inner
from common.db.hook import (
    post_delete,
    pre_save,
)
from common.db.hook import Model as _Model
from common.db.database import Database


class BaseModel(_Model, ReadSubordinateModel):

    '''BaseModel的封装
    '''
    current_user = None

    @classmethod
    def use_db(cls, db):
        """动态设置使用的database

        :param db: 数据库对象`common.db.database.Database`
        """
        cls._meta.database = db.main_database
        cls._meta.read_subordinates = db.subordinates_database or [db.main_database]
        return cls

    @classmethod
    def one(cls, *query, **kwargs):
        '''获取单条数据

        :retrun: 返回单条数据不存在则返回None
        '''
        try:
            return cls.get(*query, **kwargs)
        except DoesNotExist:
            return None

    def __eq__(self, other):
        """提供直接根据==判断方法
        """
        return hasattr(other, "id") and self.id == other.id

    def __hash__(self):
        """提供hash支持
        """
        return hash(self.id)


@post_delete(name='all_model_post_delete')
def post_delete_handler(sender, instance):
    '''所有的model删除后回调函数
    '''
    if Database.current_user is None:
        current_user = 'system'
    else:
        current_user = Database.current_user['account']
    log.info('account=%s,command=delete,table=%s,record_id=%s',
             current_user,
             instance._meta.db_table,
             instance.id)


@pre_save(name='all_model_pre_save')
def pre_save_handler(sender, instance, created):
    '''更新和保存前执行该回调
    '''
    if not isinstance(instance, sender):
        return
    time_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    fields = instance._meta.fields
    if Database.current_user is None:
        current_user = 'system'
    else:
        current_user = Database.current_user['account']
    if created:
        # insert操作
        if 'create_time' in fields:
            instance.create_time = time_now
        if 'create_user' in fields:
            instance.create_user = current_user
    else:
        # update操作
        if 'update_time' in fields:
            instance.update_time = time_now
        if 'update_user' in fields:
            instance.update_user = current_user
