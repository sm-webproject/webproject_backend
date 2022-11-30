"""
db utils
"""
import operator
import re
from typing import Optional, Type

from fastapi import HTTPException
from fastapi_sqlalchemy import db
from pydantic import BaseModel

from db import Base

operators = {"<": operator.lt, "<=": operator.le, "==": operator.eq, ">=": operator.ge,
             ">": operator.gt, "!=": operator.ne}


class ModelFilter:
    """
    create model filter
    """

    def __init__(self, model: Type[Base], column: str, comp_operator: str, value: str):
        self.model = model
        self.column = re.sub(r'(?<!^)(?=[A-Z])', '_', column).lower()
        self.value = value
        self.comp_operator = comp_operator

    def get_filter(self):
        """
        get filter
        """
        try:
            field = getattr(self.model, self.column)

            if self.comp_operator == "~=":
                return field.like(self.value)

            filter_ = operators[self.comp_operator](field,
                                                    None if self.value.lower() in ["null", "none"]
                                                    else self.value)
        except AttributeError as error:
            raise HTTPException(status_code=400,
                                detail=f'{self.model} table doesn\'t has {self.column} property') \
                from error
        return filter_


class ModelFilterGet(BaseModel):
    """
    get model filter
    """
    column: str
    comp_operator: str
    value: str


def paginate(model: Type[Base], page: int, limit: int, filters_info: Optional[str],
             order_by: Optional[str]):
    """
    paginate
    """
    main_query = db.session.query(model)

    if filters_info:
        filters_info = parse_filter(filters_info)
        filter_list = None
        for filter_ in filters_info:
            if filter_list is None:
                filter_list = ModelFilter(model, filter_.column, filter_.comp_operator,
                                          filter_.value).get_filter()
            else:
                filter_list &= ModelFilter(model, filter_.column, filter_.comp_operator,
                                           filter_.value).get_filter()
        if filter_list is not None:
            main_query = main_query.filter(filter_list)

    if order_by:
        order_by = re.sub(r'(?<!^)(?=[A-Z])', '_', order_by).lower()
        try:
            main_query = main_query.order_by(getattr(model, order_by).desc())
        except AttributeError as error:
            raise HTTPException(status_code=400,
                                detail=f'{model} table doesn\'t has {order_by} property') from error
    try:
        items = main_query.offset(limit * (page - 1)).limit(limit).all() if page and limit else main_query.all()
        total = main_query.count()
        return {"items": items, "total": total}
    except Exception:
        # pylint: disable=raise-missing-from
        raise HTTPException(status_code=400,
                            detail='Query runtime error')


def parse_filter(filter_list: Optional[str]):
    """
    필터 파싱
    """
    if filter_list is not None:
        filter_res = []
        filter_list = filter_list.split(",")
        for filter_ in filter_list:
            if not filter_:
                continue
            parsed_str = re.split('(<|<=|==|!=|>=|>|~=)', filter_)

            if len(parsed_str) < 3:
                raise HTTPException(status_code=400,
                                    detail=f'"{filter_}" query has Syntax Error')

            if not parsed_str[2]:
                continue
            parsed_class = ModelFilterGet(column=parsed_str[0], comp_operator=parsed_str[1],
                                          value=parsed_str[2])
            filter_res.append(parsed_class)
        return filter_res
    return None
