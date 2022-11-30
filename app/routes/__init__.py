"""유저 관련 api 모음"""
import inspect
from datetime import datetime, timezone
from typing import Optional, Any, List, Callable, Union, Coroutine, Type, Mapping

from fastapi import HTTPException, Request
from fastapi.param_functions import Depends, Query
from fastapi_crudrouter import SQLAlchemyCRUDRouter
from fastapi_crudrouter.core._base import NOT_FOUND
from fastapi_crudrouter.core._types import DEPENDENCIES, PYDANTIC_SCHEMA
from fastapi_crudrouter.core.databases import Model
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

import models
from db import get_db
from schemas.response import PaginationResponse
from utils.db_util import paginate, parse_filter, ModelFilter


class FilterSQLAlchemyCRUDRouter(SQLAlchemyCRUDRouter):
    """
    filter 추가 Router
    """

    # pylint: disable=too-many-arguments, redefined-outer-name, too-many-instance-attributes
    def __init__(
            self,
            schema: Type[PYDANTIC_SCHEMA],  # Response 스키마
            db_model: Type[Model],  # 대상 db_model
            get_all_schema: Optional[Type[PYDANTIC_SCHEMA]] = None,  # Get All 반환 스키마
            create_schema: Optional[Type[PYDANTIC_SCHEMA]] = None,  # Create Body 스키마
            update_schema: Optional[Type[PYDANTIC_SCHEMA]] = None,  # Update Body 스키마
            prefix: Optional[str] = None,  # URL 접두사
            tags: Optional[List[str]] = None,  # Swagger Tag
            paginate: Optional[int] = None,  # 기본 페이지네이션 숫자
            get_all_route: Union[bool, DEPENDENCIES] = True,  # Get All Depend 혹은 사용 여부
            get_one_route: Union[bool, DEPENDENCIES] = True,  # Get One Depend 혹은 사용 여부
            create_route: Union[bool, DEPENDENCIES] = True,  # Create Depend 혹은 사용 여부
            update_route: Union[bool, DEPENDENCIES] = True,  # Update Depend 혹은 사용 여부
            delete_one_route: Union[bool, DEPENDENCIES] = True,  # Delete One Depend 혹은 사용 여부
            get_all_convert_schema: Optional[Type] = None,  # Get All 에서 convert 한 결과 스키마
            get_one_convert_schema: Optional[Type] = None,  # Get One 에서 convert 한 결과 스키마
            get_all_route_convert: Optional[Callable[[Model], Any]] = None,  # Get All 에서 convert 함수
            get_one_route_convert: Optional[Callable[[Model], Any]] = None,  # Get One 에서 convert 함수
            get_all_route_complete: Optional[Callable[[Request], Any]] = None,  # Get All 성공 콜백
            get_one_route_complete: Optional[Callable[[Request], Any]] = None,  # Get One 성공 콜백
            create_route_complete: Optional[Callable[[Request], Any]] = None,  # Create 성공 콜백
            update_route_complete: Optional[Callable[[Request], Any]] = None,  # Update 성공 콜백
            delete_one_route_complete: Optional[Callable[[Request], Any]] = None,
            # Delete One 성공 콜백
            delete_all_route: Union[bool, DEPENDENCIES] = False,
            get_filter_from_path_params: Optional[List[str]] = None,
            include_path_params_to_create_schema: Optional[List[str]] = None,
            **kwargs: Any
    ) -> None:
        # model convert
        self.get_all_route_convert = get_all_route_convert
        # convert 가 있을 경우 convert schema 는 필수
        if get_all_route_convert and get_all_convert_schema is None:
            raise RuntimeError(
                "get_all_convert_schema is required, if add get_all_route_convert to FilterSQLAlchemyCRUDRouter")
        self.get_one_route_convert = get_one_route_convert
        if get_one_route_convert and get_one_convert_schema is None:
            raise RuntimeError(
                "get_all_convert_schema is required, if add get_all_route_convert to FilterSQLAlchemyCRUDRouter")

        self.get_all_schema = get_all_convert_schema if get_all_convert_schema else (
            get_all_schema if get_all_schema else schema)
        self.get_one_schema = get_one_convert_schema if get_one_convert_schema else schema
        self.get_filter_from_path_params = get_filter_from_path_params
        if self.get_filter_from_path_params:
            for param in self.get_filter_from_path_params:
                if param not in prefix:
                    raise RuntimeError(
                        f"\'{param}\' is not in prefix, can't load path parameter."
                        f"Check \'get_filter_from_path_params\' param")
        self.include_path_params_to_create_schema = include_path_params_to_create_schema
        if self.include_path_params_to_create_schema:
            for param in self.include_path_params_to_create_schema:
                if param not in prefix:
                    raise RuntimeError(
                        f"\'{param}\' is not in prefix, can't load path parameter."
                        f"Check \'include_path_params_to_create_schema\' param")
        self.get_all_route_complete = get_all_route_complete
        self.get_one_route_complete = get_one_route_complete
        self.create_route_complete = create_route_complete
        self.update_route_complete = update_route_complete
        self.delete_one_route_complete = delete_one_route_complete
        super().__init__(
            schema=schema,
            create_schema=create_schema,
            update_schema=update_schema,
            prefix=prefix or db_model.__tablename__,
            db=get_db,
            db_model=db_model,
            tags=tags,
            paginate=paginate,
            get_all_route=get_all_route,
            get_one_route=get_one_route,
            create_route=create_route,
            update_route=update_route,
            delete_one_route=delete_one_route,
            delete_all_route=delete_all_route,
            **kwargs
        )

    def _get_filter_list(self, request: Request, db: Session, item_id: str) -> Model:
        filter_list = ModelFilter(self.db_model,
                                  self.db_model.__table__.primary_key.columns.keys()[0], '==',
                                  item_id).get_filter()

        if self.get_filter_from_path_params is not None:
            filter_str = ''
            for param in self.get_filter_from_path_params:
                filter_str += param + "==" + request.path_params[
                    param] + ","
            filters_info = parse_filter(filter_str)
            for filter_ in filters_info:
                filter_list &= ModelFilter(self.db_model, filter_.column, filter_.comp_operator,
                                           filter_.value).get_filter()
        model: Model = db.query(self.db_model).filter(filter_list).first()

        if not model:
            raise NOT_FOUND

        return model

    def _get_all(self, *args: Any, **kwargs: Any) -> Callable[
        [Optional[str], str, int, Optional[int]], Coroutine[Any, Any, PaginationResponse]]:
        async def route(
                request: Request,
                order_by: Optional[str] = Query(None, description="정렬 대상 칼럼"),
                filter_list: str = Query("",
                                         description="==(일치), !=(불일치), >=, <=, >, <, ~= (포함 '%검색어%')"),
                page: int = Query(1, description="1 이상 설정 요구"),
                limit: Optional[int] = Query(None, description="값이 없을 경우 전체 반환"),
        ) -> PaginationResponse:
            if self.get_filter_from_path_params is not None:
                filter_list += ","
                for param in self.get_filter_from_path_params:
                    filter_list += param + "==" + request.path_params[
                        param] + ","

            res = paginate(self.db_model, page, limit, filter_list, order_by)
            if self.get_all_route_complete is not None:
                self.get_all_route_complete(request)

            # 모델 컨버터
            if self.get_all_route_convert is not None:
                res['items'] = list(map(self.get_all_route_convert, res['items']))

            return res

        return self.create_route_functon(route)

    def _get_one(self, *args: Any, **kwargs: Any):
        async def route(
                request: Request,
                item_id: str, db: Session = Depends(self.db_func)  # type: ignore
        ) -> Model:
            """
            한개 얻기
            """
            model = self._get_filter_list(request, db, item_id)

            # 모델 컨버터
            if self.get_one_route_convert is not None:
                model = self.get_one_route_convert(model)

            if self.get_one_route_complete is not None:
                self.get_one_route_complete(request)
            return model

        return self.create_route_functon(route)

    def _create(self, *args: Any, **kwargs: Any):
        async def route(
                request: Request,
                model: self.create_schema,  # type: ignore
                db: Session = Depends(self.db_func),
        ) -> Model:
            """
            생성
            """
            try:
                if self.include_path_params_to_create_schema:
                    added_model = model.dict()
                    for include_schema in self.include_path_params_to_create_schema:
                        added_model[include_schema] = request.path_params[
                            include_schema] if include_schema in request.path_params else None
                    db_model: Model = self.db_model(**added_model)
                else:
                    db_model: Model = self.db_model(**model.dict())
                db.add(db_model)
                db.commit()
                db.refresh(db_model)
                if self.create_route_complete is not None:
                    self.create_route_complete(request)
                return db_model
            except IntegrityError:
                db.rollback()
                raise HTTPException(422, "Key already exists") from None

        return self.create_route_functon(route)

    def _update(self, *args: Any, **kwargs: Any) -> Callable[..., Model]:
        async def route(
                request: Request,
                item_id: str,  # type: ignore
                body: self.update_schema,  # type: ignore
                db: Session = Depends(self.db_func),
        ) -> Model:
            """
            수정
            """
            try:
                pk = self.db_model.__table__.primary_key.columns.keys()[0]
                model = self._get_filter_list(request, db, item_id)

                if issubclass(model.__class__, models.DeleteTimeModel):
                    if model.deleted_at is not None:
                        raise HTTPException(status_code=400, detail="Already deleted item")

                for key, value in body.dict(exclude={pk}).items():
                    if hasattr(model, key):
                        setattr(model, key, value)

                db.commit()
                db.refresh(model)
                if self.update_route_complete is not None:
                    self.update_route_complete(request)
                return model
            except IntegrityError as error:
                db.rollback()
                self._raise(error)

        return self.create_route_functon(route)

    def _delete_one(self, *args: Any, **kwargs: Any) -> Callable[
        [Request, str, Session], Coroutine[Any, Any, Mapping[Any, Any]]]:
        async def route(
                request: Request,
                item_id: str, db: Session = Depends(self.db_func)  # type: ignore
        ) -> Model:
            model = self._get_filter_list(request, db, item_id)

            if issubclass(model.__class__, models.DeleteTimeModel):
                if model.deleted_at is not None:
                    raise HTTPException(status_code=400, detail="Already deleted item")
                model.deleted_at = datetime.now(tz=timezone.utc)
            else:
                db.delete(model)
            db.commit()
            if self.delete_one_route_complete is not None:
                self.delete_one_route_complete(request)

            return model

        return self.create_route_functon(route)

    def _add_api_route(
            self,
            path: str,
            endpoint: Callable[..., Any],
            dependencies: Union[bool, DEPENDENCIES],
            error_responses: Optional[List[HTTPException]] = None,
            **kwargs: Any,
    ) -> None:
        if kwargs['summary'] == 'Get All':
            kwargs['response_model'] = PaginationResponse[self.get_all_schema]
        if kwargs['summary'] == 'Get One':
            kwargs['response_model'] = self.get_one_schema
        dependencies = [] if isinstance(dependencies, bool) else dependencies
        responses: Any = (
            {err.status_code: {"detail": err.detail} for err in error_responses}
            if error_responses
            else None
        )

        super().add_api_route(
            path, endpoint, dependencies=dependencies, responses=responses, **kwargs
        )

    def create_route_functon(self, route):
        """
        함수 생성
        """
        pa_list = ["request: Request"]
        if self.get_filter_from_path_params:
            for filter_entry in self.get_filter_from_path_params:
                pa_list.append(filter_entry + ": str")
        fun = inspect.getsource(route)
        fun = fun.replace("def route", "def new_route")
        fun = fun.replace("request: Request,", ",".join(pa_list) + ",")
        fun = fun.replace("\n        ", "\n")
        fun = fun.replace("        async def new_route", "async def new_route")
        local_dict = {**globals(), 'self': self}
        # pylint: disable=exec-used
        exec(fun, local_dict)
        return local_dict['new_route']
