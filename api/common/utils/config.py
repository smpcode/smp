# -*- coding: utf-8 -*-

"""
config
~~~~~~~~~~~~

解析配置文件逻辑

:copyright: (c) 2016 smpcode
:authors: smpcode
:version: 1.0 of 2016-07-14

"""
import sys

import lya
import yaml

from common.utils.singleton import SingletonMixin


class Config(SingletonMixin):
    """传递配置项到命令行参数,单例
    :param cfg: lya解析后的配置对象
    """

    def __init__(self):
        self.cfg = {}

    def read_config(self, filename):
        """将文件路径解析为配置对象
        :param filename: 配置文件路径
        """
        try:
            self.cfg = lya.AttrDict.from_yaml(filename)
        except yaml.parser.ParserError:
            sys.exit(1)
