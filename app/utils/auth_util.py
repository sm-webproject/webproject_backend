"""
jwt 발급, 확인
"""
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from fastapi_sqlalchemy import db
from sqlalchemy import func, column

from models.user import UserModel

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="signin")


def decode_jwt_token(jwt_token: str):
    """
    jwt 확인
    """
    try:
        decoded_jwt = jwt.decode(jwt_token, "devfive_key", algorithms="HS256")
        return decoded_jwt
    except jwt.exceptions.ExpiredSignatureError as error:
        raise HTTPException(status_code=401, detail="login token is expired") from error
    except jwt.exceptions.DecodeError as error:
        raise HTTPException(status_code=400, detail="token has problem") from error


def decode_jwt_token_and_check_admin(permission_id: str, jwt_token: str):
    """
    jwt 확인 후 어드민 인지 확인
    """
    decoded_jwt = decode_jwt_token(jwt_token)
    if 'admin' in permission_id and decoded_jwt['tier'] == 1:
        raise HTTPException(status_code=403, detail="client can't access")
    return decoded_jwt


def get_token_expire_at():
    """
    get token expire at
    """
    return datetime.now(tz=timezone.utc) + timedelta(minutes=360)


def get_refresh_token_expire_at():
    """
    get refresh token expire at
    """
    return datetime.now(tz=timezone.utc) + timedelta(hours=100)


def create_jwt_token(data: dict):
    """
    jwt 생성
    """
    data['exp'] = get_token_expire_at()
    data['iat'] = datetime.now(tz=timezone.utc)
    encoded_jwt = jwt.encode(payload=data, key="devfive_key", algorithm="HS256")
    return encoded_jwt


def create_jwt_token_refresh(data: dict):
    """
    refresh jwt 생성
    """
    data['exp'] = get_refresh_token_expire_at()
    data['iat'] = datetime.now(tz=timezone.utc)
    encoded_jwt = jwt.encode(payload=data, key="devfive_key", algorithm="HS256")
    return encoded_jwt


def get_user(jwt_token: str = Depends(oauth2_scheme)):
    """
    jwt 확인
    """
    decoded_jwt = decode_jwt_token(jwt_token)

    user = db.session.query(UserModel).filter(
        (UserModel.username == decoded_jwt['username'])
        & UserModel.deleted_at.is_(None)).one_or_none()
    if not user:
        raise HTTPException(status_code=400, detail="user not found")
    return user


def get_user_with_permission(permission_id: str, jwt_token: str = Depends(oauth2_scheme)):
    """
    jwt 로 권한 확인
    """
    decoded_jwt = decode_jwt_token_and_check_admin(permission_id, jwt_token)
    regex = create_regex(permission_id)
    user = db.session.query(UserModel).select_from(func.unnest(UserModel.permissions)
                                                   .alias("per")).filter(
        (UserModel.username == decoded_jwt['username']) & (column("per").op("~")(regex))).all()
    return user[0] if user else None


def check_permission(permission_id: str):
    """
    check user can assess to permission
    """

    def check_auth(jwt_token: str = Depends(oauth2_scheme)):
        user = get_user_with_permission(permission_id, jwt_token)
        if not user:
            raise HTTPException(status_code=403,
                                detail="user can't access to permission , need permission : " + str(
                                    permission_id))

    return check_auth


def check_permission_and_user(permission_client: str = None,
                              permission_admin: str = None):
    """
    if user_id == token check client permission
    else check admin permission
    """

    def check_auth(user_id: str, jwt_token: str = Depends(oauth2_scheme)):
        decoded_jwt = decode_jwt_token(jwt_token)
        if permission_client is None and user_id == decoded_jwt['username']:
            return
        regex = create_regex(permission_client) if user_id == decoded_jwt['username'] else \
            create_regex(permission_admin)
        user = db.session.query(UserModel).select_from(func.unnest(UserModel.permissions)
                                                       .alias("per")).filter(
            (UserModel.username == decoded_jwt['username']) & (column("per").op("~")(regex))).all()
        if not user:
            raise HTTPException(status_code=403,
                                detail="user can't access to permission , need permission : "
                                       + (str(permission_client) if user_id ==
                                                                    decoded_jwt['username'] else
                                          str(permission_admin)))

    return check_auth


def create_regex(permission: str):
    """
    regex로 정제하는 메소드
    """
    permission_list = permission.split('.')
    regex = '^'
    for i in permission_list:
        regex += f"({i}[.]"
    regex = regex[:-3]
    regex += '$'
    for _ in range(len(permission_list)):
        regex += r'|\*$)'
    return regex
