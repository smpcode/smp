# -*- coding: utf-8 -*-

"""
errors
~~~~~~~~~~~~

所有的内部异常在此处定义

:copyright: (c) 2016 smpcode
:authors: smpcode
:version: 1.0 of 2016-07-18

"""


class SMPAPIError(Exception):

    """总的基础异常类型
    """
    pass


class RedisKeyError(SMPAPIError):

    """redis key异常
    """
    pass


class DatabaseError(SMPAPIError):

    """数据库类异常信息封装
    """
    pass


class ConfigError(SMPAPIError):

    """配置错误
    """
    pass


class InvalidSessionError(SMPAPIError):

    """无效session
    """
    pass


class ClientError(SMPAPIError):
    """
    :param code: http status
    :param message: http status infomation
    """
    code = None
    message = None


class BadRequestError(ClientError):
    """The error when client made the request incorrectly
    """
    code = 400
    message = "Bad Request"


class ValidateError(ClientError):
    """validate error
    """
    code = 401
    message = "Validate Error"


class ForbiddenError(ClientError):
    """forbidden error
    """
    code = 403
    message = "Forbidden Error"


class AccessDeniedError(ForbiddenError):
    """access denied error"""
    message = 'access denied'


class NotFoundError(ClientError):
    """validate error
    """
    code = 404
    message = "Not Found"


class MethodNotAllowedError(ClientError):
    """Error when the request method is not implemented for the URL
    """
    code = 405
    message = "Method not allowed"


class ServerError(SMPAPIError):
    """Error occurs in server side
    server端服务报错一律code一律为500
    """
    message = None


class ServerConfigError(SMPAPIError):
    """Error occurs in server when server side config is wrong
    """
    message = "server config error"
