from enum import Enum

from pydantic import BaseModel, Field
from sortedcontainers import SortedSet


# import edu.mit.spacenet.domain.DomainType
# import edu.mit.spacenet.domain.model.I_DemandModel
# import edu.mit.spacenet.domain.resource.Demand
# import edu.mit.spacenet.domain.resource.DemandSet
# import edu.mit.spacenet.simulator.I_Simulator


class StateType(str, Enum):
    active = "Active"
    special = "Special"
    quiescent = "Quiescent"
    dormant = "Dormant"
    decommissioned = "Decommissioned"

    class Config:
        title: "State Type"


class State(BaseModel):
    type: StateType = Field(..., title="State Type")
    demandModels: SortedSet = Field(..., title="Demand Models")

    class Config:
        arbitrary_types_allowed = True
