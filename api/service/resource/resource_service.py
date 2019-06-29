# -*- coding: utf-8 -*-

"""
base
~~~~~~~~~~~~

基于Model的rest接口统一处理

:copyright: (c) 2017 smpcode
:authors: smpcode
:version: 1.0 of 2017-05-11

"""
import logging as log
from common.errors import NotFoundError
from common.db.resource import Resource
from common.utils import tree


class ResourceService:

    """资源基类,提供统一钩子
    """
    _resource_map = tree.create_tree()

    def __init__(self, handler):
        """依赖
        :param handler: tornado handler实例
        """
        self.handler = handler

    def get_db(self, db_name):
        """通过db_name获取数据库对象
        """
        # 如果db不存在会排除ValueError异常
        database = self.handler.settings['service_manager'].database
        if db_name not in database:
            raise NotFoundError("no db named {}".format(db_name))
        return database[db_name]

    def register(self, db_name, resource_name):
        """注册资源,支持链式表达
        """
        db = self.get_db(db_name)
        resource = self.get_resource(db_name, resource_name)
        # 支持动态db逻辑
        model_class = resource.model
        resource.model = model_class.use_db(db)
        # 关联资源必须同一个数据库
        if resource.relation_model:
            # 将相关数据库进行确定
            for rel_model in resource.relation_model:
                rel_model.use_db(db)
        self.resource = resource(self.handler)
        return self

    @classmethod
    def add_resouce(cls, db_name, resource_name, resource):
        """
        :param db_name: 数据库名
        :param resource_name: 资源名称
        :param resource: 资源对象
        """
        if not resource_name or not db_name:
            raise ValueError("resource_name is required")
        if not issubclass(resource, Resource):
            raise TypeError("resource type error")
        cls._resource_map[db_name][resource_name] = resource

    def get_resource(self, db_name, resource_name):
        """根据资源名称获取资源对象
        :param resource_name: 资源名称
        """
        resource = self._resource_map.get(db_name, {}).get(resource_name, None)
        if resource is None:
            raise NotFoundError("no resource named {}".format(resource_name))
        return resource

    def create(self):
        """创建资源
        """
        self._before_create()
        ret = self.resource.create()
        self._after_create()
        return ret

    def read(self):
        """读取资源
        """
        self._before_read()
        ret = self.resource.read()
        self._after_read()
        return ret

    def read_by_page(self):
        self._before_read()
        ret = self.resource.read_by_page()
        self._after_read()
        return ret

    def read_detail(self, pk):
        """读取资源
        """
        self._before_read()
        ret = self.resource.read_detail(pk)
        self._after_read()
        return ret

    def edit(self):
        """更新资源
        """
        self._before_edit()
        ret = self.resource.edit()
        self._after_edit()
        return ret

    def delete(self, pk=None):
        """删除资源
        """
        self._before_delete()
        ret = self.resource.delete(pk)
        self._after_delete()
        return ret

    def _before_create(self):
        """before create hook
        """
        log.debug("before create")

    def _after_create(self):
        """after create hook
        """
        log.debug("after create")

    def _before_delete(self):
        """before delete hook
        """
        log.debug("before delete")

    def _after_delete(self):
        """after delete hook
        """
        log.debug("after delete")

    def _before_edit(self):
        """before edit hook
        """
        log.debug("before edit hook")

    def _after_edit(self):
        """after edit hook
        """
        log.debug("after edit hook")

    def _before_read(self):
        """before read hook
        """
        log.debug("before read hook")

    def _after_read(self):
        """after read hook
        """
        log.debug("after read hook")
