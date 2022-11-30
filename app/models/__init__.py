"""
DB Base Model
"""

from sqlalchemy import Column, func, DateTime


class TimeModel:
    """
    모델에 기본적으로 넣어야 하는 시간 Column
    """
    created_at: Column = Column(DateTime(timezone=True), nullable=False, default=func.now())
    updated_at: Column = Column(DateTime(timezone=True), onupdate=func.now())


class DeleteTimeModel:
    """
    db에서 직접 삭제를 하면 안되는 테이블에서 사용되는 Column
    """
    deleted_at: Column = Column(DateTime(timezone=True))


class ExpiredTimeModel:
    """
    만기 시점을 일러주는 Column
    """
    expired_at: Column = Column(DateTime(timezone=True))
