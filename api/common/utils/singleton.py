# -*- coding: utf-8 -*-
"""
Copyright (c) 2016,掌阅科技
All rights reserved.

摘    要: 线程安全单例类
创 建 者: WangLichao
创建日期: 2016-03-15
"""
import threading


class SingletonMixin(object):
    """Based on tornado.ioloop.IOLoop.instance() approach.
    参考：https://github.com/facebook/tornado
    """
    __singleton_lock = threading.Lock()
    __singleton_instance = None

    @classmethod
    def instance(cls):
        """return instance
        """
        if not cls.__singleton_instance:
            with cls.__singleton_lock:
                if not cls.__singleton_instance:
                    cls.__singleton_instance = cls()
        return cls.__singleton_instance
