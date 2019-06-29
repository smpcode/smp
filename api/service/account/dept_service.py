# -*- coding: utf-8 -*-

"""
dept_service
~~~~~~~~~~~~

部门信息

:copyright: (c) 2016 smpcode
:authors: smpcode
:version: 1.0 of 2017-06-14

"""
from functools import lru_cache
from playhouse.shortcuts import model_to_dict

from model.mysql.auth_models import (
    AuthDept,
    AuthUser
)

from common.utils import tree


def build_forest(nodelist):
    """基于列表进行构建

    :param nodelist: 列表保存节点id和父节点id
    :type nodelist: Query
    :return: 构建完成的树形结构
    """

    forest = []
    nodes = {}

    for nodeobj in nodelist:
        node_id = nodeobj.id
        node_name = nodeobj.name
        node_path = nodeobj.path
        node_email = nodeobj.email
        node_function = nodeobj.function
        node_manager = AuthUser.one(id=nodeobj.manager)
        parent_id = nodeobj.parent

        if node_id not in nodes:
            node = {
                "id": node_id,
                "name": node_name,
                "path": node_path,
                "email": node_email,
                "manager": {
                    'id': node_manager.id,
                    'name': node_manager.realname,
                },
                "function": node_function
            }
            nodes[node_id] = node
        else:
            node = nodes[node_id]
            if "name" not in node:
                node["name"] = node_name
            if "path" not in node:
                node["path"] = node_path
            if "email" not in node:
                node["email"] = node_email
            if "function" not in node:
                node["function"] = node_function

        if node_id == parent_id:
            forest.append(node)
        else:
            # 此时遍历的节点没有父节点的属性信息,仅记录id,等遍历到该节点时进行更新
            if parent_id not in nodes:
                parent = {
                    "id": parent_id
                }
                nodes[parent_id] = parent
            else:
                parent = nodes[parent_id]
            if "children" not in parent:
                parent["children"] = []
            parent["children"].append(node)

    return forest


class DeptService:

    """部门相关接口封装
    """

    def __init__(self, database):

        self.database = database

        self.user_model = AuthUser.use_db(database)
        self.dept_model = AuthDept.use_db(database)

    @lru_cache(maxsize=3)
    def get_dept_nodes(self):
        """获取所有的部门信息
        """
        dept_nodes = self.dept_model.get_dept_nodes()
        if not dept_nodes:
            return
        return build_forest(dept_nodes)
