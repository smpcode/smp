# -*- coding: utf-8 -*-

"""
tornado_cors
~~~~~~~~~~~~

解决tornado跨域请求问题

:copyright: (c) 2017 smpcode
:authors: smpcode
:version: 1.0 of 2017-05-16

"""
import inspect

from tornado.web import RequestHandler
from tornado.web import asynchronous


def _get_class_that_defined_method(meth):
    for cls in inspect.getmro(meth.__self__.__class__):
        if meth.__name__ in cls.__dict__:
            return cls
    return None


class CorsMixin:

    CORS_ORIGIN = None
    CORS_HEADERS = None
    CORS_METHODS = None
    CORS_CREDENTIALS = None
    CORS_MAX_AGE = 86400
    CORS_EXPOSE_HEADERS = None

    def set_default_headers(self):
        """设置默认头
        """
        if self.CORS_ORIGIN:
            self.set_header("Access-Control-Allow-Origin", self.CORS_ORIGIN)

        if self.CORS_EXPOSE_HEADERS:
            self.set_header('Access-Control-Expose-Headers',
                            self.CORS_EXPOSE_HEADERS)

    @asynchronous
    def options(self, *args, **kwargs):
        """写入跨域请求header
        """
        if self.CORS_HEADERS:
            self.set_header('Access-Control-Allow-Headers', self.CORS_HEADERS)
        if self.CORS_METHODS:
            self.set_header('Access-Control-Allow-Methods', self.CORS_METHODS)
        else:
            self.set_header('Access-Control-Allow-Methods',
                            self._get_methods())
        if self.CORS_CREDENTIALS != None:
            self.set_header('Access-Control-Allow-Credentials',
                            "true" if self.CORS_CREDENTIALS else "false")
        if self.CORS_MAX_AGE:
            self.set_header('Access-Control-Max-Age', self.CORS_MAX_AGE)

        if self.CORS_EXPOSE_HEADERS:
            self.set_header('Access-Control-Expose-Headers',
                            self.CORS_EXPOSE_HEADERS)

        self.set_status(204)
        self.finish()

    def _get_methods(self):
        """设置支持的跨域方法
        """
        supported_methods = [method.lower()
                             for method in self.SUPPORTED_METHODS]
        #  ['get', 'put', 'post', 'patch', 'delete', 'options']
        methods = []
        for meth in supported_methods:
            instance_meth = getattr(self, meth)
            if not meth:
                continue
            handler_class = _get_class_that_defined_method(instance_meth)
            if not handler_class is RequestHandler:
                methods.append(meth.upper())

        return ", ".join(methods)
