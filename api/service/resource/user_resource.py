# -*- coding: utf-8 -*-

"""
account
~~~~~~~~~~~~

对账户表提供对外接口

:copyright: (c) 2017 smpcode
:authors: smpcode
:version: 1.0 of 2017-05-11

"""

from model.mysql.auth_models import (
    AuthUser,
    AuthSystem,
    AuthRole,
    AuthDept,
    AuthResource,
    AuthUserRole,
    AuthKVDB,
    AuthRoleResource
)
from common.db.resource import Resource


class KVResource(Resource):

    """字典表资源
    """

    model = AuthKVDB


class SystemResource(Resource):

    """系统资源
    """

    model = AuthSystem

class DeptResource(Resource):

    """部门资源
    """

    model = AuthDept
    relation_model = (AuthUser,)

    def prepare_data(self, obj, data):
        """动态获取用户信息
        """
        manager = AuthUser.one(id=data['manager'])
        data['manager'] = {
            'id': manager.id,
            'realname': manager.realname,
        }
        return data


class RoleResource(Resource):

    """角色资源
    """
    model = AuthRole
    relation_model = (AuthRoleResource,)


class UserResource(Resource):

    """用户资源定义
    """

    exclude = ("password",)
    model = AuthUser
    relation_model = (AuthDept,)
    include_resources = {'dept': DeptResource}


class UserRoleResource(Resource):

    """用户角色相关资源定义
    """
    model = AuthUserRole
    relation_model = (AuthUser, AuthRole, AuthDept)
    include_resources = {'user': UserResource, 'role': RoleResource}


class RoleResourceResource(Resource):

    """角色资源
    """
    model = AuthRoleResource
    relation_model = (AuthRole, AuthResource)


class ResourceResource(Resource):

    """权限资源类
    """

    model = AuthResource
    relation_model = (AuthRoleResource, AuthSystem)
