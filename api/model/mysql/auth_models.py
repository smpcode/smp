# -*- coding: utf-8 -*-

"""
arch_models
~~~~~~~~~~~~

:copyright: (c) 2019 smpcode
:authors: smpcode
:version: 1.0 of 2019-06-07

"""
# pylint: disable=missing-docstring,duplicate-bases,invalid-name
import logging as log
from datetime import datetime
import ujson as json
from peewee import (
    CharField,
    IntegerField,
    ForeignKeyField,
    DateTimeField,
    TextField,
    DateField,
    SelectQuery,
    DoesNotExist
)
from common.db.database import Database
from common.db.hook import (
    post_save,
)
from model.mysql.base import BaseModel


class AuthDept(BaseModel):

    """部门表
    """

    id = IntegerField(primary_key=True)
    function = CharField()
    grade = IntegerField()
    manager = IntegerField()
    name = CharField()
    order = IntegerField()
    parent = IntegerField()
    path = CharField()
    position = CharField()
    email = CharField()

    class Meta:
        db_table = 'auth_dept'

    @classmethod
    def get_dept_nodes(cls):
        """获取全部组织信息
        """
        return cls.select().order_by(cls.grade, cls.order)


class AuthSystem(BaseModel):

    """系统表
    """

    id = IntegerField(primary_key=True)
    desc = CharField(null=True)
    name = CharField()

    class Meta:
        db_table = 'auth_system'


class AuthResource(BaseModel):

    """资源表
    """

    id = IntegerField(primary_key=True)
    create_time = DateTimeField(null=True)
    create_user = CharField(null=True)
    name = CharField()
    sys = ForeignKeyField(db_column='sys_id',
                          rel_model=AuthSystem, to_field='id')
    update_time = DateTimeField(default=datetime.now)
    update_user = CharField(null=True)
    uri = CharField(null=True)

    class Meta:
        db_table = 'auth_resource'

    @classmethod
    def get_resources(cls, sys_id):
        """获取指定系统的所有的资源
        :param sys_id: 系统id
        :return: 返回查找的Query对象或者None
        """
        if not sys_id:
            return
        return cls.select().join(AuthSystem).where(AuthSystem.id == sys_id)


class AuthRole(BaseModel):

    """角色表
    """

    id = IntegerField(primary_key=True)
    create_time = DateTimeField(null=True)
    create_user = CharField(null=True)
    desc = CharField()
    name = CharField()
    role = CharField()
    update_time = DateTimeField(default=datetime.now)
    update_user = CharField(null=True)

    class Meta:
        db_table = 'auth_role'


class AuthRoleResource(BaseModel):

    """角色资源对应关系
    """

    id = IntegerField(primary_key=True)
    create_time = DateTimeField(null=True)
    create_user = CharField(null=True)
    method = CharField()
    resource = ForeignKeyField(
        db_column='resource_id', rel_model=AuthResource, to_field='id')
    role = ForeignKeyField(db_column='role_id',
                           rel_model=AuthRole, to_field='id')
    update_time = DateTimeField(default=datetime.now)
    update_user = CharField(null=True)

    class Meta:
        db_table = 'auth_role_resource'

    @classmethod
    def get_role_resource(cls, role_id):
        """获取指定角色资源
        :param role_id: 角色id
        """
        return cls.select().join(AuthRole).where(AuthRole.id == role_id)

    @classmethod
    def fetchall(cls):
        """获取整个表数据
        """
        # 使用main_database的execute_sql执行避免关联查询
        return cls._meta.database.execute_sql("select role_id, resource_id, method from auth_role_resource").fetchall()


class AuthUser(BaseModel):

    """用户表
    基于mysql外键进行关联删除，当用户被删除时用户的角色关联信息会自动同步删除
    """

    id = IntegerField(primary_key=True)
    account = CharField(unique=True)
    avatar = CharField()
    birthday = DateField()
    create_time = DateField()
    dept = ForeignKeyField(db_column='dept_id',
                           rel_model=AuthDept, to_field='id')
    email = CharField()
    gender = CharField()
    ip = CharField()
    is_superuser = IntegerField(null=True)
    mobile = CharField()
    office = CharField()
    password = CharField()
    realname = CharField()
    update_time = DateTimeField(default=datetime.now)
    visits = IntegerField()

    class Meta:
        db_table = 'auth_user'

    @staticmethod
    def login(account, password):
        '''进行登录名、密码验证
        '''
        u = AuthUser.one(account=account)
        if u is None:
            # 如果账户不存在
            return None, False
        return u, AuthUser.check_passwd(u.password, password)

    @staticmethod
    def check_passwd(account_pwd, input_pwd):
        '''校验密码
        '''
        return account_pwd == input_pwd

    @classmethod
    def get_user_by_ids(cls, ids):
        if not ids:
            return None
        return cls.select().where(cls.id << ids)


class AuthUserRole(BaseModel):

    """用户角色对应关系表
    :param role: 角色外键，角色删除时自动被删除
    :param user: 用户外键，用户删除时自动被删除
    """

    id = IntegerField(primary_key=True)
    role = ForeignKeyField(db_column='role_id',
                           rel_model=AuthRole, to_field='id')
    user = ForeignKeyField(db_column='user_id',
                           rel_model=AuthUser, to_field='id')

    class Meta:
        db_table = 'auth_user_role'

    @classmethod
    def get_roles(cls, user_id):
        """获取指定用户的角色
        """
        if not user_id:
            return None
        return cls.select().join(AuthUser).where(AuthUser.id == user_id)

    def __str__(self):
        """
        """
        return "{}:{}".format(self.account, self.role)


class AuthKVDB(BaseModel):

    """模拟列数据库存储数据,仅保存数据字典,不要保存大量数据因为会影响条件查询性能
    """
    create_time = DateTimeField(null=True)
    create_user = CharField(null=True)
    deleted = CharField(null=True)
    desc = CharField(null=True)
    key = CharField(unique=True)
    update_time = DateTimeField()
    update_user = CharField(null=True)
    value = TextField()  # json.dumps数据

    class Meta:
        """meta config
        """
        db_table = 'auth_kvdb'

    @classmethod
    def do_get(cls, key, default=None):
        """根据key取value

        :param key: 数据字典的key,在数据中为唯一
        :type key: string
        :param default: 默认值，如果取不到返回default
        """
        if not key:
            return default
        record = cls.one(key=key)
        if record is None:
            return default
        try:
            val = json.loads(record.value)
        except ValueError:
            val = record.value
        return val

    @classmethod
    def do_set(cls, key, value, desc=''):
        '''写入K/V对

        :param key: 键
        :type key: str
        :param value: 值为json.dumps后的数据
            数据举例:
                [{
                    'key': 'test',
                    'value': 'haha',
                    'order': 1,
                    'desc': '测试'
                }]
        :type value: str
        :param desc: 描述
        '''
        if not key or not value:
            return
        try:
            val = json.dumps(value)
        except ValueError:
            val = value
        try:
            kv_pair = cls.select().where(AuthKVDB.key == key).get()
        except AuthKVDB.DoesNotExist:
            kv_pair = AuthKVDB()
        kv_pair.key = key
        kv_pair.value = val
        kv_pair.desc = desc
        kv_pair.save()

    @classmethod
    def do_delete(cls, key):
        '''删除Key
        '''
        if not key:
            return
        cls.delete().where(AuthKVDB.key == key).execute()

    @classmethod
    def do_search(cls, query):
        """模糊搜索搜索KV表

        :param query: 查询的词
        :type query: str
        """
        return cls.select().where(
            (AuthKVDB.key.contains(query)) |
            (AuthKVDB.value.contains(query)) |
            (AuthKVDB.desc.contains(query))
        )


@post_save(sender=AuthResource)
def auth_resource_post_save(_, instance, created):
    """资源保存后执行
    """
    if created:
        # insert 操作
        if not Database.current_user:
            log.error("unknown user executed")
            return
        roles = Database.current_user['roles']
        if roles is None or not instance.uri:
            return
        # 强制使用主库进行查找
        try:
            resource = SelectQuery(AuthResource).join(AuthSystem).where(
                (AuthResource.uri == instance.uri) &
                (AuthSystem.id == instance.sys.id)
            ).get()
        except DoesNotExist:
            return
        for role in roles:
            role_resource = AuthRoleResource()
            role_resource.role = AuthRole.one(role=role)
            role_resource.resource = resource
            role_resource.method = 'index'
            role_resource.save()
            log.info('do post_save on AuthResource, role=%s, resource=%s, methd=index',
                     role, resource.uri)


class AuthApi(BaseModel):
    create_time = DateTimeField(null=True)
    doc = CharField()
    method = CharField()
    sys = ForeignKeyField(db_column='sys_id', rel_model=AuthSystem, to_field='id')
    update_time = DateTimeField(null=True)
    uri = CharField()

    class Meta:
        db_table = 'auth_api'
        indexes = (
            (('uri', 'sys'), True),
        )


class AuthRoleApi(BaseModel):
    api = ForeignKeyField(db_column='api_id', rel_model=AuthApi, to_field='id')
    create_time = DateTimeField(null=True)
    method = CharField(null=True)
    role = ForeignKeyField(db_column='role_id', rel_model=AuthRole, to_field='id')
    update_time = DateTimeField(null=True)

    class Meta:
        db_table = 'auth_role_api'
        indexes = (
            (('role', 'api', 'method'), True),
        )
