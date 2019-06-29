# -*- coding: utf-8 -*-

"""
__init__
~~~~~~~~~~~~

:copyright: (c) 2016 smpcode
:authors: smpcode
:version: 1.0 of 2016-07-14

"""
import sys
import socket
import fcntl
import struct
import logging

PY2 = sys.version_info[0] == 2
__LOCAL_IP = None


def class_path(cls):
    """获取类路径"""
    if isinstance(cls, type):
        name = cls.__name__
    else:
        name = cls.__class__.__name__
    return '.'.join([cls.__module__, name])


def get_host_by_network():
    """获取本机IP
    """
    return [
        (s.connect(('10.100.20.32', 53)),
         s.getsockname()[0],
         s.close()) for s in [socket.socket(
             socket.AF_INET,
             socket.SOCK_DGRAM
         )]
    ][0][1]


def get_host(ifname=None):
    """获取服务器IP地址
    """
    global __LOCAL_IP
    # 使用全局变量对本机IP进行缓存
    if __LOCAL_IP:
        return __LOCAL_IP
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    retry_ifnames = ["bond0", "team0", "eth0"]  # 最常用的三种网卡命名方式
    if ifname and ifname not in retry_ifnames:
        retry_ifnames.insert(0, ifname)
    local_ip = None
    max_retry_times = len(retry_ifnames)
    for retry_time, ifname_ in enumerate(retry_ifnames, 1):
        try:
            if PY2:
                local_ip = socket.inet_ntoa(fcntl.ioctl(
                    sock.fileno(),
                    0x8915,  # SIOCGIFADDR
                    struct.pack('256s', ifname_[:15])
                )[20:24])
            else:
                local_ip = socket.inet_ntoa(fcntl.ioctl(
                    sock.fileno(),
                    0x8915,  # SIOCGIFADDR
                    struct.pack('256s', bytes(ifname_[:15], "utf-8"))
                )[20:24])
            break
        except IOError as err:
            if retry_time == max_retry_times:
                logging.error("get_ip_addr failed, error=%s", err)
    if not local_ip:
        local_ip = get_host_by_network()
    __LOCAL_IP = local_ip
    return local_ip


def load_class(s):
    '''获取文件模块中的类对象
    '''
    path, klass = s.rsplit('.', 1)
    __import__(path)
    mod = sys.modules[path]
    return getattr(mod, klass)

def get_value_type(value):
    """ get type
    """
    data_type = ""
    if not value:
        return data_type
    if isinstance(value, int):
        data_type = "int"
    elif isinstance(value, float):
        data_type = "float"
    else:
        data_type = "string"
    return data_type
