# -*- coding: utf-8 -*-

"""
resource base
~~~~~~~~~~~~

资源相关api接口

:copyright: (c) 2017 smpcode
:authors: smpcode
:version: 1.0 of 2017-04-21

"""
import logging

from common.helpers.tornado_helpers import BaseHandler
from service.resource.resource_service import ResourceService


class ResourceBaseHandler(BaseHandler):

    """ account基础类封装
    """
    SUPPORTED_METHODS = ("GET", "POST", "OPTIONS", "PUT", "DELETE")
    SUPPORT_CORS = True
    SUPPORT_JWT = True
    SUPPORT_SESSION = True
    logger = logging.getLogger("smp")

    def before_request(self):
        """请求前钩子
        """
        self.logger.info("user=%s", self.current_user)

    @property
    def resource_service(self):
        """资源统一接口
        """
        return ResourceService(self)

    def check_xsrf_cookie(self):
        """重写check_xsrf_cookie,首个页面不进行检查
        """
        pass
