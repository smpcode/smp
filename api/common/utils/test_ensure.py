# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring

"""
test_ensure
~~~~~~~~~~~~

:copyright: (c) 2016 smpcode
:authors: smpcode
:version: 1.0 of 2017-06-23

"""
from common.utils import ensure


def test_ensure_string():
    """测试确保字符串
    """
    str_result = ensure.ensure_string(b'test')
    assert isinstance(str_result, str)
    str_result = ensure.ensure_string('test')
    assert isinstance(str_result, str)


def test_ensure_bytes():
    """测试确保bytes
    """
    bytes_result = ensure.ensure_bytes("test")
    assert isinstance(bytes_result, bytes)
    bytes_result = ensure.ensure_bytes(b"test")
    assert isinstance(bytes_result, bytes)


def test_ensure_slash():
    """测试/结尾
    """
    slash_tail = ensure.ensure_trailing_slash("/user/test/hahah")
    assert slash_tail.endswith("/")
    slash_tail_bytes = ensure.ensure_trailing_slash(b"/user/test/hahah")
    assert slash_tail_bytes.endswith(b"/")
