"""User Model"""
from sqlalchemy import Column, String, Integer
from sqlalchemy_utils import PasswordType

from db import Base
from models import TimeModel, DeleteTimeModel


class UserModel(Base, TimeModel, DeleteTimeModel):
    """
    유저 모델
    """
    __tablename__ = 'user'

    username: Column = Column(String(32), primary_key=True)
    password: Column = Column(PasswordType(schemes=[
        'pbkdf2_sha512',
        'md5_crypt'
    ], deprecated=['md5_crypt']), nullable=False)
    name: Column = Column(String(32), nullable=False)
    tier: Column = Column(Integer, nullable=False)
    phone: Column = Column(String(16), nullable=False)
    email: Column = Column(String(64), nullable=False)
