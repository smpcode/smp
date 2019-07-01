# -*- coding: utf-8 -*-

"""
test_singleton
~~~~~~~~~~~~

please add description for this module

:copyright: (c) 2016 smpcode
:authors: smpcode
:version: 1.0 of 2016-07-18

"""
from .singleton import SingletonMixin


class A(SingletonMixin):
    """ 测试类A
    """

    def __init__(self):
        print("in")
        self.a = []

    def add(self, data):
        """添加数据
        """
        self.a.append(data)


class B(SingletonMixin):
    """ 测试类B
    """
    pass


def test_singleton():
    """测试单例模式
    """
    a1, a2 = A.instance(), A.instance()
    a1.add(1)
    a2.add(2)
    assert a1 is a2
    assert 2 in a1.a
    assert 1 in a2.a
    assert a1.a is a2.a
