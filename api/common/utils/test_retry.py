#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_retry
~~~~~~~~~~~~

测试retry策略装饰器

:copyright: (c) 2016 smpcode
:authors: smpcode
:version: 1.0 of 2017-07-06

"""
from common.utils.retry import retry

my_func_run_times = 1
pre_hook_flag = False
post_hook_flag = False

def test_retry():
    """测试重试装饰器
    """
    def pre_hook():
        """异常后再次执行时调用
        """
        global pre_hook_flag
        pre_hook_flag = True
        print("pre_hook was called, ", pre_hook_flag)
        return

    def post_hook():
        """异常后再次执行时调用
        """
        global post_hook_flag
        post_hook_flag = True
        print("post_hook was called, ", post_hook_flag)

    @retry(retry_num=3, ex_type=ValueError, pre_hook=pre_hook, post_hook=post_hook)
    def my_func():
        """测试函数
        """
        global my_func_run_times
        my_func_run_times = my_func_run_times + 1
        raise ValueError("no value error")

    my_func()  # 被装饰的函数永远不会抛出异常
    assert pre_hook_flag
    assert post_hook_flag is False
    assert my_func_run_times == 4
