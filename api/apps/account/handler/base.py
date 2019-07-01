# -*- coding: utf-8 -*-

"""
account base
~~~~~~~~~~~~

账户相关api接口

:copyright: (c) 2019 smpcode
:authors: smpcode
:version: 1.0 of 2019-04-21

"""
import logging
from common import errors
from common.helpers.tornado_helpers import BaseHandler
from service.account.account_service import AccountService
from service.account.dept_service import DeptService
from service.account.kv_service import KVService
from service.rbac.rbac_service import RBACService


class AccountBaseHandler(BaseHandler):

    """ account基础类封装
    """
    SUPPORTED_METHODS = ("GET", "POST", "OPTIONS", "PUT", "DELETE")
    SUPPORT_CORS = True
    SUPPORT_SESSION = True
    logger = logging.getLogger("smp")

    def before_request(self):
        """请求前钩子
        """
        self.logger.info("user=%s", self.current_user)

    @property
    def account_service(self):
        """账户服务
        """
        return AccountService(self.get_db("smp"))

    @property
    def dept_service(self):
        """部门服务
        """
        return DeptService(self.get_db("smp"))

    @property
    def rbac_service(self):
        """权限服务
        """
        return RBACService(self.get_db("smp"), self.sys_id)

    @property
    def kv_service(self):
        """数据字典服务
        """
        return KVService(self.get_db("smp"))

    def get_db(self, db_name):
        """获取db
        """
        return self.settings["service_manager"].database[db_name]
