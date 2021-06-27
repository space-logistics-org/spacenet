from typing import List, Union

from fastapi import APIRouter, status
from .base_funcs import list_all, read_item, create_item, update_item, delete_item

NOT_FOUND_RESPONSE = {status.HTTP_404_NOT_FOUND: {"msg": str}}


class CRUDRouter(APIRouter):
    def __init__(
            self,
            table,
            name_lower,
            name_capitalized,
            create_schema,
            read_schema,
            update_schema,
    ):
        super().__init__()
        self.add_api_route(
            "/",
            list_all(table),
            methods=["GET"],
            response_model=List[read_schema],
        )
        self.add_api_route(
            "/{item_id}",
            read_item(table, name_lower),
            methods=["GET"],
            response_model=read_schema,
            responses=NOT_FOUND_RESPONSE
        )
        self.add_api_route(
            "/",
            create_item(create_schema),
            methods=["POST"],
            response_model=read_schema,
            status_code=status.HTTP_201_CREATED
        )
        self.add_api_route(
            "/{item_id}",
            update_item(table, name_capitalized, update_schema),
            methods=["PATCH"],
            response_model=read_schema,
            responses={**NOT_FOUND_RESPONSE, status.HTTP_409_CONFLICT: {"msg": str}}
        )
        self.add_api_route(
            "/{item_id}",
            delete_item(table, name_lower),
            methods=["DELETE"],
            response_model=read_schema,
            responses=NOT_FOUND_RESPONSE
        )
