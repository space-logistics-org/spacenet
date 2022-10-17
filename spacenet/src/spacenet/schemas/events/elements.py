"""
Defines object schemas for events that act upon elements.
"""
from typing import List
from uuid import UUID

from pydantic import Field
from typing_extensions import Literal

from .event import Event, EventType

from ..elements import StateType
from ..utils import SafeInt


class CreateElements(Event):
    """
    Event that creates instantiated elements inside a node, edge, or
    instantiated element carrier.

    :param [UUID] elements: list of instantiated elements (by unique identifier) to be created
    :param UUID container: unique identifier of the node, edge, or instantiated carrier where the elements are to be created
    """

    type: Literal[EventType.CREATE_ELEMENTS] = Field(
        EventType.CREATE_ELEMENTS, title="Type", description="Event type",
    )
    elements: List[UUID] = Field(
        ...,
        description="List of instantiated elements (by unique identifier) to be created",
    )
    container: UUID = Field(
        ...,
        description="Node, edge, or instantiated carrier where the elements are to be created",
    )


class MoveElements(Event):
    """
    Event that moves instantiated elements to a new node, edge, or instantiated
    carrier.

    :param [UUID] elements: list of instantiated elements (by unique identifier) to be moved
    :param UUID container: unique identifier of the node, edge, or instantiated carrier where the elements are to be moved

    """

    type: Literal[EventType.MOVE_ELEMENTS] = Field(
        EventType.MOVE_ELEMENTS, title="Type", description="Event type",
    )
    elements: List[UUID] = Field(
        ...,
        description="List of instantiated elements (by unique identifier) to be moved",
    )
    container: UUID = Field(
        ...,
        description="Unique identifier of the node, edge, or instantiated carrier where the elements are to be moved",
    )


class RemoveElements(Event):
    """
    Event that removes instantiated elements.

    :param [UUID] elements: list of instantiated elements (by unique identifier) to be removed
    """

    type: Literal[EventType.REMOVE_ELEMENTS] = Field(
        EventType.REMOVE_ELEMENTS, title="Type", description="Event type",
    )
    elements: List[UUID] = Field(
        ...,
        description="List of instantiated elements (by unique identifier) to be removed",
    )


class ReconfigureElement(Event):
    """
    Event that changes the operational state of one instantiated element.

    :param UUID element: unique identifier of the instantiated element to be reconfigured
    :param SafeInt state_index: index of the new operational state
    """

    type: Literal[EventType.RECONFIGURE_ELEMENT] = Field(
        EventType.RECONFIGURE_ELEMENT, title="Type", description="Event type",
    )
    element: UUID = Field(
        ...,
        description="Unique identifier of the instantiated element to be reconfigured",
    )
    state_index: SafeInt = Field(
        ..., title="State Index", description="Index of the new operational state"
    )


class ReconfigureElements(Event):
    """
    Event that changes the operational state of multiple instantiated elements.

    :param [UUID] elements: list of instantiated elements (by unique identifier) to be reconfigured
    :param StateType state_type: state type to which to be reconfigured
    """

    type: Literal[EventType.RECONFIGURE_ELEMENTS] = Field(
        EventType.RECONFIGURE_ELEMENTS, title="Type", description="Event type",
    )
    elements: List[UUID] = Field(
        ...,
        description="List of instantiated elements (by unique identifier) to be reconfigured",
    )
    state_type: StateType = Field(
        ..., description="State type to which to be reconfigured",
    )
