# -*- coding: utf-8 -*-

"""
retry
~~~~~~~~~~~~

通用retry装饰器

:copyright: (c) 2016 smpcode
:authors: smpcode
:version: 1.0 of 2017-07-06

"""
import logging as log
import traceback
import functools

def retry(retry_num=1, ex_type=Exception, pre_hook=None, post_hook=None):
    """通用重试策略装饰器

    :param retry_num: 重试次数
    :param ex_type: 异常类型，default全部异常, 当发生指定异常时进行重试，如果不修改ex_type则被装饰的函数永远不抛出异常
    :param pre_hook: 当重试时在调用函数前执行
    :param post_hook: 当重试时在调用的函数后执行
    :return: 正常函数执行结果或者返回参数中的default值
    """
    def decorator(func):
        """对func进行装饰
        """
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            """ 截获异常ex_type返回then_result
            """
            for num in range(retry_num):
                try:
                    if num > 0 and pre_hook and callable(pre_hook):
                        pre_hook()
                    result = func(*args, **kwargs)
                    if num > 0 and post_hook and callable(post_hook):
                        post_hook()
                    return result
                except ex_type:  # pylint: disable=broad-except
                    log.error(
                        "exec %s, error=%s",
                        func.__name__,
                        traceback.format_exc())
        return wrapper
    return decorator
