"""
Defines simulation objects.
"""

import logging

from .analysis import (
    AggregatedDemandsAnalysis,
    DemandsAnalysis,
    EdgeDemand,
    EventEvaluation,
    ISRUAnalysis,
    ManifestAnalysis,
    ManifestResult,
    ManifestSelection,
    MissionsAnalysis,
    NodeDemand,
    PowerAnalysis,
    PropellantAnalysis,
    RawDemand,
    RawDemandsAnalysis,
    SimIssue,
    SimulationAnalysis,
    StateAnalysis,
    TankerSizing,
    TankerSizingRequest,
    size_tankers,
)
from .demand_models import (
    SimCrewConsumablesDemandModel,
    SimDemandModel,
    SimRatedDemandModel,
    SimSparingByMassDemandModel,
    SimISRUProcessModel,
    SimTimedImpulseDemandModel,
)
from .elements import (
    OperationalState,
    PartApplication,
    SimAgent,
    SimCarrier,
    SimCrewMember,
    SimElement,
    SimPropulsionSystem,
    SimPropulsiveVehicle,
    SimResourceContainer,
    SimResourceTank,
    SimRoboticAgent,
    SimSurfaceVehicle,
)
from .errors import ScenarioError, SimDemand, SimError, SimSpatialError, SimWarning
from .events import (
    AddEvent,
    BurnEvent,
    CreateEvent,
    DemandEvent,
    EvaEvent,
    ExplorationProcess,
    FlightTransportEvent,
    ManifestEvent,
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
from .manifest import (
    ManifestDemand,
    ManifestItem,
    SimManifest,
    SimManifestContainer,
    container_factory,
)
from .records import (
    BurnStep,
    ElementSnapshot,
    LocationSnapshot,
    MoeCrewSurfaceDays,
    MoeCrewTime,
    MoeExplorationCapability,
    MoeExplorationMassDelivered,
    MoeLaunchMass,
    MoeMassCapacityUtilization,
    NetworkHistory,
    NetworkSnapshot,
    PowerRecord,
    PropellantFlow,
    PropellantFlowKind,
    SimRepair,
    SimScavenge,
    TransferStep,
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
