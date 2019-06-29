# -*- coding: utf-8 -*-

"""
server
~~~~~~~~~~~~

account server

:copyright: (c) 2017 smpcode
:authors: smpcode
:version: 1.0 of 2017-04-21

"""
# pylint: disable=no-value-for-parameter

# sys
import os
import logging as log
import socket
# third
import tornado
import tornado.web
import tornado.httpserver
import tornado.ioloop
# inner
from service import ServicesManager
from common.session.session import SessionManager
from common.utils import class_path
from common.utils.logger import init_logger
# urls
from apps.resource import urls as resource_urls
from apps.account import urls as account_urls


class Application(tornado.web.Application):
    """定义应用程序
    """

    def __init__(self,  # pylint: disable=too-many-arguments
                 config,
                 routes,
                 service_manager,
                 static_path,
                 allow_origin,
                 debug=False):
        self.debug = debug
        route_ref = {}
        for route in routes:
            key = class_path(route[1])
            val = route_ref.get(key, [])
            val.append(route[0])
            route_ref[key] = val

        settings = {
            "xsrf_cookies": True,
            "site_title": "account",
            "debug": debug,
            "config": config,
            'cookie_secret': 'ek39976x43e4e8442f099fed1f3fea18x62e58320483aeed9a3d5d3859f==78d',
            'session_secret': '2cdcb1m00803b6e78233333213xab33x3333331x191x111jkslfjsalkfjlskj',
            'jwt_token': "just for my sister test",
            'jwt_algorithm': 'HS256',
            'jwt_roles': ['config_admin'],
            "session_timeout": 604800,
            "service_manager": service_manager,
            "login_url": "/smp/account/login",
            "allow_origin": allow_origin,
            "static_path": os.path.join(static_path, "./static"),
            "template_path": os.path.join(static_path, "./tpls"),
            "route_ref": route_ref
        }
        self.session_manager = SessionManager(settings["session_secret"],
                                              settings["session_timeout"])
        self.service_manager = service_manager
        tornado.web.Application.__init__(
            self,
            routes,
            **settings
        )


def start(config, route, static_path, debug=False, prefork=0, port=8000, allow_origin=""):
    """start server
    """
    init_logger(config.get("server_log_conf"), suffix=port, debug=debug)
    service_manager = ServicesManager(config)

    routes = []

    # all for test
    if "all" in route:
        routes.extend(resource_urls.URL_ROUTES)
        routes.extend(account_urls.URL_ROUTES)
    if routes:
        # app配置
        app = Application(
            config=config,
            routes=routes,
            service_manager=service_manager,
            static_path=static_path,
            allow_origin=allow_origin,
            debug=debug)
        http_server = tornado.httpserver.HTTPServer(app, xheaders=True)
        if prefork > 0:
            http_server.bind(port, family=socket.AF_INET)
            http_server.start(prefork)
        else:
            http_server.listen(port)
        log.info("server start ok, listen port=%s, debug=%s", port, debug)
    elif not route or route == "none":
        #如果不配置route 或者 route=none  走定时逻辑
        scheduler = task.init_scheduler(config)
        scheduler.start()
    try:
        tornado.ioloop.IOLoop.instance().start()
    except (KeyboardInterrupt, SystemExit):
        log.info("Bye!")
