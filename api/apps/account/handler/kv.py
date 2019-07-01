# -*- coding: utf-8 -*-

"""
kv接口
~~~~~~~~~~~~

数据字典表

:copyright: (c) 2016 smpcode
:authors: smpcode
:version: 1.0 of 2019-06-23

"""
# pylint: disable=arguments-differ
import ujson as json
from webargs import fields
from webargs.tornadoparser import use_args

from common import errors
from common.helpers.tornado_helpers import authenticated
from common.helpers.tornado_helpers import ResponseStatus
from apps.account.handler.base import AccountBaseHandler


class KVHandler(AccountBaseHandler):

    """ 数据字典相关api
    """

    SUPPORTED_METHODS = ("GET", "POST", "OPTIONS")

    @use_args({
        "key": fields.Str(required=True),  # 要修改的字典的标示名称
        "value": fields.Str(required=True),  # 要修改的字典数据列表，json.dumps后的数据
        "desc": fields.Str(required=False),  # 描述
    })
    @authenticated
    def post(self, reqargs):
        """ 更新字典表
        """
        key = reqargs["key"]
        try:
            value = json.loads(reqargs["value"])
        except ValueError as error:
            self.logger("parse param error=%s", error)
            raise errors.ValidateError()
        desc = reqargs['desc']
        self.kv_service.set(key, value, desc)
        self.make_response("Created", ResponseStatus.created)

    @use_args({
        "key": fields.Str(required=True),  # 要修改的字典的标示名称
    })
    @authenticated
    def get(self, reqargs):
        """获取字典数据
        """
        key = reqargs["key"]
        value = self.kv_service.get(key)
        self.make_response(value)

    @use_args({
        "key": fields.Str(required=True),  # 要修改的字典的标示名称
    })
    @authenticated
    def delete(self, reqargs):
        """删除指定key
        """
        key = reqargs["key"]
        self.kv_service.delete(key)
        self.make_response("Deleted", ResponseStatus.deleted)
