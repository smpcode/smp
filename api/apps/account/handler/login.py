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
from common.helpers.tornado_helpers import ResponseStatus


class AccountLoginHandler(AccountBaseHandler):

    """ 账户登陆逻辑
    """

    SUPPORTED_METHODS = ("POST", "OPTIONS")
    CODE_MESSAGE = {
        1001: "用户名不存在",
        1002: "用户名密码不匹配,登录失败",
        1003: "密码已过期,请修改密码",
    }

    @use_args({
        "account": fields.Str(required=True),  # 账户
        "password": fields.Str(required=True),  # 密码
    })
    def post(self, reqargs):
        """登录逻辑
        """
        account = reqargs["account"]
        password = reqargs["password"]
        remote_ip = self.get_remote_ip()

        user_info, is_ok, code = self.account_service.login(account, password,
                                                            remote_ip)
        self.logger.debug("login user=%s, login flag=%s", user_info, is_ok)
        if is_ok and code == 0:
            # 保存session
            roles = self.account_service.get_roles(account)
            routes = self.rbac_service.get_account_routes(account)
            self.session["user_info"] = user_info
            self.session["user_info"]["roles"] = roles
            self.session["user_info"]["routes"] = routes
            self.session.save()
            self.make_response(user_info)
        else:
            login_res = {
                "code": code,
                "message": self.CODE_MESSAGE[code],
            }
            self.make_response(login_res,
                               ResponseStatus.forbidden)

    def check_xsrf_cookie(self):
        """重写check_xsrf_cookie,首个页面不进行检查
        """
        pass
