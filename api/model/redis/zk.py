# -*- coding: utf-8 -*-

"""
zk
~~~~~~~~~~~~

zk节点树管理：
1、key是zk的节点路径，目前就存储2级路径，即分组和项目两级
2、value是这个路径的zk的节点树

:copyright: (c) 2019 smpcode
:authors: smp
:version: 1.0 of 2018-07-03

"""
import logging as log
from common.errors import RedisKeyError
from zymodel.redis.base import BaseModel


class ZKRedisModel(BaseModel):
    """zookeeper的节点树信息
    """
    prefix = 'zk'

    def set(self, zk_path, znode_tree_data, timeout):
        """设置zk的节点数信息
        """
        if not zk_path:
            raise RedisKeyError("redis construct zookeeper_key required zk_path")
        zk_key = self.key[zk_path]
        if isinstance(zk_key, bytes):
            zk_key = zk_key.decode("utf8")
        self.db.set(zk_key, znode_tree_data)
        self.db.api.expire(zk_key, timeout)

    def get(self, zk_path):
        """获取zk的节点树信息
        """
        if not zk_path:
            raise RedisKeyError("redis construct zookeeper_key required zk_path")
        zk_key = self.key[zk_path]
        if isinstance(zk_key, bytes):
            zk_key = zk_key.decode("utf8")
        return self.db.get(zk_key)

    def delete(self, zk_path):
        """删除k的节点树信息
        """
        if not zk_path:
            raise RedisKeyError("redis construct zookeeper_key required zk_path")
        zk_key = self.key[zk_path]
        if isinstance(zk_key, bytes):
            zk_key = zk_key.decode("utf8")
        try:
            del self.db[zk_key]
        except KeyError as err:
            log.error("redis delete error=%s, redis key: %s",
                      err, zk_key)
            return False
        return True
