from enum import Enum, auto
from typing import List, Set

from fastapi import APIRouter, status
from pydantic import BaseModel
from typing_extensions import Type

from .base_funcs import list_all, read_item, create_item, update_item, delete_item
from ..database import Base

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
        create_schema: Type[BaseModel],
        read_schema: Type[BaseModel],
        update_schema: Type[BaseModel],
        generated_routes: Set[Route] = None,
        prefix: str = "",
    ):
        super().__init__(prefix=prefix)
        if generated_routes is None:
            generated_routes = {variant for variant in Route}
        if Route.GetAll in generated_routes:
            self.add_api_route(
                path="/",
                endpoint=list_all(table),
                methods=["GET"],
                response_model=List[read_schema],
                summary=f"List {name_capitalized}s",
                description=f"List {name_lower}s currently in the database.",
            )
        if Route.GetOne in generated_routes:
            self.add_api_route(
                path="/{item_id}",
                endpoint=read_item(table, name_lower),
                methods=["GET"],
                response_model=read_schema,
                responses=NOT_FOUND_RESPONSE,
                summary=f"Read {name_capitalized}",
                description=f"Find a specific {name_lower} in the database.",
            )
        if Route.Create in generated_routes:
            self.add_api_route(
                path="/",
                endpoint=create_item(create_schema),
                methods=["POST"],
                response_model=read_schema,
                status_code=status.HTTP_201_CREATED,
                summary=f"Create {name_capitalized}",
                description=f"Add a new {name_lower} to the database.",
            )
        if Route.Update in generated_routes:
            self.add_api_route(
                path="/{item_id}",
                endpoint=update_item(table, name_capitalized, update_schema),
                methods=["PATCH"],
                response_model=read_schema,
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
                endpoint=delete_item(table, name_lower),
                methods=["DELETE"],
                response_model=read_schema,
                responses=NOT_FOUND_RESPONSE,
                summary=f"Delete {name_capitalized}",
                description=f"Delete an existing {name_lower} from the database.",
            )
