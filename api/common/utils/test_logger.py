# -*- coding: utf-8 -*-
"""
test_logger
~~~~~~~~~~~~

logger模块的单元测试,主要是可用性测试,无特殊性验证

:copyright: (c) 2016 smpcode
:authors: smpcode
:version: 1.0 of 2016-07-14

"""
# pylint: disable=all
import pytest
import logging
from common.utils.logger import init_logger


DEFAULT_LOGGING_CONFIG = {
    'loggers': {
        'zkapi': {
            'level': 'INFO',
            'propagate': False,
            'handlers': [
                'console',
                'info_file_handler',
                'error_file_handler',
            ]
        }
    },
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'error_file_handler': {
            'formatter': 'zkapi',
            'backupCount': 20,
            'level': 'ERROR',
            'encoding': 'utf8',
            'class': 'logging.handlers.RotatingFileHandler',
            'maxBytes': 104857600,
            'filename': '/data/logs/zkapi/zkapi.errors.log'
        },
        'console': {
            'formatter': 'zkapi',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',
            'level': 'INFO'
        },
        'info_file_handler': {
            'formatter': 'zkapi',
            'backupCount': 20,
            'level': 'INFO',
            'encoding': 'utf8',
            'class': 'logging.handlers.RotatingFileHandler',
            'maxBytes': 104857600,
            'filename': '/data/logs/zkapi/zkapi.info.log'
        }
    },
    'root': {
        'level': 'DEBUG',
        'handlers': [
            'info_file_handler',
            'error_file_handler']
    },
    'formatters': {
        'zkapi': {
            'format': '[%(levelname)1.1s %(asctime)s %(module)s:%(lineno)d] %(message)s'
        }
    }
}


def test_logger():
    """检查日志的设置模块的可用性
    """
    init_logger(DEFAULT_LOGGING_CONFIG, suffix="test", debug=True)
    logging.info("I am a info")
    logging.error("I am a error")
    logging.warning("I am a warning")

if __name__ == "__main__":
    test_logger()
