# -*- coding: utf-8 -*-

"""
login
~~~~~~~~~~~~

登陆注销逻辑

:copyright: (c) 2019 smpcode
:authors: smpcode
:version: 1.0 of 2019-05-05

"""
# pylint: disable=arguments-differ
from webargs import fields
from webargs.tornadoparser import use_args
from apps.account.handler.base import AccountBaseHandler


class AccountPasswordHandler(AccountBaseHandler):

    """ 账户修改密码
    """

    SUPPORTED_METHODS = ("POST", "OPTIONS")
    RES_MESSAGE = {
        "success": {"code": 0, "msg": "密码修改成功!"},
        "pwd_same": {"code": 1001, "msg": "新密码不能与旧密码相同!"},
        "pwd_error": {"code": 1002, "msg": "原密码错误!"},
    }

    @use_args({
        "account": fields.Str(required=True),  # 账户
        "password": fields.Str(required=True),  # 密码
        "new_password": fields.Str(required=True),  # 新密码
    })
    def post(self, reqargs):
        """修改密码
        """
        account = reqargs["account"]
        password = reqargs["password"]
        new_password = reqargs["new_password"]

        is_ok, pwd_same = self.account_service.update_password(account, password,
                                                               new_password)
        if not is_ok:
            # 原密码校验失败
            self.make_response(self.RES_MESSAGE["pwd_error"])
        elif pwd_same:
            # 新密码与旧密码相同
            self.make_response(self.RES_MESSAGE["pwd_same"])
        else:
            self.make_response(self.RES_MESSAGE["success"])

    def check_xsrf_cookie(self):
        """重写check_xsrf_cookie,首个页面不进行检查
        """
        pass
