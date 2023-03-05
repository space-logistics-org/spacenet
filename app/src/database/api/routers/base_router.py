"""
This module defines a default class for CRUD routes that can be imported and used for individual schema.
"""

from enum import Enum, auto
from typing import List, Optional, Set

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing_extensions import Type

from .utilities import create_read_update_unions
from .. import database
from ..database import Base
from ..models.utilities import SCHEMA_TO_MODEL, dictify_row
from ....auth_dependencies import User, current_user

NOT_FOUND_RESPONSE = {404: {"msg": str}}

__all__ = ["Route", "CRUDRouter"]


class Route(Enum):
    """
    An enumeration of the supported API route types.
    """
    GetAll = auto()
    GetOne = auto()
    Create = auto()
    Update = auto()
    Delete = auto()


class CRUDRouter(APIRouter):
    """
    A router which, once instantiated, supports some routes by default.
    """

    def __init__(
        self,
        table: Base,
        name: str,
        schemas: Set[Type[BaseModel]],
        generated_routes: Optional[Set[Route]] = None,
        prefix: str = "",
    ):
        """
        Construct a new router which automatically generates and provides CRUD routes.

        :param table: database table which are used to store the created values
        :param name: lowercase name of the items being stored
        :param schemas: all the schemas corresponding to the items being stored
        :param generated_routes: set of routes the constructed router is to support;
                if not provided, all routes enumerated by Route will be generated
        :param prefix: the prefix all routes for this router are to be accessed with;
                defaults to no prefix

        The provided router accesses and inserts into ``table``, concerning items
        with a lower-case name of ``name_lower``, and an upper-case name of
        ``name_capitalized``. The provided schemas in ``schemas`` correspond to all,
        and exclusively, the items, with a Create, Read, and Update schema, all of which must
        exist in ``CREATE_SCHEMA``, ``UPDATE_SCHEMA``, and ``READ_SCHEMA``, which are defined
        in the ``constants`` module of ``database/api``.
        """
        super().__init__(prefix=prefix)
        self.table = table
        self.name_lower = name
        name_cap = " ".join(w.capitalize() for w in name.split())
        self.name_cap = name_cap
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
                endpoint=self.get_read_all_items(),
                methods=["GET"],
                response_model=List[self.read_schema],
                summary=f"List {name_cap}s",
                description=f"List {name}s currently in the database.",
            )
        if Route.GetOne in generated_routes:
            self.add_api_route(
                path="/{item_id}",
                endpoint=self.get_read_item(),
                methods=["GET"],
                response_model=self.read_schema,
                summary=f"Read {name_cap}",
                description=f"Find a specific {name} in the database.",
            )
        if Route.Create in generated_routes:
            self.add_api_route(
                path="/",
                endpoint=self.get_create_item(),
                methods=["POST"],
                response_model=self.read_schema,
                status_code=status.HTTP_201_CREATED,
                summary=f"Create {name_cap}",
                description=f"Add a new {name} to the database.",
            )
        if Route.Update in generated_routes:
            self.add_api_route(
                path="/{item_id}",
                endpoint=self.get_update_item(),
                methods=["PATCH"],
                response_model=self.read_schema,
                summary=f"Update {name_cap}",
                description=f"Update an existing {name} in the database.",
            )
        if Route.Delete in generated_routes:
            self.add_api_route(
                path="/{item_id}",
                endpoint=self.get_delete_item(),
                methods=["DELETE"],
                response_model=self.read_schema,
                summary=f"Delete {name_cap}",
                description=f"Delete an existing {name} from the database.",
            )

    def get_read_all_items(self):
        """
        :return: a route retrieving all items in the backing table
        """
        def _route(db: Session = Depends(database.get_db)):
            db_items = db.query(self.table).all()
            return db_items

        return _route

    def get_read_item(self):
        """
        :return: a route retrieving the single item present in the backing table with the given
                id, or raising a 404 error if not present
        """
        def _route(item_id: int, db: Session = Depends(database.get_db)):
            db_item = db.query(self.table).get(item_id)
            if db_item is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"No {self.name_lower} found with id={item_id}",
                )
            return db_item

        return _route

    def get_create_item(self):
        """
        :return: a route creating an item in the backing table
        """
        CreateSchema = self.create_schema

        def _route(
            item: CreateSchema,
            db: Session = Depends(database.get_db),
            _user: User = Depends(current_user),
        ):
            db_item = SCHEMA_TO_MODEL[type(item)](**item.dict())
            db.add(db_item)
            db.commit()
            db.refresh(db_item)
            return db_item

        return _route

    def get_update_item(self):
        """
        :return: a route modifying an item in the backing table with the given id, raising a
                404 error if not present or a 409 error if the update would change the type of
                the item
        """
        UpdateSchema = self.update_schema

        def _route(
            item_id: int,
            item: UpdateSchema,
            db: Session = Depends(database.get_db),
            _user: User = Depends(current_user),
        ):
            db_item = db.query(self.table).get(item_id)
            if db_item is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"No item found with id={item_id}",
                )
            if hasattr(item, "type"):
                if item.type != db_item.type:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail=f"{self.name_cap} found with id={item_id} is of type "
                        f"{db_item.type}; "
                        f"cannot update type to {item.type} ",
                    )
            for field_name, field in item.dict().items():
                if field_name != "type" and field is not None:
                    setattr(db_item, field_name, field)
            db.commit()
            return db_item

        return _route

    def get_delete_item(self):
        """
        :return: a route deleting the single item present in the backing table with the given
                id, or raising a 404 error if not present
        """
        def _route(
            item_id: int,
            db: Session = Depends(database.get_db),
            _user: User = Depends(current_user),
        ):
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

        return _route
