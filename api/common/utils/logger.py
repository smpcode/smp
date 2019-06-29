# -*- coding: utf-8 -*-
"""
logger
~~~~~~~~~~~~

日志的配置通用规则
注意:颜色高亮部分来自tornado.log

:copyright: (c) 2016 smpcode
:authors: smpcode
:version: 1.0 of 2016-07-14

"""
# pylint: disable=missing-docstring, undefined-variable
import sys
import logging
import logging.handlers
import logging.config
import os.path

try:
    import curses
except ImportError:
    curses = None

DEFAULT_LOGGING_CONFIG = {
    'loggers': {
        'hicps': {
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
            'formatter': 'hicps',
            'backupCount': 20,
            'level': 'ERROR',
            'encoding': 'utf8',
            'class': 'logging.handlers.RotatingFileHandler',
            'maxBytes': 104857600,  # 100MB
            'filename': '/data/logs/hicps/hicps.errors.log'
        },
        'console': {
            'formatter': 'hicps',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',
            'level': 'INFO'
        },
        'info_file_handler': {
            'formatter': 'hicps',
            'backupCount': 20,
            'level': 'INFO',
            'encoding': 'utf8',
            'class': 'logging.handlers.RotatingFileHandler',
            'maxBytes': 104857600,
            'filename': '/data/logs/hicps/hicps.info.log'
        }
    },
    'root': {
        'level': 'DEBUG',
        'handlers': ['info_file_handler', 'error_file_handler']
    },
    'formatters': {
        'hicps': {
            'format':
            '[%(levelname)1.1s %(asctime)s %(module)s:%(lineno)d] %(message)s'
        }
    }
}

if not isinstance(b'', type('')):

    def u(s):
        return s

    unicode_type = str
    basestring_type = str
else:

    def u(s):
        return s.decode('unicode_escape')

    # These names don't exist in py3, so use noqa comments to disable
    # warnings in flake8.
    unicode_type = unicode  # noqa
    basestring_type = basestring  # noqa

_TO_UNICODE_TYPES = (unicode_type, type(None))


def to_unicode(value):
    """Converts a string argument to a unicode string.

    If the argument is already a unicode string or None, it is returned
    unchanged.  Otherwise it must be a byte string and is decoded as utf8.
    """
    if isinstance(value, _TO_UNICODE_TYPES):
        return value
    if not isinstance(value, bytes):
        raise TypeError(
            "Expected bytes, unicode, or None; got %r" % type(value))
    return value.decode("utf-8")


def safe_unicode(s):
    try:
        return to_unicode(s)
    except UnicodeDecodeError:
        return repr(s)


# 从tornado包中copy过来用来给控制台日志增加颜色输出
class LogFormatter(logging.Formatter):
    """Log formatter used in Tornado.

    Key features of this formatter are:

    * Color support when logging to a terminal that supports it.
    * Timestamps on every log line.
    * Robust against str/bytes encoding problems.

    This formatter is enabled automatically by
    `tornado.options.parse_command_line` (unless ``--logging=none`` is
    used).
    """
    DEFAULT_FORMAT = '%(color)s[%(levelname)1.1s %(asctime)s %(module)s:%(lineno)d]%(end_color)s %(message)s'
    DEFAULT_DATE_FORMAT = '%y%m%d %H:%M:%S'
    DEFAULT_COLORS = {
        logging.DEBUG: 4,  # Blue
        logging.INFO: 2,  # Green
        logging.WARNING: 3,  # Yellow
        logging.ERROR: 1,  # Red
    }

    def __init__(self, color=True, fmt=None, datefmt=None, colors=None):
        r"""
        :arg bool color: Enables color support.
        :arg string fmt: Log message format.
          It will be applied to the attributes dict of log records. The
          text between ``%(color)s`` and ``%(end_color)s`` will be colored
          depending on the level if color support is on.
        :arg dict colors: color mappings from logging level to terminal color
          code
        :arg string datefmt: Datetime format.
          Used for formatting ``(asctime)`` placeholder in ``prefix_fmt``.

        .. versionchanged:: 3.2

           Added ``fmt`` and ``datefmt`` arguments.
        """
        datefmt = datefmt or self.DEFAULT_DATE_FORMAT
        self.datefmt = datefmt
        colors = colors or self.DEFAULT_COLORS
        logging.Formatter.__init__(self, datefmt=datefmt)
        self._fmt = fmt or self.DEFAULT_FORMAT

        self._colors = {}
        if color and _stderr_supports_color():
            # The curses module has some str/bytes confusion in
            # python3.  Until version 3.2.3, most methods return
            # bytes, but only accept strings.  In addition, we want to
            # output these strings with the logging module, which
            # works with unicode strings.  The explicit calls to
            # unicode() below are harmless in python2 but will do the
            # right conversion in python 3.
            fg_color = (curses.tigetstr("setaf") or curses.tigetstr("setf") or
                        "")
            if (3, 0) < sys.version_info < (3, 2, 3):
                fg_color = unicode_type(fg_color, "ascii")

            for levelno, code in colors.items():
                self._colors[levelno] = unicode_type(
                    curses.tparm(fg_color, code), "ascii")
            self._normal = unicode_type(curses.tigetstr("sgr0"), "ascii")
        else:
            self._normal = ''

    def format(self, record):
        try:
            message = record.getMessage()
            # guaranteed by logging
            assert isinstance(message, basestring_type)
            # Encoding notes:  The logging module prefers to work with character
            # strings, but only enforces that log messages are instances of
            # basestring.  In python 2, non-ascii bytestrings will make
            # their way through the logging framework until they blow up with
            # an unhelpful decoding error (with this formatter it happens
            # when we attach the prefix, but there are other opportunities for
            # exceptions further along in the framework).
            #
            # If a byte string makes it this far, convert it to unicode to
            # ensure it will make it out to the logs.  Use repr() as a fallback
            # to ensure that all byte strings can be converted successfully,
            # but don't do it by default so we don't add extra quotes to ascii
            # bytestrings.  This is a bit of a hacky place to do this, but
            # it's worth it since the encoding errors that would otherwise
            # result are so useless (and tornado is fond of using utf8-encoded
            # byte strings whereever possible).
            record.message = safe_unicode(message)
        except Exception as e:  # pylint: disable=broad-except
            record.message = "Bad message (%r): %r" % (e, record.__dict__)

        record.asctime = self.formatTime(record, self.datefmt)

        if record.levelno in self._colors:
            record.color = self._colors[record.levelno]
            record.end_color = self._normal
        else:
            record.color = record.end_color = ''

        formatted = self._fmt % record.__dict__

        if record.exc_info:
            if not record.exc_text:
                record.exc_text = self.formatException(record.exc_info)
        if record.exc_text:
            # exc_text contains multiple lines.  We need to safe_unicode
            # each line separately so that non-utf8 bytes don't cause
            # all the newlines to turn into '\n'.
            lines = [formatted.rstrip()]
            lines.extend(
                safe_unicode(ln) for ln in record.exc_text.split('\n'))
            formatted = '\n'.join(lines)
        return formatted.replace("\n", "\n    ")


def _stderr_supports_color():
    color = False
    if curses and hasattr(sys.stderr, 'isatty') and sys.stderr.isatty():
        try:
            curses.setupterm()
            if curses.tigetnum("colors") > 0:
                color = True
        except Exception:  # pylint: disable=broad-except
            pass
    return color


def init_logger(log_conf, suffix=None, debug=False):
    """根据配置初始化日志
    :param log_conf: 日志的配置
    :param suffix: 是否设置后缀
    :param debug: 是否支持debug模式
    """
    if not log_conf or "handlers" not in log_conf:
        log_conf = DEFAULT_LOGGING_CONFIG
    for handler in log_conf['handlers'].values():
        if handler.get('filename'):
            path = os.path.expanduser(handler['filename'])
            if suffix:
                path = '%s.%s' % (path, suffix)
            dir_name = os.path.dirname(path)
            if dir_name and not os.path.exists(dir_name):
                os.makedirs(dir_name)
            handler['filename'] = path
    if debug and "console" in log_conf["handlers"]:
        log_conf["root"]["handlers"].append("console")
        log_conf["root"]["level"] = "DEBUG"
    logging.config.dictConfig(log_conf)
    logger = logging.getLogger()
    for channel in logger.handlers:
        if isinstance(channel, logging.FileHandler):
            channel.setFormatter(LogFormatter(color=False))
        else:
            channel.setFormatter(LogFormatter())
