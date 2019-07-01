# -*- coding: utf-8 -*-

"""
tornado_helpers
~~~~~~~~~~~~

封装与tornado框架相关的函数

:copyright: (c) 2016 smpcode
:authors: smpcode
:version: 1.0 of 2016-07-15

"""
import re
import datetime
import logging
import functools
from enum import IntEnum

import ujson as json
from tornado.web import RequestHandler
from tornado import escape

from common.errors import ClientError, ServerError, ForbiddenError, AccessDeniedError
from common.session import session
from common.db.database import Database
from common.utils import class_path
import common.helpers.es_logger as eslogger


class ResponseStatus(IntEnum):
    """常用非错误时不同响应状态表示含义

    400以下的状态码统一由该枚举设置
    400以上的异常统一使用raise来抛出，表示客户端导致失败
    500以上的异常由于程序内部意外导致，需要针对性处理
    """
    success = 200  # 操作成功
    created = 201  # 创建成功响应码
    accepted = 202  # 请求被接收成功
    deleted = 204  # 删除成功响应码
    move_permanently = 301  # 永久重定向
    move_temporarily = 302  # 临时重定向
    not_modified = 304  # 资源未修改
    forbidden = 403  # 权限问题
    interval_server_error = 500
    bad_gateway = 502


def authenticated(method):
    """重写tornado的authenticated避免redirect方式对前后端分离模式的侵入性

    修改点：移除对请求方法的校验，和redirect逻辑
    参考：tornado.web.authenticated
    """
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        """直接获取当前用户如果失败即异常
        """
        if not self.current_user:
            raise ForbiddenError()
        return method(self, *args, **kwargs)
    return wrapper


class BaseHandler(RequestHandler):
    """zkapi项目接口基类
    """
    SUPPORTED_METHODS = ("GET", "POST", "POST", "PUT", "DELETE")
    BUILTIN_TYPES = (str, int, float, datetime.datetime)
    ACCESS_CONTROL_ALLOW_HEADERS = "Origin,Content-Type,X-Requested-With,X-Xsrftoken,X-Real-IP,X-System-ID,Accept,Authorization"
    ACCESS_CONTRON_ALLOW_METHODS = "post, POST, get, GET, options, OPTIONS, put, PUT, delete, DELETE"
    SUPPORT_CORS = False  # 是否支持跨域
    SUPPORT_SESSION = True  # 是否支持session

    config = {}
    debug = False
    session = None

    def initialize(self):
        """初始化相关属性
        """
        self.config = self.settings.get("config", {})
        if "error_key" not in self.config:
            self.config["error_key"] = "error"
        if "plain_result_key" not in self.config:
            self.config["plain_result_key"] = "result"

        self.debug = self.settings.get("debug")
        # 重新实例化session对象
        if self.SUPPORT_SESSION:
            self.session = session.Session(
                self.application.session_manager, self)
        if hasattr(self, "before_request"):
            self.before_request()

        # 初始化审计service
        if hasattr(self, "service_manager"):
            self.service_manager.init()

    def has_argument(self, argument):
        """判断请求参数是否包含某个参数

        :rtype: bool
        """
        return argument in self.request.arguments

    def make_response(self, response, response_status=ResponseStatus.success):
        """解析响应结果，返回指定类型

        :param response: 返回结果对象
        """
        if response is None:
            result = {
                self.config['plain_result_key']: ""
            }
        elif isinstance(response, (dict, list, tuple, set)):
            result = response
        elif isinstance(response, self.BUILTIN_TYPES):
            result = {
                self.config['plain_result_key']: response
            }
        else:
            raise ServerError(
                "Could not serialize '{}' to JSON".format(
                    type(response).__name__
                )
            )
        status_code = int(response_status)
        self.set_status(status_code)


        # 写json格式的日志供logstash解析
        eslogger.write(status=status_code,
                       request_uri=self.request.uri,
                       remote_ip=self.request.remote_ip,
                       request_args=str(self.request.arguments),
                       user=(self.current_user['account'] if self.current_user else ''))

        if status_code in (204, 304):
            return self.finish()
        self._write_dict(result)

    def _write_dict(self, response_dict):
        """响应json格式的数据
        """
        self.set_header('Content-Type', 'application/json')
        result = json.dumps(response_dict)
        self.write(result)
        self.finish()

    def write_error(self, _, exc_info=None, **kwargs):
        """The top function for writing errors"""
        if exc_info:
            exc_type, exc_inst, _ = exc_info
            if issubclass(exc_type, ClientError):
                self._write_client_error(exc_inst)
                return
            # 兼容参数解析模块错误处理逻辑
            if hasattr(exc_inst, 'messages'):
                exc_inst.code = 400
                exc_inst.message = exc_inst.messages
                self._write_client_error(exc_inst)
                return
            if issubclass(exc_type, ServerError):
                self._write_server_error(exc_inst)
                return
        self._write_server_error()

    def _write_client_error(self, exc):
        """Formats and returns a client error to the client"""
        error_msg = "{}: {}".format(exc.message, str(exc))
        result = {
            self.config['error_key']: error_msg
        }
        logging.error(
            "client error code=%s, messages=%s",
            exc.code,
            exc.message)


        self.set_status(exc.code)
        self.write(json.dumps(result))
        self.finish()

    def _write_server_error(self, exc=None):
        """Formats and returns a server error to the client"""
        if exc:
            error_msg = "{}: {}".format(exc.message, str(exc))
        else:
            error_msg = "Internal Error"
        result = {
            self.config['error_key']: error_msg
        }
        logging.error(
            "internal error code=500, messages=%s, request_uri=%s, remote_ip=%s, request_args=%s, user=%s",
            error_msg,
            self.request.uri,
            self.request.remote_ip,
            str(self.request.arguments),
            self.current_user['account'] if self.current_user else '')

        self.set_status(500)
        self.write(json.dumps(result))
        # 如果异常进行重新初始化服务
        if hasattr(self, "service_manager"):
            self.service_manager.init()
        self.finish()

    def get_xsrf(self):
        '''获取签名值
        '''
        return escape.xhtml_escape(self.xsrf_token)

    def data_received(self, chunk):
        """Implement this method to handle streamed request data.

        Requires the `.stream_request_body` decorator.
        """
        pass

    def set_default_headers(self):
        """ 用于支持跨域请求
        """
        if self.SUPPORT_CORS:
            self.set_header('Access-Control-Allow-Credentials',
                            'true')  # 允许写入cookie
            self.set_header('Access-Control-Request-Headers', '*')
            allow_origin = self.settings.get("allow_origin")
            if allow_origin:
                self.set_header("Access-Control-Allow-Origin",
                                allow_origin)
            self.set_header("Access-Control-Allow-Headers",
                            self.ACCESS_CONTROL_ALLOW_HEADERS)
            self.set_header('Access-Control-Allow-Methods',
                            self.ACCESS_CONTRON_ALLOW_METHODS)

    def options(self, *args, **kwargs):
        """跨域支持
        """
        if self.SUPPORT_CORS:
            self.set_status(204)
            self.finish()

    def get_current_user(self):
        """获取用户信息
        """
        # 从session中获取，如果获取失败则表示未登陆过
        if self.SUPPORT_SESSION:
            user_info = self.session.get("user_info")
            Database.current_user = user_info
            return user_info

    @property
    def remote_ip(self):
        """通过属性获取用户IP
        """
        return self.get_remote_ip()

    def get_remote_ip(self):
        """获取请求的实际IP地址
        """
        remote_ip = self.request.headers.get("X-Real-Ip", '')
        if not remote_ip:
            remote_ip = self.request.remote_ip
        return remote_ip

    @property
    def sys_id(self):
        """通过属性获取系统ID
        """
        return self.get_system_id()

    def get_system_id(self):
        """获取系统ID
        """
        try:
            sys_id = int(self.request.headers.get("X-System-ID", 0))
            if not sys_id:
                sys_id = int(self.get_argument("sys_id", 1))
        except ValueError:
            return 1
        return sys_id

    def check_xsrf_cookie(self):
        """重写父类的xsrf校验逻辑，增加对debug环境的支持
        """
        if self.debug:
            return
        if self.SUPPORT_SESSION:
            super(BaseHandler, self).check_xsrf_cookie()
