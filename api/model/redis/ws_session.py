# -*- coding: utf-8 -*-

"""
websocket session
~~~~~~~~~~~~

websocket会话管理

:copyright: (c) 2019 smpcode
:authors: smp
:version: 1.0 of 2019-03-29

"""
import logging as log
from common.errors import RedisKeyError
from model.redis.base import BaseModel


class WebSocketSessionModel(BaseModel):
    """ websocket session信息
    """
    prefix = ''
    session_key = "websocket_console_sessions"

    def set(self, session_data):
        """设置session信息
        """
        s_key = self.key[self.session_key]
        if isinstance(s_key, bytes):
            s_key = s_key.decode("utf8")
        self.db.set(s_key, session_data)

    def get(self):
        """获取session信息
        """
        s_key = self.key[self.session_key]
        if isinstance(s_key, bytes):
            s_key = s_key.decode("utf8")
        return self.db.get(s_key)
