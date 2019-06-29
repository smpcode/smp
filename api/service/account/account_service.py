# -*- coding: utf-8 -*-

"""
account_service
~~~~~~~~~~~~

账户相关的接口层封装

:copyright: (c) 2017 smpcode
:authors: smpcode
:version: 1.0 of 2017-05-04

"""
from datetime import datetime, timedelta
from playhouse.shortcuts import model_to_dict
from model.mysql.auth_models import (
    AuthUser,
    AuthRole,
    AuthDept,
    AuthUserRole,
)


class AccountService:

    """账户相关接口层封装
    """
    no_use_key = [
        "password",
    ]

    def __init__(self, database):
        """初始化服务
        :param database: 数据库对象`class common.db.database.Database`
        """
        self.user_model = AuthUser.use_db(database)
        self.dept_model = AuthDept.use_db(database)
        self.user_role_model = AuthUserRole.use_db(database)
        self.role_model = AuthRole.use_db(database)

    def get_user(self, account):
        """获取用户信息
        :param account: 账户名称
        """
        user = self.user_model.one(account=account)
        if not user:
            return
        user_info = model_to_dict(user, exclude=self.no_use_key)
        if not user_info:
            return
        return user_info

    def login(self, account, password, remote_ip=""):
        """登录
        :return: (AuthUser, Bool)
        :rtype: tupple
        """
        code = 0
        user, is_ok = self.user_model.login(account, password)
        if not user:
            code = 1001
        elif not is_ok:
            code = 1002
        else:
            user.visits = user.visits + 1
            user.ip = remote_ip
            user.save()
            user = model_to_dict(user, exclude=self.no_use_key)
        return user, is_ok, code

    def is_passwd_expire(self, expire_time):
        """ 检查密码是否已经过期
        """
        return expire_time and datetime.now() > expire_time

    def update_password(self, account, password, new_password):
        """ 更新密码
        :return: Bool
        :rtype: Bool
        """
        user, is_ok = self.user_model.login(account, password)
        if is_ok:
            if new_password == password:
                return is_ok, True
            user.password = new_password
            user.passwd_expire_time = datetime.now() + timedelta(days=90)
            user.save()
        return is_ok, False

    def get_roles(self, account):
        """获取账户角色

        :param account: 账户
        :return: 账户拥有的角色
        :rtype: set
        """
        user = AuthUser.one(account=account)
        if not user:
            return
        return set([str(urm.role.role) for urm in self.user_role_model.get_roles(user.id)])

    def add_to_tourists(self, account):
        """将指定账户加到游客分组,当用户首次登陆时默认分组
        """
        tourists = self.role_model.one(role='tourists')
        # 如果游客分组不存在则自动创建
        if not tourists:
            auth_role = AuthRole()
            auth_role.name = "游客"
            auth_role.role = "tourists"
            auth_role.desc = "游客默认分组"
            auth_role.save()
            tourists = self.role_model.one(role='tourists')
        account_role = self.user_role_model.one(
            account=account,
            role=tourists)
        if not account_role:
            ur = AuthUserRole()
            ur.user = AuthUser(account=account)
            ur.role = tourists
            ur.save()
