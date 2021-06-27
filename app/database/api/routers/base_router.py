from enum import Enum, auto
from typing import Callable, List, Set

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing_extensions import Type

from app.database.api import database
from app.database.api.database import Base
from app.database.api.models.utilities import SCHEMA_TO_MODEL, dictify_row
from app.database.api.routers.utilities import create_read_update_unions

NOT_FOUND_RESPONSE = {status.HTTP_404_NOT_FOUND: {"msg": str}}
TYPE_CONFLICT_RESPONSE = {status.HTTP_409_CONFLICT: {"msg": str}}


class Routes(Enum):
    GetOne = (auto(),)
    GetAll = (auto(),)
    Create = (auto(),)
    Patch = (auto(),)
    DeleteOne = (auto(),)


def not_found_error(object_name: str, id_: int) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"{object_name} with id={id_} not found",
    )


def type_conflict_error(object_name, id_, stored_type, new_type) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail=f"{object_name} found with id={id_} is of type {stored_type};"
        f"cannot update type to {new_type}",
    )


class CRUDRouter(APIRouter):
    def __init__(
        self,
        name: str,
        all_schemas: Set[Type[BaseModel]],
        table: Base,
        generated_routes: Set[Routes] = None,
        authentication_required: Set[Routes] = None,
    ):
        super().__init__()
        if generated_routes is None:
            generated_routes = {variant for variant in Routes}
        if authentication_required is None:
            authentication_required = set()
        assert authentication_required.issubset(
            generated_routes
        ), "Cannot require authentication for routes which are not generated"
        (
            self.create_schemas,
            self.read_schemas,
            self.update_schemas,
        ) = create_read_update_unions(all_schemas)
        self.table = table
        self.object_name = name
        if Routes.GetAll in generated_routes:
            self.add_api_route(
                "",
                self._get_all(),
                methods=["GET"],
                response_model=List[self.read_schemas],
                description=f"List the {name.lower()}s currently in the database.",
            )
        if Routes.GetOne in generated_routes:
            self.add_api_route(
                "",
                self._get_one(),
                methods=["GET"],
                response_model=self.read_schemas,
                responses=NOT_FOUND_RESPONSE,
                description=f"Find a specific {name.lower()} in the database.",
            )
        if Routes.Create in generated_routes:
            self.add_api_route(
                "",
                self._create(),
                methods=["POST"],
                status_code=status.HTTP_201_CREATED,
                response_model=self.read_schemas,
                description=f"Add a new {name.lower()} to the database.",
            )
        if Routes.Patch in generated_routes:
            self.add_api_route(
                "",
                self._patch(),
                methods=["PATCH"],
                response_model=self.read_schemas,
                responses={**NOT_FOUND_RESPONSE, **TYPE_CONFLICT_RESPONSE},
                description=f"Update an existing {name.lower()} in the database.",
            )
        if Routes.DeleteOne in generated_routes:
            self.add_api_route(
                "",
                self._delete(),
                methods=["DELETE"],
                response_model=self.read_schemas,
                responses=NOT_FOUND_RESPONSE,
                description=f"Delete an {name.lower()} from the database.",
            )

    def _get_all(self) -> Callable[..., List[BaseModel]]:
        def route(
            db: Session = Depends(database.get_db)
        ):
            db_objects = db.query(self.table)
            return db_objects

        return route

    def _get_one(self) -> Callable[..., BaseModel]:
        def route(id_: int, db: Session = Depends(database.get_db)):
            db_object = db.query(self.table).get(id_)
            if db_object is None:
                raise not_found_error(self.object_name, id_)
            return db_object

        return route

    def _create(self) -> Callable[..., BaseModel]:
        create_schemas = self.create_schemas

        def route(obj: create_schemas, db: Session = Depends(database.get_db)):
            db_object = SCHEMA_TO_MODEL[type(obj)](**obj.dict())
            db.add(db_object)
            db.commit()
            db.refresh(db_object)
            return db_object

        return route

    def _patch(self) -> Callable[..., BaseModel]:
        update_schemas = self.update_schemas

        def route(
            id_: int, obj: update_schemas, db: Session = Depends(database.get_db)
        ):
            db_obj = db.query(self.table).get(id_)
            if db_obj is None:
                raise not_found_error(self.object_name, id_)
            if db_obj.type != obj.type:
                raise type_conflict_error(
                    self.object_name, id_, stored_type=db_obj.type, new_type=obj.type
                )
            for attr, value in obj.dict().items():
                if attr != "type" and value is not None:
                    setattr(db_obj, attr, value)
            db.commit()
            return db_obj

        return route

    def _delete(self) -> Callable[..., BaseModel]:
        def route(id_: int, db: Session = Depends(database.get_db)):
            db_obj = db.query(self.table).get(id_)
            if db_obj is None:
                raise not_found_error(self.object_name, id_)
            as_dict = dictify_row(db_obj)
            db.delete(db_obj)
            db.commit()
            return as_dict

        return route
