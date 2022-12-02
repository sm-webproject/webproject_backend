"""
보드 스키마
"""

from models.board import BoardModel
from schemas import make_schema_from_orm

Board = make_schema_from_orm(BoardModel, model_name="Board")
BoardGet = make_schema_from_orm(BoardModel, model_name="Board")
BoardCreate = make_schema_from_orm(BoardModel,
                                   model_name="BoardCreate",
                                   exclude=("board_id", "created_at", "updated_at"))
BoardUpdate = make_schema_from_orm(BoardModel, model_name="BoardUpdate",
                                   exclude=("board_id", "created_at", "updated_at"))
