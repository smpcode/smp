# -*- coding: utf-8 -*-

"""
test_get_host
~~~~~~~~~~~~

:copyright: (c) 2016 smpcode
:authors: smpcode
:version: 1.0 of 2016-09-14

"""

from common.utils import get_host


def test_get_host():
    """测试获取本机IP
    """
    local_ip = get_host()
    print(local_ip)
    assert local_ip
