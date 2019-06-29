# -*- coding: utf-8 -*-

"""
utils
~~~~~~~~~~~~

db相关公用方法

:copyright: (c) 2017 smpcode
:authors: smpcode
:version: 1.0 of 2017-05-10

"""
# pylint: disable=protected-access
import math
import re

from peewee import DoesNotExist
from peewee import ForeignKeyField
from peewee import Model
from peewee import SelectQuery


def get_object(query_or_model, *query):
    """获取查询对象
    """
    if not isinstance(query_or_model, SelectQuery):
        query_or_model = query_or_model.select()
    try:
        return query_or_model.where(*query).get()
    except DoesNotExist:
        return None


class PaginatedQuery:

    """带分页功能的查询类
    """
    # 用于分页的字段
    page_var = 'page'

    def __init__(self, handler, query_or_model, paginate_by):
        """实例化分页对象
        :param handler: tornado请求对象
        :param query_or_model: model或query对象
        :param paginate_by: 排序规则
        """
        self.paginate_by = paginate_by
        self.handler = handler

        if isinstance(query_or_model, SelectQuery):
            self.query = query_or_model
            self.model = self.query.model_class
        else:
            self.model = query_or_model
            self.query = self.model.select()

    def get_page(self):
        """获取当前页
        """
        curr_page = self.handler.get_argument(self.page_var, '1')
        if curr_page and curr_page.isdigit():
            return int(curr_page)
        return 1

    def get_pages(self):
        """获取页数
        """
        if not hasattr(self, '_get_pages'):
            self._get_pages = int(math.ceil(
                float(self.query.count()) / self.paginate_by))
        return self._get_pages

    def get_total(self):
        """获取记录数,生命周期为一个对象实例
        """
        if not hasattr(self, '_total'):
            self._total = self.query.count()
        return self._total

    def get_list(self):
        """获取分页列表
        """
        return self.query.paginate(self.get_page(), self.paginate_by)


def slugify(s):
    """过滤字符串
    """
    return re.sub('[^a-z0-9_\-]+', '-', s.lower())


def get_dictionary_from_model(model, fields=None, exclude=None):
    """从model获取字典类型
    """
    model_class = type(model)
    data = {}

    fields = fields or {}
    exclude = exclude or {}
    curr_exclude = exclude.get(model_class, [])
    curr_fields = fields.get(model_class, model._meta.sorted_field_names)

    for field_name in curr_fields:
        if field_name in curr_exclude:
            continue
        field_obj = model_class._meta.fields[field_name]
        field_data = model._data.get(field_name)
        if isinstance(field_obj, ForeignKeyField) and field_data and field_obj.rel_model in fields:
            rel_obj = getattr(model, field_name)
            data[field_name] = get_dictionary_from_model(
                rel_obj, fields, exclude)
        else:
            data[field_name] = field_data
    return data


def get_model_from_dictionary(model, field_dict):
    """基于字典类型获取model实例
    """
    if isinstance(model, Model):
        model_instance = model
        check_fks = True
    else:
        model_instance = model()
        check_fks = False
    models = [model_instance]
    for field_name, value in field_dict.items():
        field_obj = model._meta.fields[field_name]
        if isinstance(value, dict):
            rel_obj = field_obj.rel_model
            if check_fks:
                try:
                    rel_obj = getattr(model, field_name)
                except field_obj.rel_model.DoesNotExist:
                    pass
                if rel_obj is None:
                    rel_obj = field_obj.rel_model
            rel_inst, rel_models = get_model_from_dictionary(rel_obj, value)
            models.extend(rel_models)
            setattr(model_instance, field_name, rel_inst)
        else:
            setattr(model_instance, field_name, field_obj.python_value(value))
    return model_instance, models
