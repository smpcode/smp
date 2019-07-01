#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
es_logger
~~~~~~~~~~~~

please add description for this module

:copyright: (c) 2016 smpcode
:authors: Qilei
:version: 1.0 of 2017-06-11

"""
import json
import logging as log


def write(json_message=None, **kargs):
    """写json格式日志到文件
    """
    log_dict = kargs
    if json_message:
        log_dict = json.loads(json_message)
        log_dict.update(kargs)

    log_data = json.dumps(log_dict)
    logger = log.getLogger('hrsystem_es')
    logger.info(log_data)
