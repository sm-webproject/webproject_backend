"""환경 변수 설정 및 정의"""
import os

from dotenv import load_dotenv

load_dotenv(verbose=True)

STAGE = os.getenv('STAGE')
DB_URL = os.getenv('DB_URL')
DB_PORT = os.getenv('DB_PORT')
DB_ID = os.getenv('DB_ID')
DB_PW = os.getenv('DB_PW')
DB_DB = os.getenv('DB_DB')
DB_SCHEMA = os.getenv('DB_SCHEMA')
AWS_ACCESS_KEY_ID = os.getenv('ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('SECRET_ACCESS_KEY')
AWS_S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME')
