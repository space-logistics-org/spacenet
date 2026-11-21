"""
Defines object schemas for events that act upon resources.
"""

from enum import Enum
from typing import List, Optional, Union
from uuid import UUID

from pydantic import Field
from typing_extensions import Literal

from .event import Event, EventType

from ..elements.propulsion import TankSelector
from ..resources import ResourceAmount, GenericResourceAmount


class TransferMode(str, Enum):
    """
    Enumeration of the modes of a resource transfer.
    """

    #: Transfer the listed resource amounts.
    AMOUNT = "Amount"
    #: Transfer as much as possible to fill the destination.
    FILL_DESTINATION = "Fill Destination"
    #: Transfer as much as possible to empty the origin.
    EMPTY_ORIGIN = "Empty Origin"


class TransferResources(Event):
    """
    Event that transfers resources between resource container elements,
    including the integral fuel and oxidizer tanks of vehicles (e.g., to
    refuel a vehicle from a propellant depot).
    """

    type: Literal[EventType.TRANSFER_RESOURCES] = Field(
        EventType.TRANSFER_RESOURCES,
        title="Type",
        description="Event type",
    )
    resources: List[Union[ResourceAmount, GenericResourceAmount]] = Field(
        [],
        title="Transferred Resources",
        description="list of resource amounts to transfer (optional to fill "
        "the destination or empty the origin with all matching resources)",
    )
    origin_container: UUID = Field(
        ...,
        title="Origin Container",
        description="Unique identifier of the resource-transferring origin container",
    )
    destination_container: UUID = Field(
        ...,
        title="Destination Container",
        description="Unique identifier of the resource-transferring destination container",
    )
    origin_tank: Optional[TankSelector] = Field(
        None,
        title="Origin Tank",
        description="Integral tank of an origin vehicle (default: the tanks "
        "which hold the transferred resources)",
    )
    destination_tank: Optional[TankSelector] = Field(
        None,
        title="Destination Tank",
        description="Integral tank of a destination vehicle (default: the "
        "tanks which hold the transferred resources)",
    )
    transfer_mode: Optional[TransferMode] = Field(
        None,
        title="Transfer Mode",
        description="Transfer the listed amounts (default), fill the "
        "destination, or empty the origin",
    )
    loss_fraction: Optional[float] = Field(
        None,
        title="Loss Fraction",
        description="Fraction of the removed resources lost during transfer "
        "(omitted if no losses)",
        ge=0,
        lt=1,
    )
