# -*- coding: utf-8 -*-

# pylint: disable=missing-docstring
"""
test_base_mixin
~~~~~~~~~~~~


:copyright: (c) 2017 smpcode
:authors: smpcode
:version: 1.0 of 2017-04-19

"""

from common.utils import base_mixin


class MyMixin(base_mixin.BaseMixin):
    pass


def test_base_mixin():

    sm = MyMixin()

    class Test:

        def test_hi(self):
            return "name_is_test"

    sm.register("test", Test())
    assert sm.test.test_hi() == "name_is_test"
    sm.unregister("test")
    assert sm.test is None
