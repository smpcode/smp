# -*- coding: utf-8 -*-

"""
serializer
~~~~~~~~~~~~

序列化/反序列化model

:copyright: (c) 2017 smpcode
:authors: smpcode
:version: 1.0 of 2017-05-10

"""
import datetime
from peewee import Model
from common.db.utils import get_dictionary_from_model
from common.db.utils import get_model_from_dictionary


class Serializer:

    """序列化对象
    """
    date_format = '%Y-%m-%d'
    time_format = '%H:%M:%S'
    datetime_format = ' '.join([date_format, time_format])

    def convert_value(self, value):
        """将特定字段进行转换
        """
        if isinstance(value, datetime.datetime):
            return value.strftime(self.datetime_format)
        elif isinstance(value, datetime.date):
            return value.strftime(self.date_format)
        elif isinstance(value, datetime.time):
            return value.strftime(self.time_format)
        elif isinstance(value, Model):
            return value.get_id()
        else:
            return value

    def clean_data(self, data):
        """清洗数据
        """
        for key, value in data.items():
            if isinstance(value, dict):
                self.clean_data(value)
            elif isinstance(value, (list, tuple)):
                data[key] = map(self.clean_data, value)
            else:
                data[key] = self.convert_value(value)
        return data

    def serialize_object(self, obj, fields=None, exclude=None):
        """从model获取字段
        """
        data = get_dictionary_from_model(obj, fields, exclude)
        return self.clean_data(data)


class Deserializer:

    """反序列化对象
    """

    def deserialize_object(self, model, data):
        """从model获取反序列化字段
        """
        return get_model_from_dictionary(model, data)
