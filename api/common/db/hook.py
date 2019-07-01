# -*- coding: utf-8 -*-

"""
hook
~~~~~~~~~~~~

db hook for database crud lifetime

:copyright: (c) 2017 smpcode
:authors: smpcode
:version: 1.0 of 2017-04-28

"""

# pylint: disable=invalid-name
from peewee import Model as _Model
from peewee import IntegerField


class Hook(object):

    '''钩子修饰器,提供sql操作基础回掉函数
    Stores a list of receivers (callbacks) and calls them
    when the “send” method is invoked.
    '''

    def __init__(self):
        self._flush()

    def connect(self, receiver, name=None, sender=None):
        '''连接
        '''
        name = name or receiver.__name__
        if name not in self._receivers:
            self._receivers[name] = (receiver, sender)
            self._receiver_list.append(name)
        else:
            raise ValueError('receiver named %s already connected' % name)

    def disconnect(self, receiver=None, name=None):
        '''关闭连接
        '''
        if receiver:
            name = receiver.__name__
        if name:
            del self._receivers[name]
            self._receiver_list.remove(name)
        else:
            raise ValueError('a receiver or a name must be provided')

    def __call__(self, name=None, sender=None):
        def decorator(fn):
            '''函数修饰器
            '''
            self.connect(fn, name, sender)
            return fn
        return decorator

    def send(self, instance, *args, **kwargs):
        '''执行实例调用
        '''
        sender = type(instance)
        responses = []
        for name in self._receiver_list:
            r, s = self._receivers[name]
            if s is None or isinstance(instance, s):
                # responses.append((r, r(sender, instance, *args, **kwargs)))
                r(sender, instance, *args, **kwargs)  # 执行回调函数,无需保存结果
        return responses

    def _flush(self):
        '''刷新
        '''
        self._receivers = {}
        self._receiver_list = []


pre_save = Hook()
post_save = Hook()
pre_delete = Hook()
post_delete = Hook()
pre_init = Hook()
post_init = Hook()


class Model(_Model):

    '''总的基础model类,添加回调函数
    '''

    def __init__(self, *args, **kwargs):
        '''添加初始化钩子
        '''
        super(Model, self).__init__(*args, **kwargs)
        pre_init.send(self)

    def prepared(self):
        '''添加初始化完成钩子
        '''
        super(Model, self).prepared()
        post_init.send(self)

    def save(self, *args, **kwargs):
        '''save前后添加钩子
        '''
        pk_value = self._get_pk_value()
        created = kwargs.get('force_insert', False) or not bool(pk_value)
        pre_save.send(self, created=created)
        super(Model, self).save(*args, **kwargs)
        post_save.send(self, created=created)

    @classmethod
    def delete(cls):
        """删除前后添加钩子, 如果含deleted字段使用逻辑删除
        """
        if 'deleted' in cls._meta.fields:
            return super(Model, cls).update(deleted='1')
        else:
            return super(Model, cls).delete()

    @classmethod
    def select(cls, *selection):
        """逻辑删除后的select
        """
        if 'deleted' in cls._meta.fields:
            if isinstance(cls.deleted, IntegerField):
                deleted = 0
            else:
                deleted = '0'
            return super(Model, cls).select(*selection).where(cls.deleted == deleted)
        else:
            return super(Model, cls).select(*selection)

    def delete_instance(self, *args, **kwargs):
        '''删除前后添加钩子,如果disable字段存在自动使用逻辑删除
        '''
        pre_delete.send(self)
        if 'deleted' in self._meta.fields:
            setattr(self, 'deleted', '1')
            super(Model, self).save()
        else:
            super(Model, self).delete_instance(*args, **kwargs)
        post_delete.send(self)
