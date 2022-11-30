"""
Result 스키마
"""
from typing import TypeVar, Generic, List

from pydantic import BaseModel, Json
from pydantic.generics import GenericModel


class ResultResponse(BaseModel):
    """
    Result schema
    """
    rs: str


class JsonResultResponse(BaseModel):
    """JSON Result schema"""
    rs: Json


T = TypeVar('T')


class PaginationResponse(GenericModel, Generic[T]):
    """
    Result schema
    """
    total: int
    items: List[T]
