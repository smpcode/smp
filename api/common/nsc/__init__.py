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

    def get_master_service(self, namespace):
        """获取主服务
        """
        services = self.get_services(namespace)
        for service in services:
            if service.get("role") == "master":
                return service
        return {}

    def get_slave_service(self, namespace):
        """获取从服务
        """
        slaves = []
        services = self.get_services(namespace)
        for service in services:
            if service.get('role') == 'slave':
                slaves.append(service)
        return slaves

    def get_services(self, namespace):
        """获取服务列表
        """
        return self.config.get(namespace, [])
