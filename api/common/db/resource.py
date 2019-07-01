# -*- coding: utf-8 -*-

"""
rest
~~~~~~~~~~~~

基于model的rest风格api封装

将model转换为Resource，每个model由resource封装后支持api的create,update,delete,query操作

:copyright: (c) 2017 smpcode
:authors: smpcode
:version: 1.0 of 2017-05-10

"""
# pylint: disable=protected-access
import logging as log
import operator
try:
    import ujson as json
except ImportError:
    import json

from functools import reduce

import tornado
from peewee import DQ
from peewee import DJANGO_MAP

from common.errors import BadRequestError
from common.db.filters import make_field_tree
from common.db.serializer import Deserializer
from common.db.serializer import Serializer
from common.db.utils import (
    PaginatedQuery,
    slugify,
    get_object
)


class Resource:

    """资源类接口
    """
    # 分页逻辑
    paginate_by = 20
    # 允许单页返回的最大数据量
    max_paginate_by = 100

    # 限制输出配置
    fields = None  # 默认用于排序的字段
    exclude = None

    # 用于绑定Model,该项为必选项
    model = None

    # 过滤参数
    filter_exclude = None
    filter_fields = None
    filter_recursive = True

    # 定义关联资源
    include_resources = None  # 需要外键支持
    relation_model = None  # 相关Model，用于数据库初始化
    # 是否支持递归删除
    delete_recursive = False

    default_arguments = {
        "ordering": "ordering",  # 参数用于排序
        "limit": "limit",  # 用于限制分页数
        "data": "data",  # 用于传递create,update的值
        "pk": "pk",  # 用于获取主键值delete,detail两个接口需要
    }

    def __init__(self, handler):
        """资源类定义
        :param model: peewee Model实例
        :param handler: tornado handler实例
        """
        self.handler = handler

        self.pk = self.model._meta.primary_key

        self._fields = {
            self.model: self.fields or self.model._meta.sorted_field_names}
        if self.exclude:
            self._exclude = {self.model: self.exclude}
        else:
            self._exclude = {}

        self._filter_fields = self.filter_fields or list(
            self.model._meta.sorted_field_names)
        self._filter_exclude = self.filter_exclude or []

        self._resources = {}

        # 关联外键资源
        if self.include_resources:
            for field_name, resource in self.include_resources.items():
                # field_obj = self.model._meta.fields[field_name]
                resource_obj = resource(self.handler)
                self._resources[field_name] = resource_obj
                self._fields.update(resource_obj._fields)
                self._exclude.update(resource_obj._exclude)

                self._filter_fields.extend(
                    ['%s__%s' % (field_name, ff) for ff in resource_obj._filter_fields])
                self._filter_exclude.extend(
                    ['%s__%s' % (field_name, ff) for ff in resource_obj._filter_exclude])

            self._include_foreign_keys = True
        else:
            self._include_foreign_keys = False

        self._field_tree = make_field_tree(
            self.model, self._filter_fields, self._filter_exclude, self.filter_recursive)

    def get_model_name(self):
        """获取model名称
        """
        return slugify(self.model.__name__)

    def get_url_name(self, request_arguments):
        """获取请求地址
        """
        uri = self.handler.request.uri.split("?")[0]
        arg_list = []
        for key, val in request_arguments.items():
            if isinstance(val, list):
                val = self.unicode(val[-1])
            arg_list.append("{}={}".format(key, val))
        uri_arg = "&".join(arg_list)
        return '{}?{}'.format(
            uri,
            uri_arg,
        )

    @staticmethod
    def unicode(key):
        """对bytes类型进行转换
        """
        if isinstance(key, bytes):
            return key.decode("utf8")
        return key

    @property
    def args(self):
        """请求参数
        """
        return self.handler.request.arguments

    def get_arg_list(self, arg):
        """获取多个相同query
        """
        return self.handler.get_arguments(arg)

    def get_arg(self, arg, default=None):
        """获取单个参数
        """
        # 从form表和请求参数获取
        data = self.handler.get_argument(arg, default)
        # 如果没有获取成功，再次从request body中获取，request payload方式
        if not data:
            arg_dic = {}
            file_dic = {}
            tornado.httputil.parse_body_arguments(
                'application/x-www-form-urlencoded', self.handler.request.body, arg_dic, file_dic)
            data = arg_dic.get(arg, default) or file_dic.get(arg, default)
        return data

    def get_query(self):
        """获取实例查询
        """
        return self.model.select()

    def process_query(self, query):
        """构造query
        """
        raw_filters = {}

        # clean and normalize the request parameters
        for key in self.args:
            orig_key = key
            if key.startswith('-'):
                negated = True
                key = key[1:]
            else:
                negated = False
            if '__' in key:
                expr, op = key.rsplit('__', 1)
                if op not in DJANGO_MAP:
                    expr = key
                    op = 'eq'
            else:
                expr = key
                op = 'eq'
            raw_filters.setdefault(expr, [])
            raw_filters[expr].append(
                (op, self.get_arg_list(orig_key), negated)
            )

        # 和model field对比过滤出来符合要求的query
        queue = [(self._field_tree, '')]
        while queue:
            node, prefix = queue.pop(0)
            for field in node.fields:
                filter_expr = '%s%s' % (prefix, field.name)
                if filter_expr in raw_filters:
                    for op, arg_list, negated in raw_filters[filter_expr]:
                        query = self.apply_filter(
                            query, filter_expr, op, arg_list, negated)

            for child_prefix, child_node in node.children.items():
                queue.append((child_node, prefix + child_prefix + '__'))

        return query

    def apply_filter(self, query, expr, op, arg_list, negated):
        """构造查询条件

        :param query: query对象
        :param expr: 查询语句
        :param op: 查询操作
        :param arg_list: 请求列表
        :param negated: 排序方式
        """
        query_expr = '%s__%s' % (expr, op)

        def constructor(kwargs):
            """构造django风格的查询表达式
            类似：{"username__eq": "wlc", "id__bt": 2}
            """
            return negated and ~DQ(**kwargs) or DQ(**kwargs)

        if op == 'in':
            # 对于in操作进行转换，将请求参数中类似：1,2,3,4的转为列表[1,2,3,4]
            arg_list = [i.strip() for i in arg_list[0].split(',')]
            return query.filter(constructor({query_expr: arg_list}))
        elif len(arg_list) == 1:
            return query.filter(constructor({query_expr: arg_list[0]}))
        else:
            query_clauses = [
                constructor({query_expr: val}) for val in arg_list
            ]
            return query.filter(reduce(operator.or_, query_clauses))

    def get_serializer(self):
        """序列化器
        """
        return Serializer()

    def get_deserializer(self):
        """获取反序列化
        """
        return Deserializer()

    def prepare_data(self, obj, data):  # pylint: disable=unused-argument
        """预处理逻辑，做为后期钩子使用
        """
        return data

    def serialize_object(self, obj):
        """对象序列化
        """
        s = self.get_serializer()
        return self.prepare_data(
            obj, s.serialize_object(obj, self._fields, self._exclude)
        )

    def serialize_query(self, query):
        """query序列化
        """
        s = self.get_serializer()
        return [
            self.prepare_data(obj, s.serialize_object(
                obj, self._fields, self._exclude))
            for obj in query
        ]

    def deserialize_object(self, data, instance):
        """反序列化对象
        """
        d = self.get_deserializer()
        return d.deserialize_object(instance, data)

    def response_bad_request(self):
        """请求不合法
        """
        raise BadRequestError("bad request")

    def response(self, data):
        """返回响应结果
        """
        return data

    def save_object(self, instance, raw_data):
        """保存
        """
        log.debug("save_object: raw_data=%s", raw_data)
        instance.save()
        return instance

    def apply_ordering(self, query):
        """添加排序方式
        """
        ordering = self.get_arg(self.default_arguments['ordering'], '')
        if ordering:
            desc, column = ordering.startswith('-'), ordering.lstrip('-')
            if column in self.model._meta.fields:
                field = self.model._meta.fields[column]
                query = query.order_by(
                    field.asc() if not desc else field.desc())
        return query

    def get_request_metadata(self, paginated_query):
        """获取请求元数据
        """
        var = paginated_query.page_var
        request_arguments = self.args.copy()

        current_page = paginated_query.get_page()
        next_page = previous_page = ''

        if current_page > 1:
            request_arguments[var] = current_page - 1
            previous_page = self.get_url_name(request_arguments)
        page_total = paginated_query.get_pages()
        if current_page < page_total:
            request_arguments[var] = current_page + 1
            next_page = self.get_url_name(request_arguments)

        return {
            'total': paginated_query.get_total(),
            'page_total': page_total,
            'current_page': current_page,
            'previous': previous_page,
            'next': next_page,
        }

    def get_paginate_by(self):
        """获取分页逻辑
        """
        try:
            paginate_by = int(self.get_arg(self.default_arguments['limit'],
                                           self.paginate_by))
        except ValueError:
            paginate_by = self.paginate_by
        else:
            if self.max_paginate_by:
                paginate_by = min(
                    paginate_by, self.max_paginate_by)  # 限制返回的最大数据量
        return paginate_by

    def paginated_object_list(self, filtered_query):
        """返回支持分页的object列表
        """
        paginate_by = self.get_paginate_by()
        pq = PaginatedQuery(self.handler, filtered_query, paginate_by)
        meta_data = self.get_request_metadata(pq)

        query_dict = self.serialize_query(pq.get_list())

        return self.response({
            'meta': meta_data,
            'objects': query_dict,
        })

    def read(self):
        """读取资源
        """
        if self.default_arguments["pk"] in self.args:
            return self.read_detail()
        return self.read_by_page()

    def read_by_page(self):
        """返回分页列表
        """
        query = self.get_query()
        query = self.apply_ordering(query)

        # process any filters
        query = self.process_query(query)

        if self.paginate_by or self.default_arguments['limit'] in self.args:
            return self.paginated_object_list(query)

        return self.response(self.serialize_query(query))

    def read_detail(self, pk=None):
        """返回对象详情
        """
        if not pk:
            pk = self.get_arg(self.default_arguments["pk"])
        if not pk:
            raise BadRequestError("{} is required".format(
                self.default_arguments["pk"]))
        obj = get_object(self.get_query(), self.pk == pk)
        if not obj:
            raise BadRequestError("does not existe pk=%s", pk)
        return self.response(self.serialize_object(obj))

    def save_related_objects(self, instance, data):
        """保存关联数据库对象
        """
        for k, v in data.items():
            if k in self._resources and isinstance(v, dict):
                rel_resource = self._resources[k]
                rel_obj, _ = rel_resource.deserialize_object(
                    v, getattr(instance, k))
                rel_resource.save_related_objects(rel_obj, v)
                setattr(instance, k, rel_resource.save_object(rel_obj, v))

    def read_request_data(self):
        """获取请求data字段
        """
        data = self.get_arg(self.default_arguments["data"], "")
        return json.loads(data)

    def create(self):
        """create实现,包括create关联对象
        """
        try:
            data = self.read_request_data()
        except ValueError:
            return self.response_bad_request()

        obj, _ = self.deserialize_object(data, self.model())

        self.save_related_objects(obj, data)
        obj = self.save_object(obj, data)

        return self.response(self.serialize_object(obj))

    def edit(self):
        """edit实现,包括关联对象
        """
        try:
            data = self.read_request_data()
        except ValueError:
            return self.response_bad_request()

        obj, _ = self.deserialize_object(data, self.model())

        self.save_related_objects(obj, data)
        obj = self.save_object(obj, data)

        return self.response(self.serialize_object(obj))

    def delete(self, pk=None):
        """delete逻辑实现
        """
        if not pk:
            pk = self.get_arg(self.default_arguments["pk"])
        if not pk:
            raise BadRequestError("{} is required".format(
                self.default_arguments["pk"]))
        obj = get_object(self.get_query(), self.pk == pk)
        if not obj:
            return {'deleted': 1}
        res = obj.delete_instance(recursive=self.delete_recursive)
        return {'deleted': res}
