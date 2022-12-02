"""User Model"""
from sqlalchemy import Column, String, Integer

from db import Base
from models import TimeModel


class BoardModel(Base, TimeModel):
    """
    보드 모델
    """
    __tablename__ = 'board'

    board_id: Column = Column(Integer, autoincrement=True, primary_key=True )
    writer: Column = Column(String(32), nullable=False)
    content: Column = Column(String(32), nullable=False)
    title: Column = Column(String(32), nullable=False)
