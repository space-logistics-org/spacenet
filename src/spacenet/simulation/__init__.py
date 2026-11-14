"""
Defines simulation objects.
"""

import logging

from .analysis import (
    AggregatedDemandsAnalysis,
    EdgeDemand,
    NodeDemand,
    RawDemand,
    RawDemandsAnalysis,
)
from .demand_models import (
    SimCrewConsumablesDemandModel,
    SimDemandModel,
    SimRatedDemandModel,
    SimSparingByMassDemandModel,
    SimTimedImpulseDemandModel,
)
from .elements import (
    OperationalState,
    PartApplication,
    SimAgent,
    SimCarrier,
    SimCrewMember,
    SimElement,
    SimPropulsiveVehicle,
    SimResourceContainer,
    SimResourceTank,
    SimRoboticAgent,
    SimSurfaceVehicle,
)
from .errors import SimDemand, SimError, SimSpatialError, SimWarning
from .events import (
    AddEvent,
    BurnEvent,
    CreateEvent,
    DemandEvent,
    EvaEvent,
    ExplorationProcess,
    FlightTransportEvent,
    MissionEvent,
    MoveEvent,
    ReconfigureEvent,
    ReconfigureGroupEvent,
    RemoveEvent,
    SimEvent,
    SpaceTransportEvent,
    SurfaceTransportEvent,
    TransferEvent,
    TransportEvent,
)
from .mission import SimMission
from .network import SimBurn, SimEdge, SimLocation, SimNetwork, SimNode
from .records import (
    ElementSnapshot,
    LocationSnapshot,
    MoeCrewSurfaceDays,
    MoeCrewTime,
    MoeExplorationCapability,
    MoeExplorationMassDelivered,
    MoeLaunchMass,
    MoeMassCapacityUtilization,
    NetworkSnapshot,
    SimRepair,
    SimScavenge,
)
from .resources import Demand, DemandSet, SimResource
from .settings import Settings
from .simulator import (
    DemandSimulator,
    FullSimulator,
    MiniSimulator,
    PreSimulator,
    Simulator,
)
from .state import State
from .supply import RepairItem, SupplyEdge, SupplyPoint

# simulation progress is only reported if the application configures logging
logging.getLogger(__name__).addHandler(logging.NullHandler())
