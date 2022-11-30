"""유저 관련 api 모음"""
from fastapi import APIRouter, Depends, Body
from fastapi import HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_sqlalchemy import db

from models.user import UserModel
from routes import FilterSQLAlchemyCRUDRouter
from schemas.user import UserCreate, UserUpdate, UserGet, SigninResponse, RefreshRequest
from utils.auth_util import create_jwt_token, get_user, create_jwt_token_refresh, decode_jwt_token, get_token_expire_at, \
    get_refresh_token_expire_at

user_router = APIRouter(tags=["Users"])

user_router.include_router(
    FilterSQLAlchemyCRUDRouter(schema=UserGet, create_schema=UserCreate,
                               db_model=UserModel,
                               prefix='/users',
                               dependencies=[Depends(get_user)],
                               delete_all_route=False, update_schema=UserUpdate, paginate=20))


def complete(request: Request):
    """
    get all 추가 코드
    """
    print(request)
    print('Complete get all')


user_router.include_router(
    FilterSQLAlchemyCRUDRouter(schema=UserGet, create_schema=UserCreate,
                               db_model=UserModel,
                               prefix='/test/{name}',
                               tags=['Users'],
                               # name_data 경로 매개 변수를 name 칼럼에 필터링
                               get_filter_from_path_params=['name'],
                               # get_all 이 완료 되었을 때 호출
                               get_all_route_complete=complete,
                               delete_all_route=False, update_schema=UserUpdate, paginate=20))


@user_router.get("/me", response_model=UserGet, tags=["Users"], )
def me(user: UserModel = Depends(get_user)):
    """
    현재 자신의 정보
    """

    return user


@user_router.post("/signin", response_model=SigninResponse)
def signin(form: OAuth2PasswordRequestForm = Depends()):
    """
    로그인
    """
    user: UserModel = db.session.query(UserModel).filter(
        (UserModel.username == form.username)).first()

    if not user or user.deleted_at is not None:
        raise HTTPException(status_code=404,
                            detail='User is not found')

    if user.password != form.password:
        raise HTTPException(status_code=401,
                            detail='Password is wrong')
    return {"access_token": create_jwt_token({
        "username": user.username
    }), "refresh_token": create_jwt_token_refresh({
        "username": user.username,
        "refresh": True
    }), "token_type": "bearer",
        "access_token_expire_at": get_token_expire_at().isoformat(),
        "refresh_token_expire_at": get_refresh_token_expire_at().isoformat()
    }


@user_router.post("/refresh", response_model=SigninResponse)
def refresh_token(refresh: RefreshRequest = Body(...)):
    """
    토큰 재발급
    """
    jwt = decode_jwt_token(refresh.token)

    if not ('refresh' in jwt and jwt['refresh']):
        raise HTTPException(status_code=400,
                            detail='Token is not refresh token')

    user: UserModel = db.session.query(UserModel).filter(
        (UserModel.username == jwt['username'])).first()

    if not user or user.deleted_at is not None:
        raise HTTPException(status_code=404,
                            detail='User is not found')

    return {"access_token": create_jwt_token({
        "username": user.username
    }), "refresh_token": create_jwt_token_refresh({
        "username": user.username,
        "refresh": True
    }), "token_type": "bearer",
        "access_token_expire_at": get_token_expire_at().isoformat(),
        "refresh_token_expire_at": get_refresh_token_expire_at().isoformat()
    }
