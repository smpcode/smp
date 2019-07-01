# -*- coding: utf-8 -*-

# pylint: disable=all
"""
test_rest
~~~~~~~~~~~~

测试rest文件

:copyright: (c) 2017 smpcode
:authors: smpcode
:version: 1.0 of 2017-05-10

"""
import json
import mock
import pytest
from peewee import SqliteDatabase
from peewee import Model
from peewee import *

from common.db.resource import Resource

database = SqliteDatabase('test.db')


def setup_module(module):
    print('\nsetup_module')
    User.create_table()
    Relationship.create_table()
    Message.create_table()
    user = User()
    user.username = "smpcode"
    user.password = "test"
    user.email = "smpcode@smpcode.com"
    user.join_date = "2017-07-01"
    user.save()
    user = User()
    user.username = "qilei"
    user.password = "qileitest"
    user.email = "qilei@smpcode.com"
    user.join_date = "2017-02-01"
    user.save()
    user = User()
    user.username = "test"
    user.password = "test123"
    user.email = "test@smpcode.com"
    user.join_date = "2017-02-02"
    user.save()
    rs = Relationship()
    rs.from_user = 1
    rs.to_user = 2
    rs.save()
    msg = Message()
    msg.user = 1
    msg.content = "i am content1"
    msg.pub_date = "2017-01-12"
    msg.save()
    msg = Message()
    msg.user = 2
    msg.content = "i am content2"
    msg.pub_date = "2017-02-12"
    msg.save()


def teardown_module(module):
    print('\nteardown_module')
    User.drop_table()
    Relationship.drop_table()
    Message.drop_table()


class BaseModel(Model):

    class Meta:
        database = database

    @classmethod
    def one(cls, *query, **kwargs):
        '''获取单条数据
        :retrun: 返回单条数据不存在则返回None
        '''
        try:
            return cls.get(*query, **kwargs)
        except DoesNotExist:
            return None


class User(BaseModel):
    username = CharField(unique=True)
    password = CharField()
    email = CharField()
    join_date = DateTimeField()

    class Meta:
        order_by = ('username',)


class Relationship(BaseModel):
    from_user = ForeignKeyField(User, related_name='relationships')
    to_user = ForeignKeyField(User, related_name='related_to')

    class Meta:
        indexes = (
            (('from_user', 'to_user'), True),
        )


class Message(BaseModel):
    user = ForeignKeyField(User)
    content = TextField()
    pub_date = DateTimeField()

    class Meta:
        order_by = ('-pub_date',)


class Handler:

    arg_map = {
        "username": "smpcode",
        "ordering": "id",
        "limit": '10',
        "page": '1',
        "pk": 3,
        "data": json.dumps({"username": "qilei2", "email": "qilei2@smpcode.com", "password": "1223", "join_date": "2016-09-04"}),
    }

    arguments = [
        "smpcode",
        "qilei",
    ]

    def __init__(self, username=None, data=None, arguments=None, pk=None):
        if pk:
            self.arg_map["pk"] = pk
        if username:
            self.arg_map["username"] = username
        if data:
            self.arg_map["data"] = data
        if arguments:
            self.arguments = arguments

    @property
    def request(self):
        class Request:
            arguments = self.arguments
        return Request()

    def get_argument(self, arg, default=None):
        print("do get_argument", arg)
        return self.arg_map.get(arg, default)

    def get_arguments(self, arg):
        return self.arguments


class UserResource(Resource):
    exclude = ('password',)
    model = User


class RelationshipResource(Resource):
    include_resources = {'from_user': UserResource, 'to_user': UserResource}
    model = Relationship


class MessageResource(Resource):
    include_resources = {'user': UserResource}
    model = Message


def test_read_by_page():
    """测试获取对象列表
    """

    handler = Handler()
    user_res = UserResource(handler)
    object_list = user_res.read_by_page()
    # expected result
    # {"meta":{"page":1,"model":"user","next":"","previous":""},"objects":[{"id":1,"join_date":"2017-07-01
    # 00:00:00","username":"smpcode"}]}
    # object_list = json.loads(object_list)
    assert "meta" in object_list
    assert "objects" in object_list
    assert isinstance(object_list["objects"], list)
    assert object_list["objects"][0]["username"] == "smpcode"


def test_read_detail():
    """测试获取对象详情
    """

    handler = Handler(pk=1)
    rsr = RelationshipResource(handler)
    """
    obj = Relationship.select().where(
        Relationship.from_user == 1
    ).get()
    object_detail = rsr.read_detail(obj)
    """
    object_detail = rsr.read_detail()
    assert isinstance(object_detail, dict)
    assert object_detail["id"] == 1
    assert object_detail["from_user"]["username"] == "smpcode"
    assert object_detail["to_user"]["username"] == "qilei"


def test_delete():
    """测试删除字段
    """
    obj = User.select().where(User.username == "test").get()
    handler = Handler(pk=obj.id)
    user_res = UserResource(handler)
    """
    obj = User.select().where(User.username == "test").get()
    data = user_res.delete(obj)
    """
    data = user_res.delete()
    assert data["deleted"] == 1
    try:
        obj = User.select().where(User.username == "test").get()
        expected = False
    except DoesNotExist:
        expected = True
    assert expected


def test_edit():
    """测试编辑
    """
    handler = Handler()
    user_res = UserResource(handler)
    data = user_res.edit()
    # data = json.loads(data)
    assert data["username"] == "qilei2"
    assert "password" not in data


def test_create():
    """测试创建实例
    """
    data = json.dumps({"username": "baijiangtao", "email": "baijiangtao@smpcode.com",
                       "password": "r1223", "join_date": "2011-09-04"})
    handler = Handler(data=data)
    user_res = UserResource(handler)
    user = user_res.create()
    # user = json.loads(user)
    assert user["email"] == "baijiangtao@smpcode.com"
