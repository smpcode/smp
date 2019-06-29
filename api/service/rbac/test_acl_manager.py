# -*- coding: utf-8 -*-

"""
test_acl_manager
~~~~~~~~~~~~

test acl_manager

:copyright: (c) 2017 smpcode
:authors: smpcode
:version: 1.0 of 2017-05-27

"""
from service.rbac.acl_manager import ACLManager


class Role:
    """Mock role
    """

    def __init__(self, id_):
        self.id = id_


class Resource:
    """mock resource
    """

    def __init__(self, id_):
        self.id = id_


def test_acl_manager():
    """测试acl
    """

    acl_manager = ACLManager()
    roles = {Role("admin"), Role("ns"), Role("config")}
    resources = {Resource("page1"), Resource("page2"), Resource("page3")}
    operations = {"index", "create", "update", "delete", "download", "upload"}
    acl_manager.add_roles(roles)
    acl_manager.add_resources(resources)
    # page1
    acl_manager.allow("admin", "index", "page1")
    acl_manager.allow("admin", "delete", "page1")
    # page2
    acl_manager.allow("admin", "index", "page2")
    acl_manager.allow("admin", "update", "page2")
    # page5 does not exist
    acl_manager.allow("admin", "index", "page5")
    # testrole does not exist
    acl_manager.allow("testrole", "index", "page1")

    assert acl_manager.is_allowed("admin", "delete", "page1") is True
    assert acl_manager.is_allowed("admin", "index", "page1") is True
    assert acl_manager.is_allowed("admin", "upload", "page1") is False
    assert acl_manager.is_allowed("admin", "update", "page1") is False
    assert acl_manager.is_allowed("admin", "delete", "page2") is False
    assert acl_manager.is_allowed("admin", "index", "page2") is True
    assert acl_manager.is_allowed("admin", "index", "page3") is False
    assert acl_manager.is_allowed("test", "index", "page3") is False
    assert acl_manager.is_allowed("testrole", "index", "page1") is False
    assert acl_manager.is_allowed("admin", "index", "page5") is False
    print(acl_manager)
