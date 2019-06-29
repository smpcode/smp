# -*- coding: utf-8 -*-
"""
tree
~~~~~~~~~~~~

用于生成树形结构的对象

:copyright: (c) 2016 smpcode
:authors: smpcode
:version: 1.0 of 2016-07-14

"""
from collections import defaultdict


class DefaultDict(defaultdict):
    '''为defaultdict添加属性操作
    '''

    def __getattr__(self, attr):
        return self[attr]

    def __setattr__(self, attr, val):
        self[attr] = val


def create_tree():
    '''使用字典表示树的节点，非字典类型表示叶子节点
    具体使用请参考测试数据
    '''
    return DefaultDict(create_tree)


def dicts(t):
    '''获取树的叶子节点
    '''
    if isinstance(t, dict):
        return {k: dicts(t[k]) for k in t}
    return t
