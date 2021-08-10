from typing import Dict, List, Set, Tuple, Union
from uuid import UUID

from pydantic import BaseModel, Field, NonNegativeFloat, validator

from spacenet.analysis.indirect_entities import IndirectEntity
from spacenet.analysis.simulation_errors import SimError
from spacenet.schemas import AllElements, AllNodes, AllUUIDEdges, PropulsiveVehicle

__all__ = ["SimElement", "SimNode", "SimEdge", "into_indirect_entity"]

InvRichNamespace = Dict[Union["SimElement", "SimNode", "SimEdge"], UUID]


class ContainsElements(BaseModel):
    contents: List["SimElement"] = Field(default_factory=list)


class SimElement(ContainsElements):
    """
    An element under simulation; wraps Element schema.
    """

    inner: AllElements
    fuel_mass: NonNegativeFloat = 0

    def __hash__(self):
        return hash(self.inner)

    def all_contained(self) -> Tuple[Set[AllElements], List["SimError"]]:
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
        all_contained, errors = self.all_contained()
        return sum(contained.mass for contained in all_contained), errors

    @property
    def current_mass(self) -> float:
        return self.inner.mass + self.fuel_mass

    @validator("fuel_mass")
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

    inner: AllUUIDEdges

    def __hash__(self):
        # Analogous safety argument as to SimNode
        return hash(self.inner)


SimElement.update_forward_refs()


def into_indirect_entity(
    entity: Union[SimElement, SimNode, SimEdge], inverse_namespace: InvRichNamespace,
) -> IndirectEntity:
    return IndirectEntity(
        inner=inverse_namespace[entity],
        contents=[inverse_namespace[element] for element in entity.contents],
    )
