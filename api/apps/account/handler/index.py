# -*- coding: utf-8 -*-

"""
index
~~~~~~~~~~~~

首页加载

:copyright: (c) 2019 smpcode
:authors: smpcode
:version: 1.0 of 2019-05-16

"""

from apps.account.handler.base import AccountBaseHandler


class IndexHandler(AccountBaseHandler):
    """程序执行入口
    """

    def get(self):
        '''入口
        '''
        self.render("index.html")
        vue_index_path = self.settings["template_path"] + "index.html"
        with open(vue_index_path, 'r') as file:
            self.write(file.read())
