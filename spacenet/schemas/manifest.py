from pydantic import BaseModel, Field
from sortedcontainers import SortedSet, SortedDict

from ..constants import ClassOfSupply, Environment
# import spacenet.domain.element.I_Carrier
# import spacenet.domain.element.I_Element
# import spacenet.domain.element.I_ResourceContainer
# import spacenet.domain.element.ResourceContainer
# import spacenet.domain.element.ResourceContainerFactory
# import spacenet.domain.network.node.Body
# import spacenet.domain.network.node.SurfaceNode
# import spacenet.domain.resource.Demand
# import spacenet.domain.resource.DemandSet
# import spacenet.scenario.SupplyEdge.SupplyPoint
# import spacenet.simulator.event.ManifestEvent
# import spacenet.util.GlobalParameters
import spacenet.schemas.scenario

class Manifest(BaseModel):
    scenario: Scenario = Field(..., title="Scenario")
    supplyEdges: SortedSet = Field(..., title="Supply Edges")
    supplyPoints: SortedSet = Field(..., title="Supply Points")
    aggregatedNodeDemands: SortedDict = Field(..., title="Aggregated Node Demands")
    aggregatedEdgeDemands: SortedDict = Field(..., title="Aggregated Edge Demands")
    demandsAsPacked: dict = Field(..., title="Demands as packed")
    packedDemands: dict = Field(..., title="Packed Demands")
    cachedContainerDemands: SortedDict = Field(..., "Cached Container Demands")
    manifestedContainers: SortedDict = Field(..., "Manifested Containers")
