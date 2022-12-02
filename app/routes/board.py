import datetime

from fastapi import APIRouter, HTTPException
from fastapi_sqlalchemy import db

from models.board import BoardModel
from schemas.board import BoardCreate, BoardUpdate
from sqlalchemy.exc import IntegrityError

board_router = APIRouter(tags=["Boards"], prefix="/boards")


@board_router.get("", tags=["Boards"])
def get_board_all():
    data = db.session.query(BoardModel).all()
    return data


@board_router.post("", tags=["Boards"])
def create_board(payload: BoardCreate):
    added_model = BoardModel()
    added_model.writer = payload.writer
    added_model.content = payload.content
    added_model.title = payload.title

    try:
        db.session.add(added_model)
    except IntegrityError as e:
        raise HTTPException(402, e) from None
    db.session.commit()

    user = db.session.query(BoardModel).first()

    return user


@board_router.delete("/{board_id}", tags=["Boards"])
def create_board(board_id: str):
    board = db.session.query(BoardModel).filter(BoardModel.board_id == int(board_id)).one_or_none()
    print(board)
    if not board:
        return HTTPException(404, "there is no board in " + board_id)
    db.session.delete(board)
    db.session.commit()

    return True


@board_router.put("/{board_id}", tags=["Boards"])
def create_board(board_id: str, payload: BoardUpdate):
    board = db.session.query(BoardModel).filter(BoardModel.board_id == int(board_id)).one_or_none()
    print(board)
    if not board:
        return HTTPException(404, "there is no board in " + board_id)

    board.writer = payload.writer
    board.content = payload.content
    board.title = payload.title
    db.session.commit()
    db.session.refresh(board)

    return board


@board_router.get("/{board_id}", tags=["Boards"])
def create_board(board_id: str):
    board = db.session.query(BoardModel).filter(BoardModel.board_id == int(board_id)).one_or_none()
    if not board:
        return HTTPException(404, "there is no board in " + board_id)

    return board


