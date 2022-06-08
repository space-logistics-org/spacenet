"""
This module defines entities which are to be simulated, most of which are wrappers around other
schema to add additional fields or methods.
"""
from datetime import datetime
from typing import Dict, List, Set, Tuple, Union
from uuid import UUID

from pydantic import BaseModel, Field, NonNegativeFloat, validator

from ..analysis.indirect_entities import IndirectEntity
from ..analysis.errors import SimError
from ..schemas import AllElements, AllNodes, AllEdges, PropulsiveVehicle

__all__ = ["SimElement", "SimNode", "SimEdge", "SimResult", "into_indirect_entity"]

InvRichNamespace = Dict[Union["SimElement", "SimNode", "SimEdge"], UUID]


class ContainsElements(BaseModel):
    """
    A mixin for entities which contain elements under simulation.
    """

    contents: List["SimElement"] = Field(default_factory=list)


class SimElement(ContainsElements):
    """
    An element under simulation; wraps Element schema.
    """

    inner: AllElements
    fuel_mass: NonNegativeFloat = None

    def __hash__(self):
        return hash(self.inner)

    def all_contained(self) -> Tuple[Set[AllElements], List["SimError"]]:
        """
        :return: the set of all elements contained in this element, and any errors found
                relating to invariant violations in the containment relationship
        """
        visited = {self.inner}
        errors = []
        stack = list(self.contents)
        while stack:
            next_element = stack.pop()
            for contained in next_element.contents:
                if contained.inner == self.inner:
                    errors.append(
                        SimError(
                            description=f"Element {self.inner.name} cannot contain itself"
                        )
                    )
                elif contained.inner in visited:
                    errors.append(
                        SimError(
                            description=f"Element {contained.inner.name} "
                            f"has multiple containers"
                        )
                    )
                else:
                    stack.append(contained)
            visited.add(next_element.inner)
        return visited, errors

    def total_mass(self) -> Tuple[float, List["SimError"]]:
        """
        :return: the total mass of all elements contained in this element, and any errors
            found relating to invariant violations in the containment relationship
        """
        all_contained, errors = self.all_contained()
        return sum(contained.mass for contained in all_contained) + self.fuel_mass, errors

    @property
    def current_mass(self) -> float:
        """
        :return: the current mass of this element
        """
        return self.inner.mass + self.fuel_mass

    @validator("fuel_mass", always=True)
    def _initialize_fuel_mass(cls, value, values, config, field) -> float:
        inner: AllElements = values.get("inner")
        return inner.max_fuel if isinstance(inner, PropulsiveVehicle) else 0


ContainsElements.update_forward_refs()


class SimNode(ContainsElements):
    """
    A node under simulation; wraps Node schema.
    """

    inner: AllNodes

    def __hash__(self):
        # This is safe because, assuming Node is safe to hash, we don't hash the mutable
        # state in contents
        return hash(self.inner)


class SimEdge(ContainsElements):
    """
    An edge under simulation; wraps Edge schema.
    """

    inner: AllEdges

    def __hash__(self):
        # Analogous safety argument as to SimNode
        return hash(self.inner)


SimElement.update_forward_refs()


def into_indirect_entity(
    entity: Union[SimElement, SimNode, SimEdge], inverse_namespace: InvRichNamespace,
) -> IndirectEntity:
    """
    Convert a richly represented entity into the equivalent entity.

    :param entity: entity to convert into indirect equivalent
    :param inverse_namespace: namespace mapping rich representations of entities
        (not using UUID references) to the UUIDs of those entities
    :return: the indirect entity which is equivalent to entity
    """
    return IndirectEntity(
        inner=inverse_namespace[entity],
        contents=[inverse_namespace[element] for element in entity.contents],
    )


class SimResult(BaseModel):
    """
    A representation of the outcome of a simulation. Uses indirection and namespace together
    to simplify queries on the network in the result.
    """

    nodes: List[IndirectEntity]
    edges: List[IndirectEntity]
    elements: List[IndirectEntity]
    end_time: datetime
    namespace: Dict[UUID, Union[SimEdge, SimElement, SimNode]]
