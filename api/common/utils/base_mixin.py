# -*- coding: utf-8 -*-

"""
base_mixin
~~~~~~~~~~~~

组合多个service

:copyright: (c) 2017 smpcode
:authors: smpcode
:version: 1.0 of 2017-04-18

"""


class BaseMixin:

    """ 基础mixin模式，避免使用多重继承
    """

    mixins = {}

    def register(self, name, service):
        """ 注册服务
        :param name: 服务名称
        :param service: 服务实例对象
        """
        if name in self.mixins:
            return
        self.mixins[name] = service

    def unregister(self, name):
        """ 删除服务
        """
        if name in self.mixins:
            del self.mixins[name]

    def __getattr__(self, name):
        """ 将mixin改为可以直接调用注册类的方法
        """
        return self.mixins.get(name, None)
