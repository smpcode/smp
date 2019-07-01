# -*- coding: utf-8 -*-

"""
rbac
~~~~~~~~~~~~

基于RBAC的权限控制API

:copyright: (c) 2019 smpcode
:authors: smpcode
:version: 1.0 of 2019-05-26

"""
# pylint: disable=arguments-differ

import ujson as json
from webargs import fields
from webargs.tornadoparser import use_args

from common import errors
from common.helpers.tornado_helpers import authenticated
from common.helpers.tornado_helpers import ResponseStatus
from apps.account.handler.base import AccountBaseHandler


class UserRoleHandler(AccountBaseHandler):

    """用户角色管理接口类
    """

    def get(self):
        """获取用户拥有的角色
        """
        pass

    def delete(self):
        """删除用户拥有的某个角色
        """
        pass

    @use_args({
        "role_id": fields.Str(required=True),  # 角色id
        "user_ids": fields.Str(required=True),  # 用户列表,json 序列化的数据
    })
    @authenticated
    def post(self, reqargs):
        """用户新增角色
        """
        role_id = reqargs['role_id']
        try:
            user_ids = json.loads(reqargs['user_ids'])
        except ValueError:
            raise errors.ValidateError()
        self.rbac_service.add_role_users(role_id, user_ids)


class RoleResourceHandler(AccountBaseHandler):

    """角色资源管理接口类
    """

    @use_args({
        "role_id": fields.Str(required=True),  # 角色id
    })
    @authenticated
    def get(self, reqargs):
        """获取指定角色对应的资源
        """
        role_id = reqargs['role_id']
        role_routes = self.rbac_service.get_routes_by_role(role_id)
        self.make_response(role_routes)

    @use_args({
        "role_id": fields.Str(required=True),  # 角色id
    })
    @authenticated
    def delete(self, reqargs):
        """删除指定角色对应的资源
        """
        pass

    @use_args({
        "role_id": fields.Str(required=True),  # 角色id
    })
    @authenticated
    def post(self, reqargs):
        """新增角色对应的资源
        """
        pass


class UserResourceHandler(AccountBaseHandler):

    """用户资源
    """

    @use_args({
        "account": fields.Str(required=True),  # 账户
        "resource": fields.Str(required=True),  # 资源
    })
    @authenticated
    def get(self, reqargs):
        """获取用户对指定资源的操作权限列表
        """
        account = reqargs['account']
        resource = reqargs['resource']
        operations = self.rbac_service.get_operations(account, resource)
        self.make_response(operations)


class RBACHandler(AccountBaseHandler):

    """权限接入控制
    """

    @use_args({
        "account": fields.Str(required=True),  # 账户
    })
    @authenticated
    def get(self, reqargs):
        """获取指定账户的权限信息
        """
        routes = self.rbac_service.get_account_routes(reqargs["account"])
        self.make_response(routes)

    @use_args({
        "role_id": fields.Str(required=True),  # 角色id
        # 角色的权限列表,经过json.dumps后的数据
        "add_routes": fields.Str(),
        "delete_routes": fields.Str(),
    })
    @authenticated
    def post(self, reqargs):
        """更新权限信息
        """
        role_id = reqargs['role_id']
        try:
            add_routes = json.loads(reqargs["add_routes"])
            delete_routes = json.loads(reqargs["delete_routes"])
        except ValueError as error:
            self.logger("parse param error=%s", error)
            raise errors.ValidateError()
        self.logger.debug("add_routes=%s, delete_routes=%s",
                          add_routes, delete_routes)
        self.rbac_service.update_permission(role_id, add_routes, delete_routes)
        self.make_response('ok', ResponseStatus.created)
