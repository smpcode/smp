# -*- coding: utf-8 -*-

"""
init_service
~~~~~~~~~~~~

服务统一初始化

:copyright: (c) 2017 smpcode
:authors: smpcode
:version: 1.0 of 2017-04-28

"""
import logging
from common.errors import ConfigError
from common.db.database import Database
from common.nsc import NSC


class ServicesManager:

    """服务管理
    """

    db_name = "hrsystem"

    database = {}
    services = {}

    def __init__(self, config):
        self.logger = logging.getLogger("hrapi")
        self.config = config
        self.nsc = NSC(config)
        self.init()

    def init(self):
        """初始化入口
        """
        self._init_database()
        self._init_redis()
        return self

    def get_db(self, db_name):
        """获取数据库对象
        """
        return self.database.get(db_name)

    def get_redis(self):
        """获取codis proxy对象
        """
        pass

    def _init_database(self):
        """初始化数据库
        """
        self.logger.debug("begin init database")
        database_config = self.config.get("database", None)
        if database_config is None:
            raise ConfigError("database is not in config")
        for db_name, db_config in database_config.items():
            self.logger.debug("exec _init_database, db_name=%s, db_config=%s",
                              db_name, db_config)
            db_user = db_config["user"]
            db_password = db_config["password"]
            namespace = db_config["namespace"]
            self.database[db_name] = Database(self.nsc, namespace, db_name, db_user, db_password)

    def _init_redis(self):
        """初始化redis
        """
        pass


    def finish(self):
        """结束初始化的服务连接
        """
        pass
