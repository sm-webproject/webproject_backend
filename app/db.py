"""데이터베이스 설정"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from env import DB_ID, DB_PW, DB_URL, DB_PORT, DB_DB, DB_SCHEMA

SQLALCHEMY_DATABASE_URL = f'postgresql+pg8000://{DB_ID}:{DB_PW}@{DB_URL}:{DB_PORT}/{DB_DB}'

engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)
session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
Base.metadata.schema = DB_SCHEMA


def get_db():
    """db 객체 반환"""
    session = session_local()
    try:
        yield session
    except:
        session.rollback()
        raise
    finally:
        session.close()
