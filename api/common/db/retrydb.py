# -*- coding: utf-8 -*-

"""
retrydb
~~~~~~~~~~~~

refer: http://docs.peewee-orm.com/en/latest/peewee/database.html#advanced-connection-management

:copyright: (c) 2017 smpcode
:authors: smpcode
:version: 1.0 of 2017-04-28

"""
# pylint: disable=abstract-method
from playhouse.shortcuts import RetryOperationalError
from peewee import MySQLDatabase


class RetryDB(RetryOperationalError, MySQLDatabase):
    """继承
    """
    pass
