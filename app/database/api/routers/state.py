"""
This module defines CRUD routes for the state schema.
"""

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth_dependencies import User, current_user
from .base_router import CRUDRouter, NOT_FOUND_RESPONSE, Route
from .. import database
from ..models import state as models
from ..models.element import Element as ElementModel
from ..schemas.constants import STATE_SCHEMAS
from ..schemas.state import State, StateRead, StateUpdate

router = CRUDRouter(
    table=models.State,
    name_lower="state",
    name_capitalized="State",
    schemas=STATE_SCHEMAS,
    generated_routes={Route.GetOne, Route.GetAll, Route.Delete},
)


@router.post(
    "/",
    response_model=StateRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create State",
    description="Add a new state to the database.",
)
def create_state(
    state: State,
    db: Session = Depends(database.get_db),
    _user: User = Depends(current_user),
) -> StateRead:
    db_element = db.query(ElementModel).get(state.element_id)
    if db_element is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid element id: {state.element_id} does not correspond to "
            f"an element in the database",
        )
    create_item_fn = router.get_create_item()
    return create_item_fn(state, db, _user)


@router.patch(
    "/{item_id}",
    response_model=StateRead,
    responses={**NOT_FOUND_RESPONSE, status.HTTP_409_CONFLICT: {"msg": str},},
    summary="Update State",
    description="Update an existing state in the database.",
)
def update_state(
    state: StateUpdate,
    db: Session = Depends(database.get_db),
    _user: User = Depends(current_user),
):
    db_element = db.query(ElementModel).get(state.element_id)
    if db_element is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid element id: {state.element_id} does not correspond to "
            f"an element in the database",
        )
    update_item_fn = router.get_update_item()
    return update_item_fn(state, db, _user)
