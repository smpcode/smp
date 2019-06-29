# -*- coding: utf-8 -*-

"""
ensure
~~~~~~~~~~~~

确保返回的类型为所需类型

:copyright: (c) 2016 smpcode
:authors: smpcode
:version: 1.0 of 2017-06-23

"""
# pylint: disable=no-else-return

import sys

PY3 = sys.version_info.major > 2


def ensure_bytes(s):
    """确保返回类型为bytes类型"""

    if PY3 and isinstance(s, bytes):
        return s
    if not PY3 and isinstance(s, str):
        return s
    if hasattr(s, 'encode'):
        return s.encode()
    if hasattr(s, 'tobytes'):
        return s.tobytes()
    if isinstance(s, bytearray):
        return bytes(s)
    if not PY3 and hasattr(s, 'tostring'):
        return s.tostring()
    if isinstance(s, dict):
        return {k: ensure_bytes(v) for k, v in s.items()}
    else:
        # Perhaps it works anyway - could raise here
        return s


def ensure_string(s):
    """ 确保返回的为string类型

    >>> ensure_string(b'123')
    '123'
    >>> ensure_string('123')
    '123'
    >>> ensure_string({'x': b'123'})
    {'x': '123'}
    """
    if isinstance(s, dict):
        return {k: ensure_string(v) for k, v in s.items()}
    if hasattr(s, 'decode'):
        return s.decode()
    else:
        return s


def ensure_string_new(s):
    """ 确保返回的为string类型

    >>> ensure_string(b'123')
    '123'
    >>> ensure_string('123')
    '123'
    >>> ensure_string({'x': b'123'})
    {'x': '123'}
    """
    if isinstance(s, dict):
        return {k: ensure_string_new(v) for k, v in s.items()}
    if isinstance(s, list):
        return [ensure_string(item) for item in s]
    if hasattr(s, 'decode'):
        return s.decode()
    else:
        return s


def ensure_trailing_slash(s, ensure=True):
    """ 确保以/结尾

    >>> ensure_trailing_slash('/user/directory')
    '/user/directory/'
    >>> ensure_trailing_slash('/user/directory/')
    '/user/directory/'
    >>> ensure_trailing_slash('/user/directory/', False)
    '/user/directory'
    """
    slash = '/' if isinstance(s, str) else b'/'
    if ensure and not s.endswith(slash):
        s += slash
    if not ensure and s.endswith(slash):
        s = s[:-1]
    return s


def ensure_path_format(path, ensure=False):
    """确保返回的是文件/目录路径的格式，即/xx/xx/xx，或者/xx/xx/xx/
    :param path: 路径
    :param ensure:是文件路径还是目录路径
    """
    slash = '/' if isinstance(path, str) else b'/'
    if not path.startswith(slash):
        path = slash + path
    if ensure and not path.endswith(slash):
        path += slash
    if not ensure and path.endswith(slash):
        path = path[:-1]
    return path
