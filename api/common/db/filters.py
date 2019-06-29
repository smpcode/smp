# -*- coding: utf-8 -*-

"""
filters
~~~~~~~~~~~~

搜索条件过滤

:copyright: (c) 2017 smpcode
:authors: smpcode
:version: 1.0 of 2017-05-10

"""
# pylint: disable=protected-access
from peewee import ForeignKeyField


class FieldTreeNode(object):

    """字段树节点
    """

    def __init__(self, model, fields, children=None):
        """初始化节点
        :param model: peewee的model类
        :param fields: model的字段
        :param children: 子节点
        """
        self.model = model
        self.fields = fields
        self.children = children or {}


def make_field_tree(model, fields, exclude, force_recursion=False, seen=None):
    """生成字段的树形结构
    """
    # 无明确字段的时候使用全部字段
    no_explicit_fields = fields is None
    if no_explicit_fields:
        fields = model._meta.sorted_field_names
    # 设置不包含某字段
    exclude = exclude or []
    # 对于包含外键的model，其关联model存为seen
    seen = seen or set()

    model_fields = []
    children = {}

    for field_obj in model._meta.sorted_fields:
        if field_obj.name in exclude or field_obj in seen:
            continue

        if field_obj.name in fields:
            model_fields.append(field_obj)

        if isinstance(field_obj, ForeignKeyField):
            seen.add(field_obj)
            if no_explicit_fields:
                rel_fields = None
            else:
                rel_fields = [
                    rf.replace('%s__' % field_obj.name, '')
                    for rf in fields if rf.startswith('%s__' % field_obj.name)
                ]
                if not rel_fields and force_recursion:
                    rel_fields = None

            rel_exclude = [
                rx.replace('%s__' % field_obj.name, '')
                for rx in exclude if rx.startswith('%s__' % field_obj.name)
            ]
            children[field_obj.name] = make_field_tree(
                field_obj.rel_model, rel_fields, rel_exclude, force_recursion, seen)

    return FieldTreeNode(model, model_fields, children)
