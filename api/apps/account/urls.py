# -*- coding: utf-8 -*-

"""
urls
~~~~~~~~~~~~

路由规则

:copyright: (c) 2017 smpcode
:authors: smpcode
:version: 1.0 of 2017-04-21

"""

from apps.account.handler import (
    index,
    account,
    dept,
    login,
    password,
    rbac,
    kv,
)

URL_ROUTES = [
    (r"/", index.IndexHandler),
    (r"/smp/account/info", account.AccountHandler),
    (r"/smp/account/login", login.AccountLoginHandler),
    (r"/smp/account/password", password.AccountPasswordHandler),
    (r"/smp/dept/nodes", dept.DeptHandler),
    (r"/smp/rbac/role/resource", rbac.RoleResourceHandler),
    (r"/smp/rbac/acls", rbac.RBACHandler),
    (r"/smp/rbac/user/role", rbac.UserRoleHandler),
    (r"/smp/rbac/user/resource", rbac.UserResourceHandler),
    (r"/smp/kv", kv.KVHandler),
]
