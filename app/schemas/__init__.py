"""
idx 있을 경우 기본적인 Orm
"""
from collections import ChainMap
from datetime import datetime
from typing import Any, Container, Optional, Type, TypeVar, Union

from humps.main import camelize
from pydantic import BaseConfig, BaseModel, Field, create_model
from sqlalchemy import inspect
from sqlalchemy.orm import ColumnProperty


class Orm(BaseModel):
    """idx 를 포함하지 않는 orm 기초 모델"""
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        """orm 을 이용하기 위한 세팅"""
        orm_mode = True
        arbitrary_types_allowed = True


class IdxOrm(Orm):
    """idx 를 포함하는 orm 기초 모델"""
    idx: int


class IdOrm(Orm):
    """id 만 포함하는 orm 기초 모델"""
    id: str


class _OrmConfig(BaseConfig):
    """Base config for Pydantic models."""

    orm_mode = True
    alias_generator = camelize
    allow_population_by_field_name = True


Model = TypeVar("Model")


def _from_pydantic(model: Model) -> dict[Any, tuple[Any, Any]]:
    """Convert Pydantic dataclass to dict, for further including.
    :param model: Pydantic model dataclass
    :return: dict format model
    """
    fields, new_fields = model.__fields__, {}
    for name, value in fields.items():
        if hasattr(value, "type_"):
            if "__main__" in str(value.type_):
                new_fields[name] = Optional[_from_pydantic(value.type_)]
            else:
                new_fields[name] = (Optional[value.type_], ...)
    return new_fields


def _model_dict(
        model_name: str, dict_def: dict, *, inner: bool = False
) -> Union[Model, dict[Any, tuple[Any, Any]]]:
    """Convert a dictionary to a form suitable for pydantic.create_model.
    :param model_name: Name of further schema
    :param dict_def: Source of fields data
    :param inner: If model field is nested
    :return: fields dict for pydantic.create_model
    """
    model_name = model_name.replace("_", " ").capitalize()
    fields = {}
    for name, value in dict_def.items():
        # pylint: disable=protected-access
        if hasattr(value, '_name') and value._name == 'List':
            fields[name] = tuple([value, Field(...)])
        elif issubclass(value, BaseModel):
            fields[name] = tuple([value, Field(...)])
        elif isinstance(value, tuple):
            fields[name] = value if len(value) > 1 else tuple([value[0], Field(...)])
        elif isinstance(value, dict):
            fields[name] = (
                _model_dict(f"{model_name}_{name}", value, inner=True),
                ...,
            )
        else:
            raise ValueError(f"Field {model_name}:{value} has invalid syntax")
    return create_model(model_name, **fields) if inner else fields


def make_schema_from_orm(
        db_model: Type,
        model_name,
        *,
        config: BaseConfig = _OrmConfig,
        include: dict[str, Union[Type[BaseModel], tuple[Type[BaseModel], Type[Field]], Type[list[BaseModel]]]] = (),
        exclude: Container[str] = (),
        exclude_all: Container[str] = (),
        required: Container[str] = (),
        required_all: bool = False,
        validators: dict[str, classmethod] = None,
) -> Model:
    """
    :param db_model: Base를 상속받은 데이터 모델
    :param model_name: 모델 이름
    :param config: 모델 설정
    :param include: 필드 재정의 혹은 추가
    :param exclude: 필드 제외
    :param exclude_all: 해당 필드 외에 모두 제외
    :param required: 필수 필드
    :param required_all: 모두 필수 필드
    :param validators:
    :return:
    """
    if exclude and exclude_all:
        raise ValueError(
            "You can define only one of parameters(exclude, exclude_all)"
        )

    inspection = inspect(db_model)
    fields, defaults = {}, {int: 0, float: 0.0, str: "", bool: False, dict: {}}
    for attr in inspection.attrs:
        if isinstance(attr, ColumnProperty):
            if attr.columns:
                name = attr.key
                if name in exclude:
                    continue
                if exclude_all and name not in exclude_all:
                    continue
                column, _type = attr.columns[0], None
                if hasattr(column.type, "impl"):
                    if hasattr(column.type.impl, "python_type"):
                        _type = column.type.impl.python_type
                elif hasattr(column.type, "python_type"):
                    _type = column.type.python_type

                default = (
                    Field(defaults.get(_type, ...))
                    if required_all or name in required
                    else defaults.get(_type, None)
                )
                if column.default is None and not column.nullable:
                    default = ...
                fields[name] = (Optional[_type], default)

    fields = {k: v for (k, v) in fields.items() if not k.startswith("_")}

    if include:
        _includes = []
        item = include
        if not isinstance(item, dict):
            raise ValueError("Include incorrect type")
        item = _model_dict("include", item)
        _includes.append(item)
        include = ChainMap(*_includes)
        fields = {**fields, **include}
    new_model = create_model(
        f"{db_model.__name__} {model_name}",
        __config__=config,
        __validators__=validators,
        **fields,
    )
    return new_model
