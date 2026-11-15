"""
Object schemas for the results of simulation analyses.
"""

from .demands import (
    AggregatedDemandsAnalysis,
    DemandElement,
    DemandLocation,
    DemandResource,
    DemandResourceType,
    DemandsAnalysis,
    DemandSeries,
    DemandSource,
    EdgeDemand,
    FeasibilityPoint,
    NodeDemand,
    NodeFeasibility,
    RawDemand,
    RawDemandsAnalysis,
    SupplyEdgeSummary,
    SupplyPointSummary,
)
from .export import export_aggregated_demands, export_manifest, export_raw_demands
from .issues import IssueReference, SimIssue, collect_issues
from .manifest import (
    ManifestAnalysis,
    ManifestCarrierView,
    ManifestContainerView,
    ManifestDemandView,
    ManifestEdgeView,
    ManifestResult,
    ManifestSelection,
    PackedDemandView,
)
from .missions import (
    ElementLocationHistory,
    EventSummary,
    LocationSegment,
    LocationSummary,
    MissionsAnalysis,
    MissionSummary,
)
from .simulation import (
    MassHistory,
    MassSeries,
    MeasureRecord,
    Measures,
    MeasureTotals,
    NetworkState,
    SimulationAnalysis,
)
from .state import (
    BurnResult,
    BurnStepResult,
    ElementState,
    EventEvaluation,
    LocationState,
    NextEvent,
    StateAnalysis,
    TransportResult,
)
