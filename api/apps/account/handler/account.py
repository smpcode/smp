# -*- coding: utf-8 -*-

"""
account
~~~~~~~~~~~~

账户相关基础API

:copyright: (c) 2019 smpcode
:authors: smpcode
:version: 1.0 of 2019-04-21

"""
# pylint: disable=arguments-differ
from webargs import fields
from webargs.tornadoparser import use_args

from apps.account.handler.base import AccountBaseHandler


class AccountHandler(AccountBaseHandler):

    """ 账户相关api
    """

    SUPPORTED_METHODS = ("GET", "POST", "OPTIONS")

    @use_args({
        "account": fields.Str(required=True),  # 账户名称
    })
    def get(self, reqargs):
        """ 获取账户
        """
        account = reqargs["account"]
        account_info = self.account_service.get_user(account)
        if isinstance(account_info, dict):
            account_info["routes"] = self.rbac_service.get_account_routes(account)
        self.make_response(account_info)
