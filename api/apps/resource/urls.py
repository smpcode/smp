# -*- coding: utf-8 -*-

"""
urls
~~~~~~~~~~~~

路由规则

:copyright: (c) 2019 smpcode
:authors: smpcode
:version: 1.0 of 2019-04-21

"""

from apps.resource.handler import resource

from service.resource.resource_service import ResourceService
from service.resource import (
    user_resource,
    ats_resource,
)

ResourceService.add_resouce("smp", "kv", user_resource.KVResource)
ResourceService.add_resouce("smp", "user", user_resource.UserResource)
ResourceService.add_resouce("smp", "dept", user_resource.DeptResource)
ResourceService.add_resouce("smp", "system", user_resource.SystemResource)
ResourceService.add_resouce("smp", "user_role",
                            user_resource.UserRoleResource)
ResourceService.add_resouce("smp", "role",
                            user_resource.RoleResource)
ResourceService.add_resouce("smp", "role_resource",
                            user_resource.RoleResourceResource)
ResourceService.add_resouce("smp", "resource",
                            user_resource.ResourceResource)
ResourceService.add_resouce("smp", "ats_channel",
                            ats_resource.AtsChannelResource)
ResourceService.add_resouce("smp", "ats_job",
                            ats_resource.AtsJobResource)
ResourceService.add_resouce("smp", "ats_interview",
                            ats_resource.AtsInterviewResource)

URL_ROUTES = [
    (r"/smp/resource/(\w+)/(\w+)/(\w+)", resource.ResourcePKHandler),
    (r"/smp/resource/(\w+)/(\w+)", resource.ResourceHandler),
]
