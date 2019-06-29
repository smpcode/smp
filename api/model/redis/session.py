# -*- coding: utf-8 -*-

"""
session
~~~~~~~~~~~~

会话管理

:copyright: (c) 2019 smpcode
:authors: smpcode
:version: 1.0 of 2019-04-24

"""
import logging as log
from common.errors import RedisKeyError
from model.redis.base import BaseModel


class SessionModel(BaseModel):
    """session信息
    """
    prefix = 'session'

    def set(self, session_id, session_data, timeout):
        """设置session信息
        """
        if not session_id:
            raise RedisKeyError("construct session_key required session_id")
        session_key = self.key[session_id]
        if isinstance(session_key, bytes):
            session_key = session_key.decode("utf8")
        self.db.api.set(session_key, session_data)
        self.db.api.expire(session_key, timeout)

    def get(self, session_id):
        """获取session信息
        """
        if not session_id:
            raise RedisKeyError("construct session_key required session_id")
        session_key = self.key[session_id]
        if isinstance(session_key, bytes):
            session_key = session_key.decode("utf8")
        return self.db.api.get(session_key)

    def delete(self, session_id):
        """删除session信息
        """
        if not session_id:
            raise RedisKeyError("construct session_key required session_id")
        session_key = self.key[session_id]
        if isinstance(session_key, bytes):
            session_key = session_key.decode("utf8")
        try:
            self.db.api.delete(session_key)
        except KeyError as err:
            log.error("redis delete error=%s, redis key: %s",
                      err, session_key)
            return False
        return True
