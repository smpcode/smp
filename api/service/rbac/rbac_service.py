# -*- coding: utf-8 -*-

"""
rbac_service
~~~~~~~~~~~~

基于角色的权限管理模块

:copyright: (c) 2017 smpcode
:authors: smpcode
:version: 1.0 of 2017-05-26

"""
import logging as log
import itertools

from model.mysql.auth_models import (
    AuthUser,
    AuthRole,
    AuthDept,
    AuthResource,
    AuthUserRole,
    AuthSystem,
    AuthRoleResource,
    AuthApi,
    AuthRoleApi
)

from service.rbac.acl_manager import ACLManager

class RBACService:

    """权限相关服务

    Role Based Access Control
    """
    acl_manager = None

    def __init__(self, database, sys_id):
        """初始化逻辑

        :param database: 数据库对象`class common.db.database.Database`
        :param sys_id: 所属系统的id，用于区分资源
        """
        self.sys_id = sys_id
        self.database = database
        self.user_model = AuthUser.use_db(database)
        self.role_model = AuthRole.use_db(database)
        self.system_model = AuthSystem.use_db(database)
        self.dept_model = AuthDept.use_db(database)
        self.user_role_model = AuthUserRole.use_db(database)
        self.resource_model = AuthResource.use_db(database)
        self.role_resource_model = AuthRoleResource.use_db(database)
        self.auth_api_model = AuthApi.use_db(database)
        # 初始化全局权限
        self.init_acl_manager(self.sys_id)

    def init_acl_manager(self, sys_id=None):
        """初始化权限，当权限变更需要重新初始化，因此需要公开此方法
        :param sys_id: 系统id,用于刷新指定系统的缓存
        """
        if not self.acl_manager:
            self.acl_manager = ACLManager()
        if sys_id is None:
            sys_id = self.sys_id

        if not sys_id:
            log.error("act=init_acl_manager, error = sys_id is required")
            return

        # init role
        self.acl_manager.add_roles(self.role_model.select())
        # init resource
        resources = self.resource_model().get_resources(sys_id)
        if not resources:
            return
        self.acl_manager.add_resources(resources)
        # init role resource
        for role_id, resource_id, method in self.role_resource_model.fetchall():
            self.acl_manager.allow(role_id, method, resource_id)
        return self.acl_manager

    def get_global_acls(self):
        """获取全局权限接入列表字典

        :return: 全局权限字典
        :rtype: dict
        """

        return self.acl_manager.as_dict()

    def get_account_roles(self, account):
        """获取指定账户的roles

        :param account: 账户
        :return: 角色集合
        :rtype: set
        """

        if not account:
            return set()
        user = AuthUser.one(account=account)
        if not user:
            return set()
        return {str(urm.role.id) for urm in self.user_role_model.get_roles(user.id)}

    def get_account_resources(self, account, detail=False):
        """获取指定账户的resources

        :param account: 账户
        :param detail: 是否返回资源详情
        :return: 用户拥有的角色对应的资源
        :rtype: dict
        """
        role_resources = {}
        if not account:
            return {}
        roles = self.get_account_roles(account)
        if not roles:
            return {}
        for role in roles:
            role_resources[role] = self.acl_manager.get_resources(role, detail=detail)
        return role_resources

    def get_account_routes(self, account):
        """获取账户有权限路由

        :param account: 账户
        :return: 返回资源以及对应的权限列表
            example:
                {"/": ["read", "update", "delete"]}
        :rtype: dict
        """
        routes = {}
        if not account:
            return
        account_resources = self.get_account_resources(account, detail=True)
        for role, resources in account_resources.items():
            for res in resources:
                operations = self.acl_manager.get_operations(role, res.id)
                if not res.uri:
                    continue
                routes[res.uri] = list(set(routes.get(res.uri, [])) | set(operations))
        return routes

    def update_permission(self, role_id, add_routes, delete_routes):
        """更新指定角色的权限信息

        :param role_id: 角色id
        :type role_id: int
        :param add_routes: 需要添加的资源权限信息
        :type add_routes: dict
        :param delete_routes: 需要删除的资源权限信息
        :type delete_routes: dict
        """
        # 1, 将系统中未添加的资源进行添加
        self.update_resource(add_routes)
        # 2, 将角色对应的资源进行添加
        self.update_role_resource(role_id, add_routes)
        # 3，删除资源
        self.delete_role_resource(role_id, delete_routes)

    # todo从权限表中查询，不应该直接从数据库中查
    def update_resource(self, resources):
        """更新资源,直接更新到资源表即可

        :param resources: 资源列表
        :type resources: list
        :return: 返回是否更新成功
        :rtype: bool
        """
        if not resources:
            return
        sys = self.system_model.one(id=self.sys_id)
        if not sys:
            return
        for uri, config in resources.items():
            res = self.resource_model.one(uri=uri, sys=sys)
            if not res:
                self.resource_model.create(
                    uri=uri, sys=sys, name=config.get('name', ''))

    def update_role_resource(self, role_id, resources):
        """更新角色对应资源,需要将角色之前的资源项删除然后添加

        :param role_id: 角色id
        :param resources: 资源列表
        """
        if not role_id or not resources:
            return
        role = self.role_model.one(id=role_id)
        if not role:
            return
        for uri, config in resources.items():
            resource = self.resource_model.one(uri=uri)
            if not resource:
                continue
            if not isinstance(config, dict):
                continue
            for method in config.get("methods", []):
                if not method:
                    continue
                self.role_resource_model.get_or_create(
                    role=role, resource=resource, method=method)

    def delete_role_resource(self, role_id, resources):
        """删除角色资源

        :param role_id: 角色id
        :param resources: 需要删除的资源
        """
        if not role_id or not resources:
            return
        role = self.role_model.one(id=role_id)
        if not role:
            return
        for uri, config in resources.items():
            resource = self.resource_model.one(uri=uri)
            if not resource:
                continue
            for method in config.get('methods', []):
                self.role_resource_model.delete().where(
                    (AuthRoleResource.resource == resource) &
                    (AuthRoleResource.method == method) &
                    (AuthRoleResource.role == role)).execute()

    def add_role_users(self, role_id, user_ids):
        """批量添加指定角色的用户

        :param role_id: 角色id
        :param user_ids: 用户id列表
        :type user_ids: list
        """
        if not role_id or not user_ids:
            return
        role = self.role_model.one(id=role_id)
        if not role:
            return
        for user_id in user_ids:
            user = self.user_model.one(id=user_id)
            if not user:
                continue
            self.user_role_model.get_or_create(user=user, role=role)

    def get_operations(self, account, resource):
        """通过账户和资源来获取响应的操作权限

        :param account: 账户
        :param resource: 资源
        :return: 该账户对应资源的权限操作列表
        :rtype: list
        """
        if not account:
            return []
        routes = self.get_account_routes(account)
        return list(routes.get(resource, []))

    def get_routes_by_role(self, role):
        """通过角色获取响应的权限路由表

        :param role: 角色id
        :return: 角色权限路由
        :rtype: {}
        """
        routes = {}
        if not role:
            return {}
        resources = self.acl_manager.get_resources(role, detail=True)
        if not resources:
            return routes
        for res in resources:
            operations = self.acl_manager.get_operations(role, res.id)
            if res.uri:
                routes[res.uri] = operations
        return routes

    def get_sys_apis(self, sys_id):
        """获取系统api列表
        ：param sys_id: 系统id
        """
        if not sys_id:
            return []
        ret = []
        apis = self.auth_api_model.select().where(self.auth_api_model.sys == sys_id)
        for api in apis:
            methods = [{'id': str(api.id) + '-' + i, 'name': i} for i in api.method.split(',')]
            ret.append({
                'id': str(api.id), 'name': api.uri + '--' + api.doc, 'children': methods
            })
        return ret
