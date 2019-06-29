# -*- coding: utf-8 -*-

"""
acl_manager
~~~~~~~~~~~~

access control list manager
权限接入列表控制

:copyright: (c) 2017 smpcode
:authors: smpcode
:version: 1.0 of 2017-05-26

"""
import peewee
from common.utils import tree


class ACLManager:

    """接入控制逻辑
    """
    role_map = {}
    resource_map = {}

    def __init__(self, roles=None, resources=None):
        """初始化

        :param roles: 支持的角色列表
        :param resources: 支持的资源列表
        """

        self.roles = roles or set()
        self.resources = resources or set()
        self.acl_tree = tree.create_tree()

    def add_role(self, role):
        """添加角色

        :param role: Model对象实例
        """
        if not role:
            return
        role_id = str(role.id)
        if isinstance(role, peewee.Model):
            self.role_map[role_id] = role
        self.roles.add(role_id)

    def add_roles(self, roles):
        """批量添加角色

        :param roles: 角色集合
        :type roles: set
        """

        for role in roles:
            self.add_role(role)

    def add_resource(self, resource):
        """添加资源

        :param resource: 资源Model对象实例
        """
        if not resource:
            return
        resource_id = str(resource.id)
        if isinstance(resource, peewee.Model):
            self.resource_map[resource_id] = resource
        self.resources.add(resource_id)

    def add_resources(self, resources):
        """批量添加资源

        :param resources: 资源集合
        :type resources: set
        """

        for resource in resources:
            self.add_resource(resource)

    def get_resources(self, role, detail=False):
        """获取角色对应的资源列表

        :param role: 角色id
        :type role: str
        :param detail: 是否返回详情,默认不返回
        :type detail: bool
        :return: 返回资源集合,如果detail为True返回集合的对象为dict否则仅仅返回id
        :rtype: set
        """

        role = str(role)
        resources = set()
        if role in self.roles:
            for key in self.acl_tree[role].keys():
                if detail:
                    resources.add(self.resource_map[key])
                else:
                    resources.add(key)
        return resources

    def get_operations(self, role, resource):
        """获取角色对应资源的操作权限

        :param role: 角色id
        :type role: str
        :param resource: 资源id
        :type resource: str
        :return: 操作权限
        :rtype: list
        """

        role, resource = str(role), str(resource)
        if role in self.roles and resource in self.resources:
            return self.acl_tree[role][resource].keys()
        return []

    def allow(self, role, operation, resource):
        """是否允许某个角色执行某个资源操作,角色+资源可以对应多个方法

        :param role: 角色
        :type role: str
        :param operation: 操作方法：index, delete, create, update, download等
        :type operation: str
        :param resource: 资源
        :type resource: str
        """

        role, operation, resource = str(role), str(operation), str(resource)
        if role in self.roles and resource in self.resources and operation:
            self.acl_tree[role][resource][operation] = True

    def is_allowed(self, role, operation, resource):
        """验证某个角色是否有权限操作某个资源

        :rtype: bool
        """

        return operation in self.acl_tree.get(str(role), {}).get(str(resource), {})

    def as_dict(self):
        """将acl_tree转为字典
        """

        return tree.dicts(self.acl_tree)

    def __repr__(self):
        """格式化输出
        """

        return self.__str__()

    def __str__(self):
        """字符串查看
        """

        return "ACLManager: roles={}, resources={}, acl_tree={}".format(
            self.roles,
            self.resources,
            tree.dicts(self.acl_tree)
        )
