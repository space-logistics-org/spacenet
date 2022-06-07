"""
This module enumerates all of the schema variants and subtypes from the api documentation.
"""

import doctest

from .edge import *
from .element import *
from .node import *
from .resource import *
from .state import *
from .utilities import invert_injective_map

__all__ = [
    "CREATE_SCHEMAS",
    "UPDATE_SCHEMAS",
    "READ_SCHEMAS",
    "CREATE_TO_UPDATE",
    "CREATE_TO_READ",
    "READ_TO_CREATE",
    "UPDATE_TO_CREATE",
    "EDGE_SCHEMAS",
    "ELEMENT_SCHEMAS",
    "NODE_SCHEMAS",
    "RESOURCE_SCHEMAS",
    "STATE_SCHEMAS"
]


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
    State: StateUpdate,
}

CREATE_SCHEMAS = set(CREATE_TO_UPDATE.keys())

UPDATE_TO_CREATE = invert_injective_map(CREATE_TO_UPDATE)

UPDATE_SCHEMAS = set(UPDATE_TO_CREATE.keys())

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
    State: StateRead
}

READ_TO_CREATE = invert_injective_map(CREATE_TO_READ)

READ_SCHEMAS = set(READ_TO_CREATE.keys())

EDGE_SCHEMAS = {
    FlightEdge,
    FlightEdgeUpdate,
    FlightEdgeRead,
    SpaceEdge,
    SpaceEdgeUpdate,
    SpaceEdgeRead,
    SurfaceEdge,
    SurfaceEdgeUpdate,
    SurfaceEdgeRead,
}

ELEMENT_SCHEMAS = {
    Element,
    ElementUpdate,
    ElementRead,
    ElementCarrier,
    ElementCarrierUpdate,
    ElementCarrierRead,
    ResourceContainer,
    ResourceContainerUpdate,
    ResourceContainerRead,
    SurfaceVehicle,
    SurfaceVehicleUpdate,
    SurfaceVehicleRead,
    PropulsiveVehicle,
    PropulsiveVehicleUpdate,
    PropulsiveVehicleRead,
    HumanAgent,
    HumanAgentUpdate,
    HumanAgentRead,
    RoboticAgent,
    RoboticAgentUpdate,
    RoboticAgentRead,
}

NODE_SCHEMAS = {
    LagrangeNode,
    LagrangeNodeUpdate,
    LagrangeNodeRead,
    OrbitalNode,
    OrbitalNodeUpdate,
    OrbitalNodeRead,
    SurfaceNode,
    SurfaceNodeUpdate,
    SurfaceNodeRead,
}

RESOURCE_SCHEMAS = {
    ContinuousResource,
    ContinuousUpdate,
    ContinuousRead,
    DiscreteResource,
    DiscreteUpdate,
    DiscreteRead,
}

STATE_SCHEMAS = {
    State,
    StateUpdate,
    StateRead
}

if __name__ == "__main__":
    doctest.testmod()
