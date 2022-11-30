"""스키마 유틸"""

import json
from typing import Type, Any

from pydantic import ConfigError, validate_model
from pydantic.main import object_setattr
from pydantic.utils import ROOT_KEY


# pylint: disable=W0212
def from_orm_with_json_converter(cls: Type['Model'], obj: Any, json_entry=None) -> 'Model':
    """json converter 추가 함수"""
    if json_entry is None:
        json_entry = []
    if not cls.__config__.orm_mode:
        raise ConfigError('You must have the config attribute orm_mode=True to use from_orm')
    obj = {ROOT_KEY: obj} if cls.__custom_root_type__ else cls._decompose_class(obj)
    model = cls.__new__(cls)
    values, fields_set, validation_error = validate_model(cls, obj)
    if validation_error:
        raise validation_error

    for (k, val) in json_entry:
        values[k] = json.loads(values[val])
        fields_set.add(k)
    object_setattr(model, '__dict__', values)
    object_setattr(model, '__fields_set__', fields_set)
    model._init_private_attributes()
    return model
