from enum import Enum, auto
from typing import List, Set

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing_extensions import Type

from .utilities import create_read_update_unions
from .. import database
from ..database import Base
from ..models.utilities import SCHEMA_TO_MODEL, dictify_row

NOT_FOUND_RESPONSE = {status.HTTP_404_NOT_FOUND: {"msg": str}}


class Route(Enum):
    GetAll = auto()
    GetOne = auto()
    Create = auto()
    Update = auto()
    Delete = auto()


class CRUDRouter(APIRouter):
    def __init__(
        self,
        table: Base,
        name_lower: str,
        name_capitalized: str,
        schemas: Set[Type],
        generated_routes: Set[Route] = None,
        prefix: str = "",
    ):
        super().__init__(prefix=prefix)
        self.table = table
        self.name_lower = name_lower
        self.name_capitalized = name_capitalized
        (
            self.create_schema,
            self.read_schema,
            self.update_schema,
        ) = create_read_update_unions(schemas)
        if generated_routes is None:
            generated_routes = {variant for variant in Route}
        if Route.GetAll in generated_routes:
            self.add_api_route(
                path="/",
                endpoint=self._read_all_items(),
                methods=["GET"],
                response_model=List[self.read_schema],
                summary=f"List {name_capitalized}s",
                description=f"List {name_lower}s currently in the database.",
            )
        if Route.GetOne in generated_routes:
            self.add_api_route(
                path="/{item_id}",
                endpoint=self._read_item(),
                methods=["GET"],
                response_model=self.read_schema,
                responses=NOT_FOUND_RESPONSE,
                summary=f"Read {name_capitalized}",
                description=f"Find a specific {name_lower} in the database.",
            )
        if Route.Create in generated_routes:
            self.add_api_route(
                path="/",
                endpoint=self._create_item(),
                methods=["POST"],
                response_model=self.read_schema,
                status_code=status.HTTP_201_CREATED,
                summary=f"Create {name_capitalized}",
                description=f"Add a new {name_lower} to the database.",
            )
        if Route.Update in generated_routes:
            self.add_api_route(
                path="/{item_id}",
                endpoint=self._update_item(),
                methods=["PATCH"],
                response_model=self.read_schema,
                responses={
                    **NOT_FOUND_RESPONSE,
                    status.HTTP_409_CONFLICT: {"msg": str},
                },
                summary=f"Update {name_capitalized}",
                description=f"Update an existing {name_lower} in the database.",
            )
        if Route.Delete in generated_routes:
            self.add_api_route(
                path="/{item_id}",
                endpoint=self._delete_item(),
                methods=["DELETE"],
                response_model=self.read_schema,
                responses=NOT_FOUND_RESPONSE,
                summary=f"Delete {name_capitalized}",
                description=f"Delete an existing {name_lower} from the database.",
            )

    def _read_all_items(self):
        def route(db: Session = Depends(database.get_db)):
            db_items = db.query(self.table).all()
            return db_items

        return route

    def _read_item(self):
        def route(item_id: int, db: Session = Depends(database.get_db)):
            db_item = db.query(self.table).get(item_id)
            if db_item is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"No {self.name_lower} found with id={item_id}",
                )
            return db_item

        return route

    def _create_item(self):
        create_schema = self.create_schema

        def route(item: create_schema, db: Session = Depends(database.get_db)):
            db_item = SCHEMA_TO_MODEL[type(item)](**item.dict())
            db.add(db_item)
            db.commit()
            db.refresh(db_item)
            return db_item

        return route

    def _update_item(self):
        update_schema = self.update_schema

        def route(
            item_id: int, item: update_schema, db: Session = Depends(database.get_db)
        ):
            db_item = db.query(self.table).get(item_id)
            if db_item is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"No item found with id={item_id}",
                )
            if item.type != db_item.type:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"{self.name_capitalized} found with id={item_id} is of type "
                    f"{db_item.type}; "
                    f"cannot update type to {item.type} ",
                )
            for field_name, field in item.dict().items():
                if field_name != "type" and field is not None:
                    setattr(db_item, field_name, field)
            db.commit()
            return db_item

        return route

    def _delete_item(self):
        def route(item_id: int, db: Session = Depends(database.get_db)):
            db_item = db.query(self.table).get(item_id)
            if db_item is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"No {self.name_lower} found with id={item_id}",
                )
            as_dict = dictify_row(db_item)
            db.delete(db_item)
            db.commit()
            return as_dict

        return route
