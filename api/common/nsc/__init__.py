# -*- coding: utf-8 -*-

"""
nsc
~~~~~~~~~~~~

:copyright: (c) 2018 smpcode
:authors: smpcode
:version: 1.0 of 2019-05-29

"""

class NSC(object):

    """模拟服务发现客户端针对名字空间进行动态解析逻辑
    """

    def __init__(self, config):
        """init
        """
        self.config = config

    def get_main_service(self, namespace):
        """获取主服务
        """
        services = self.get_services(namespace)
        for service in services:
            if service.get("role") == "main":
                return service
        return {}

    def get_subordinate_service(self, namespace):
        """获取从服务
        """
        subordinates = []
        services = self.get_services(namespace)
        for service in services:
            if service.get('role') == 'subordinate':
                subordinates.append(service)
        return subordinates

    def get_services(self, namespace):
        """获取服务列表
        """
        return self.config.get(namespace, [])
