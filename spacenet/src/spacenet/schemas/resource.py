"""
This module defines schemas for specifying resources.
"""
from enum import Enum
from typing import List, Optional, Union
from uuid import uuid4, UUID

from pydantic import Field
from typing_extensions import Literal

from .mixins import ImmutableBaseModel
from .types import SafeNonNegFloat, SafePosFloat
from .constants import ClassOfSupply, Environment

__all__ = ["ResourceType", "ContinuousResource", "DiscreteResource", "ResourceUUID", "Resource", "ResourceAmount", "ResourceAmountRate", "GenericResourceAmountRate", "GenericResourceAmount"]

class ResourceUUID(ImmutableBaseModel):
    """
    A base class which defines a resource by its UUID only.
    
    :param UUID id: unique identifier for resource
    """
    id: UUID = Field(default_factory=uuid4, description="unique identifier for resource")


class ResourceType(str, Enum):
    """
    An enumeration of the different kinds of resource.
    """

    Discrete = "Discrete"
    Continuous = "Continuous"

class Resource(ResourceUUID):
    """
    A resource with a given class of supply as a general category, as well as specified
    physical properties such as mass and volume.

    :param str name: resource name
    :param ClassOfSupply class_of_supply: class of supply number for resource
    :param SafeNonNegFloat packing_factor: nonnegative float representing resource's packing factor
    :param str units: user customizable field for what 1.0 quantity of resource represents
    :param str description: optional field for description of resource
    :param SafePosFloat unit_mass: resource mass
    :param unit_volume SafeNonNegFloat: resource volume
    """

    name: str = Field(..., title="Name", description="Resource name")
    class_of_supply: ClassOfSupply = Field(
        ..., title="Class of Supply", description="Class of supply number"
    )
    packing_factor: SafeNonNegFloat = Field(..., title="Packing Factor", description="Nonnegative float representing resource's packing factor")
    units: str = Field(default="kg", title="Units", description="user customizable field for what 1.0 quantity of resource represents")
    description: Optional[str] = Field(
        default=None, title="Description", description="Short description"
    )
    unit_mass: SafePosFloat = Field(..., title="Unit Mass", description="Resource mass")
    unit_volume: SafeNonNegFloat = Field(
        ..., title="Unit Volume", description="Resource volume"
    )

class ResourceAmount(ImmutableBaseModel):
    """
    A specified amount of a resource type.

    :param UUID resource: UUID of resource being used
    :param float amount: amount of resource being used, in units specified by that resource
    """

    resource: UUID = Field(..., title="Resource UUID", description="UUID of the resource being used")
    amount: float = Field(..., title="Amount", description="amount of resource being used, in units specified by that resource")

class ResourceAmountRate(ImmutableBaseModel):
    """
    A specified amount of a resource type.

    :param UUID resource: UUID of resource being used
    :param float rate: rate of resource being used, in units specified by that resource
    """

    resource: UUID = Field(..., title="Resource UUID", description="UUID of the resource being used")
    rate: float = Field(..., title="Rate", description="rate of resource being used, in units specified by that resource")

class GenericResourceAmount(ImmutableBaseModel):
    """
    A specified amount of a generic resource.

    :param ClassOfSupply class_of_supply: COS number of generic resource being used
    :param Environment environment: environment of generic resource. Either pressurized or unpressurized.
    :param float amount: amount of generic resource being used, in units specified by that resource
    """

    class_of_supply: ClassOfSupply = Field(..., title="Class of Suppoly", description="class of suppply of the generic resource being used")
    environment: Environment = Field(..., title="Environment", description="Environment"),
    amount: float = Field(..., title="Amount", description="amount of resource being used, in units specified by that resource")

class GenericResourceAmountRate(ImmutableBaseModel):
    """
    A specified amount of a generic resource.

    :param ClassOfSupply class_of_supply: COS number of generic resource being used
    :param Environment environment: environment of generic resource. Either pressurized or unpressurized.
    :param float rate: rate of generic resource being used, in units specified by that resource
    """

    class_of_supply: ClassOfSupply = Field(..., title="Class of Suppoly", description="class of suppply of the generic resource being used")
    environment: Environment = Field(..., title="Environment", description="Environment"),
    rate: float = Field(..., title="Rate", description="rate of resource being used, in units specified by that resource")



class DiscreteResource(Resource):
    """
    A resource which can only be replaced in discrete increments.
    """

    type: Literal[ResourceType.Discrete] = Field(
        ResourceType.Discrete, title="Type", description="Resource type"
    )


class ContinuousResource(Resource):
    """
    A resource which can be replaced in continuous increments.
    """

    type: Literal[ResourceType.Continuous] = Field(
        ResourceType.Continuous, title="Type", description="Resource type"
    )

AllResources = Union[DiscreteResource, ContinuousResource]
