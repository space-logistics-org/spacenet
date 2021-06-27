from typing import Union

from fastapi import Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database.api import database, models
from app.database.api.database import Base
from app.database.api.models.utilities import SCHEMA_TO_MODEL, dictify_row


def list_all(table, db):
    db_items = db.query(table).all()
    return db_items


def read_item(table, item_name, item_id, db):
    db_item = db.query(table).get(item_id)
    if db_item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No {item_name} found with id={item_id}",
        )
    return db_item


def create_item(item, db):
    db_item = SCHEMA_TO_MODEL[type(item)](**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def update_item(table, item_name, item_id, item, db):
    db_item = db.query(table).get(item_id)
    if db_item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No item found with id={item_id}",
        )
    if item.type != db_item.type:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"{item_name} found with id={item_id} is of type {db_item.type}; "
            f"cannot update type to {item.type} ",
        )
    for field_name, field in item.dict().items():
        if field_name != "type" and field is not None:
            setattr(db_item, field_name, field)
    db.commit()
    return db_item


def delete_item(table, item_name, item_id, db):
    db_item = db.query(table).get(item_id)
    if db_item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No {item_name} found with id={item_id}",
        )
    as_dict = dictify_row(db_item)
    db.delete(db_item)
    db.commit()
    return as_dict
