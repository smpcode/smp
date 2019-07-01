# -*- coding: utf-8 -*-

"""
session
~~~~~~~~~~~~

会话管理

:copyright: (c) 2017 smpcode
:authors: smpcode
:version: 1.0 of 2017-04-24

"""
import logging as log
import hmac
import uuid
import hashlib

import ujson as json

from tornado import escape

from common.errors import InvalidSessionError
from model.redis.session import SessionModel


class SessionData(dict):
    '''session数据
    '''

    def __init__(self, session_id, hmac_key):
        self.session_id = session_id
        self.hmac_key = hmac_key


class Session(SessionData):
    '''session
    '''

    def __init__(self, session_manager, request_handler):
        self.session_manager = session_manager
        self.request_handler = request_handler

        try:
            current_session = session_manager.get(request_handler)
        except InvalidSessionError:
            current_session = session_manager.get()

        for key, data in current_session.items():
            self[key] = data
        self.session_id = current_session.session_id
        self.hmac_key = current_session.hmac_key

    def save(self, timeout=None):
        '''保存会话
        '''
        self.session_manager.set(self.request_handler, self, timeout)


class SessionManager:
    '''session管理
    '''
    SM = SessionModel()

    def __init__(self, secret, session_timeout):
        self.secret = secret
        self.session_timeout = session_timeout

    def _fetch(self, session_id):
        '''根据session_id获取session
        '''
        try:
            session_data = raw_data = self.SM.get(session_id)
            if not raw_data:
                return {}
            log.debug("raw_data=%s", raw_data)
            session_data = json.loads(raw_data)
            if isinstance(session_data, dict):
                log.debug("session_data=%s", session_data)
                return session_data
            log.debug("session_data format error=%s", session_data)
            return {}
        except IOError as error:
            log.error("exec _fetch session failed, session_id=%s, error=%s", session_id, error)
            return {}

    def get(self, request_handler=None):
        '''获取session
        '''

        if request_handler is None:
            session_id = None
            hmac_key = None
        else:
            session_id = request_handler.get_secure_cookie("session_id")
            hmac_key = request_handler.get_secure_cookie("verification")

            log.debug(
                "get session_id=%s, hmac_key=%s from request_handler", session_id, hmac_key)

        if session_id is None:
            session_exists = False
            session_id = self._generate_id()
            hmac_key = self._generate_hmac(session_id)
        else:
            session_exists = True

        check_hmac = self._generate_hmac(session_id)
        if isinstance(hmac_key, bytes):
            hmac_key = hmac_key.decode("utf8")
        if hmac_key != check_hmac:
            raise InvalidSessionError(
                "check session error for hmac_key != check_hmac, hmac_key=%s, check_hmac=%s",
                hmac_key,
                check_hmac)

        if isinstance(session_id, bytes):
            session_id = session_id.decode("utf8")
        session = SessionData(session_id, hmac_key)

        if session_exists:
            session_data = self._fetch(session_id)
            for key, data in session_data.items():
                session[key] = data

        log.debug("get session = %s", session)
        return session

    def set(self, request_handler, session, timeout=None):
        '''添加session
        '''
        if timeout is None:
            timeout = self.session_timeout
        request_handler.set_secure_cookie("session_id", session.session_id)
        request_handler.set_secure_cookie("verification", session.hmac_key)
        # 调用xsrf_token即可写入xsrf cookie
        request_handler.xsrf_token
        session_data = json.dumps(dict(session.items()))
        # redis存储session
        self.SM.set(session.session_id, session_data, timeout)
        log.info("exec set_secure_cookie, session timeout=%s, session_id=%s, session_data=%s",
                 timeout, session.session_id, session_data)

    def get_session_by_id(self, session_id):
        '''g根据sessionid获取session信息
        '''
        return self._fetch(session_id)

    def release(self, session):
        '''清除session
        '''
        # redis存储session
        return self.SM.delete(session.session_id)

    def _generate_id(self):
        '''产生会话id
        '''
        new_id = hashlib.sha256(
            (self.secret + str(uuid.uuid4())).encode("utf8"))
        log.debug("exec _generate_id, id=%s", new_id.hexdigest())
        return new_id.hexdigest()

    def _generate_hmac(self, session_id):
        '''生成hamc地址
        '''
        if isinstance(session_id, str):
            session_id = session_id.encode("utf-8")
        if isinstance(self.secret, str):
            secret = self.secret.encode("utf-8")
        return hmac.new(session_id, secret, hashlib.sha256).hexdigest()
