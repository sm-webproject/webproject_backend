"""
유저 스키마
"""

from fastapi_camelcase import CamelModel
from pydantic.fields import Field

from models.user import UserModel
from schemas import make_schema_from_orm

User = make_schema_from_orm(UserModel, model_name="User")
UserGet = make_schema_from_orm(UserModel, model_name="User", exclude=tuple(["password"]))
UserCreate = make_schema_from_orm(UserModel,
                                  model_name="UserCreate",
                                  exclude=("created_at", "updated_at", "deleted_at"))
UserUpdate = make_schema_from_orm(UserModel, model_name="UserUpdate",
                                  exclude=("created_at", "updated_at", "username",
                                           "deleted_at", "password"))


class SigninResponse(CamelModel):
    """
    JWT Signin Response
    """
    access_token: str = Field(..., description="JWT Access Token")
    refresh_token: str = Field(..., description="JWT Refresh Token")
    token_type: str = Field(..., description="Token Type")
    access_token_expire_at: str = Field(..., description="JWT Access Token expire ISO datetime")
    refresh_token_expire_at: str = Field(..., description="JWT Refresh Token expire ISO datetime")


class RefreshRequest(CamelModel):
    """
    JWT Token Refresh Request
    """
    token: str = Field(..., description="JWT Access Token")
