from typing import Any, Dict, Optional

from pydantic import root_validator

from spacenet.schemas import Scenario
from spacenet.schemas.mission import Mission
from spacenet.schemas.scenario import Network


class CheckedScenario(Scenario):
    """
    A validated scenario which guarantees some invariants which Simulation requires of the
    input scenario.
    """
    @root_validator(skip_on_failure=True)
    def _same_start_date_as_earliest_mission_start_date(
        cls, values: Dict[str, Any]
    ) -> Dict[str, Any]:
        missions = values.get("missionList")
        assert missions is not None
        earliest_starting_mission: Optional[Mission] = min(
            missions, key=lambda mission: mission.start_date, default=None
        )
        if earliest_starting_mission is not None:
            start_date = values.get("startDate")
            assert start_date is not None
            assert start_date == earliest_starting_mission.start_date
        return values

    @root_validator(skip_on_failure=True)
    def _no_common_ids(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        network: Optional[Network] = values.get("network")
        assert network is not None
        network_ids = network.nodes.keys() | network.edges.keys()
        elements = values.get("elementList")
        assert elements is not None
        assert not (
            elements.keys() & network_ids
        ), "must not have common ids between elements and network entities"
        return values

    @root_validator(skip_on_failure=True)
    def _network_ids_match(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        network: Optional[Network] = values.get("network")
        nodes = network.nodes
        for edge_id, edge in network.edges.items():
            assert edge.origin_id in nodes, f"Edge {edge_id}'s origin is not a node"
            assert (
                edge.destination_id in nodes
            ), f"Edge {edge_id}'s destination is not a node"
        return values

    # TODO: validate events too somehow? that would require being able to decompose events
    # TODO: check that no additions will overflow as well?
