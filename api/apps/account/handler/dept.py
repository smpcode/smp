# -*- coding: utf-8 -*-

"""
dept
~~~~~~~~~~~~

账户相关基础API

:copyright: (c) 2019 smpcode
:authors: smpcode
:version: 1.0 of 2019-04-21

"""
# pylint: disable=arguments-differ
from apps.account.handler.base import AccountBaseHandler


class DeptHandler(AccountBaseHandler):

    """ 部门相关api
    """

    SUPPORTED_METHODS = ("GET", "POST", "OPTIONS")
    SUPPORT_SESSION = True

    def get(self):
        """ 获取账户
        """
        self.make_response(self.dept_service.get_dept_nodes())
