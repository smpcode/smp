#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cli
~~~~~~~~~~~~

命令行解析逻辑

:copyright: (c) 2019 smpcode
:authors: smpcode
:version: 1.0 of 2019-04-10

"""
import os
import logging

import click

import apps
from common.utils.config import Config

__author__ = "smpcode"
__version__ = "0.1.0"

pass_config = click.make_pass_decorator(Config, ensure=True)  # pylint:disable=invalid-name


def read_config(ctx, _, value):
    """定义解析配置的回调函数."""
    cfg = ctx.ensure_object(Config)
    if not value:
        return
    if not os.path.exists(value):
        return
    cfg.read_config(value)
    return value


@click.group(context_settings={'help_option_names': ['-h', '--help']})
@click.version_option(
    __version__, '-v', '--version', help="show api version")
@click.option(
    '-f',
    '--config-file',
    type=click.Path(exists=True, dir_okay=False),
    callback=read_config,
    expose_value=False,
    required=True,
    help='specify config file path')
def cli():
    """api client"""
    pass


# api 入口
@cli.command(name="api")
@click.option(
    '-P',
    '--prefork',
    help="use prefork for multi processes",
    type=int,
    default=0)
@click.option('-D', '--debug', help="use debug model", is_flag=True)
@click.option('-p', '--port', help="port", type=int, default=8000)
@click.option('-r', '--route', help="route", default="all")
@click.option('-s', '--static-path', help="static file path", default=os.path.dirname(__file__))
@click.option('-a', '--allow-origin', help="allow origin")
@pass_config
def api_command(config, debug, prefork, port, route, static_path, allow_origin):
    """start api http server"""
    if debug:
        import tornado.autoreload  # pylint: disable=unused-import
    try:
        apps.start(config.cfg, route, static_path,
                   debug, prefork, port, allow_origin)
    except IOError as ioex:
        logging.error(os.strerror(ioex.errno))


if __name__ == '__main__':
    cli()
