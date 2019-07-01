#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_tree
~~~~~~~~~~~~

测试tree

:copyright: (c) 2017 smpcode
:authors: smpcode
:version: 1.0 of 2017-05-26

"""

from common.utils import tree


def test_tree():
    tree_obj = tree.create_tree()
    tree_obj["test1"]["test2"] = 3
    assert "test1" in tree_obj
    assert "test2" in tree_obj.test1
    tree_obj1 = tree.create_tree()
    tree_obj1["t1"]["t2"]["k1"] = True
    tree_obj1["t1"]["t2"]["k2"] = True
    tree_obj1["t1"]["t2"]["k3"] = True
    keys_ = tree_obj1["t1"]["t2"]
    print(keys_)
    assert "k1" in keys_
    # 不赋值也会写入tree_obj1
    test = tree_obj1["t1"]["t3"]
    # 直接用属性赋值也会写入原对象
    h = test.t1.t4
    print("----->", h)
    print(test)
    print(tree_obj1)
    test2 = tree_obj1.get("t1", {}).get("t5", None)
    assert test2 is None
    print(tree_obj1)
