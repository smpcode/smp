# -*- coding: utf-8 -*-

"""
user
~~~~~~~~~~~~

用户资源相关接口

:copyright: (c) 2017 smpcode
:authors: smpcode
:version: 1.0 of 2017-05-19

"""
# pylint: disable=arguments-differ
from apps.resource.handler.base import ResourceBaseHandler
from common.helpers.tornado_helpers import ResponseStatus


class ResourcePKHandler(ResourceBaseHandler):

    """单个资源相关API
    """

    SUPPORTED_METHODS = ("GET", "DELETE")

    def get(self, db_name, resource_name, pk):  # pylint: disable=invalid-name
        """获取指定用户信息
        example:
            /smp/resource/warship/user/23
        """
        info = self.resource_service.register(
            db_name, resource_name).read_detail(pk)
        self.make_response(info)

    def delete(self, db_name, resource_name, pk):  # pylint: disable=invalid-name
        """删除指定用户
        """
        info = self.resource_service.register(
            db_name, resource_name).delete(pk)
        # deleted status code = 204
        self.make_response(info, ResponseStatus.deleted)


class ResourceHandler(ResourceBaseHandler):

    """多个资源相关API
    """

    SUPPORTED_METHODS = ("GET", "POST", "PUT", "DELETE", "OPTIONS")

    def get(self, db_name, resource_name):
        """获取用户信息
        example:
            获取第三页，限制每页返回数量为5，id字段需要大于5
            语法需要符合DJANGO_MAP风格:
                {
                    'like': 'like',
                    'eq': '=',
                    'lt': '<',
                    'ilike': 'ilike',
                    'lte': '<=',
                    'in': 'in',
                    'is': 'is',
                    'regexp': 'regexp',
                    'ne': '!=',
                    'gte': '>=',
                    'gt': '>'
                }
            /smp/resource/warship/user?page=3&limit=5&id__gt=5&account__like=%wang%
        """
        info = self.resource_service.register(
            db_name, resource_name).read()
        self.make_response(info)

    def post(self, db_name, resource_name):
        """新增用户信息
        """
        info = self.resource_service.register(
            db_name, resource_name).create()
        # created status code = 201
        self.make_response(info, ResponseStatus.created)

    def put(self, db_name, resource_name):
        """更新用户
        """
        info = self.resource_service.register(db_name, resource_name).edit()
        # update status code = 201
        self.make_response(info, ResponseStatus.created)

    def delete(self, db_name, resource_name):
        """删除指定用户
        """
        info = self.resource_service.register(
            db_name, resource_name).delete()
        # deleted status code = 204
        self.make_response(info, ResponseStatus.deleted)
