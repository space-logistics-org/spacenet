import doctest
from collections import defaultdict
from typing import Dict, Hashable, Mapping, Set, TypeVar

from .edge import *
from .element import *
from .node import *
from .resource import *

__all__ = [
    "CREATE_TO_UPDATE",
    "CREATE_TO_READ",
    "READ_TO_CREATE",
    "UPDATE_TO_CREATE",
]

K = TypeVar("K")
HashableK = TypeVar("HashableK", bound=Hashable)
V = TypeVar("V", bound=Hashable)


def __invert_map(m: Mapping[HashableK, V]) -> Dict[V, Set[K]]:
    """
    Invert a mapping from K to V without mutating the provided input.

    :param m: any mapping from hashable keys to hashable values
    :return: a dict mapping v->ks where ks is all k in key-value pairs k->v in m
    >>> __invert_map({1: 2, 3: 2}) == {2: {1, 3}}
    True
    """
    ret: defaultdict[V, Set[HashableK]] = defaultdict(set)
    for k, v in m.items():
        ret[v].add(k)
    return ret


def __invert_injective_map(m: Mapping[K, V]) -> Dict[V, K]:
    """
    Invert an injective mapping from K to V without mutating the
    provided input.

    :param m: mapping from keys to one hashable value,
              where each value has only one associated key
    :return: a dict mapping v->k for all key-value pairs k->v in m
    >>> __invert_injective_map({1: 2, 3: 4}) == {2: 1, 4: 3}
    True
    """
    assert len(set(m.values())) == len(
        m.values()
    ), "key-value mapping must be an injective function"
    return {v: k for k, v in m.items()}


CREATE_TO_UPDATE = {
    FlightEdge: FlightEdgeUpdate,
    SpaceEdge: SpaceEdgeUpdate,
    SurfaceEdge: SurfaceEdgeUpdate,
    Element: ElementUpdate,
    ElementCarrier: ElementCarrierUpdate,
    ResourceContainer: ResourceContainerUpdate,
    SurfaceVehicle: SurfaceVehicleUpdate,
    PropulsiveVehicle: PropulsiveVehicleUpdate,
    HumanAgent: HumanAgentUpdate,
    RoboticAgent: RoboticAgentUpdate,
    LagrangeNode: LagrangeNodeUpdate,
    OrbitalNode: OrbitalNodeUpdate,
    SurfaceNode: SurfaceNodeUpdate,
    ContinuousResource: ContinuousUpdate,
    DiscreteResource: DiscreteUpdate,
}

UPDATE_TO_CREATE = __invert_injective_map(CREATE_TO_UPDATE)

CREATE_TO_READ = {
    FlightEdge: FlightEdgeRead,
    SpaceEdge: SpaceEdgeRead,
    SurfaceEdge: SurfaceEdgeRead,
    Element: ElementRead,
    ElementCarrier: ElementCarrierRead,
    ResourceContainer: ResourceContainerRead,
    SurfaceVehicle: SurfaceVehicleRead,
    PropulsiveVehicle: PropulsiveVehicleRead,
    HumanAgent: HumanAgentRead,
    RoboticAgent: RoboticAgentRead,
    LagrangeNode: LagrangeNodeRead,
    OrbitalNode: OrbitalNodeRead,
    SurfaceNode: SurfaceNodeRead,
    ContinuousResource: ContinuousRead,
    DiscreteResource: DiscreteRead,
}

READ_TO_CREATE = __invert_injective_map(CREATE_TO_READ)


if __name__ == "__main__":
    doctest.testmod()
