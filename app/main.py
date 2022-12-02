"""
메인
"""

import alembic.command
from alembic.config import Config
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from fastapi_sqlalchemy import DBSessionMiddleware
from mangum import Mangum
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.gzip import GZipMiddleware

from db import SQLALCHEMY_DATABASE_URL
from env import STAGE
from routes.board import board_router
from routes.user import user_router

app = FastAPI(title="데브파이브", description="데브파이브 백엔드",
              root_path=("/" + STAGE) if STAGE != "local" else "/",
              openapi_url=None if STAGE == "prod" else "/openapi.json", debug=STAGE != "prod")


def custom_openapi():
    """
    access_token 을 accessToken 으로 바꾸기 위한 custom openapi
    """
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
        servers=[{
            'url': ("/" + STAGE) if STAGE != "local" else "/"
        }]
    )
    openapi_schema["components"]["securitySchemes"]["OAuth2PasswordBearer"]["x-tokenName"] = "accessToken"
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi

app.add_middleware(GZipMiddleware, minimum_size=1000)


@app.on_event('startup')
def startup():
    """
    SQL 모델 동기화
    """
    config = Config('alembic.ini')
    alembic.command.upgrade(config, 'head')


app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://localhost",
                   "http://localhost",
                   "https://localhost:3000",
                   "http://localhost:3000",
                   "http://maeneung.iptime.org:3000",
                   "http://maeneung.iptime.org"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(DBSessionMiddleware,
                   db_url=SQLALCHEMY_DATABASE_URL)

app.include_router(user_router)
app.include_router(board_router)


@app.get("/")
async def root():
    """
    root
    """
    return "Devfive api server"


handler = Mangum(app)
