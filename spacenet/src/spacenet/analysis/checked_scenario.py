"""
This module defines a schema for scenarios which validates that some properties required for
making a scenario run without exceptions are true.
"""
from typing import Any, Dict, List, Optional

from pydantic import root_validator, validator

from spacenet.schemas import (
    FlightTransport,
    Scenario,
    SpaceTransport,
    SurfaceTransport,
    SpaceEdge,
)
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
        missions = values.get("mission_list")
        assert missions is not None
        earliest_starting_mission: Optional[Mission] = min(
            missions, key=lambda mission: mission.start_date, default=None
        )
        if earliest_starting_mission is not None:
            start_date = values.get("start_date")
            assert start_date is not None
            assert start_date == earliest_starting_mission.start_date
        return values

    @root_validator(skip_on_failure=True)
    def _no_common_ids(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        network: Optional[Network] = values.get("network")
        assert network is not None
        network_ids = network.nodes.keys() | network.edges.keys()
        elements = values.get("element_templates")
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

    # Initialization occurs in this schema because we do validation that edges actually exist
    # in this schema

    @validator("mission_list")
    def _initialize_default_delta_v(cls, v, values, **kwargs) -> List[Mission]:
        assert "network" in values, "prior errors raised for network being invalid"
        network: Network = values["network"]
        edges = network.edges
        missions: List[Mission] = v
        for mission in missions:
            for event in mission.events:
                if isinstance(event, SpaceTransport) and event.delta_v is None:
                    assert event.edge_id in edges
                    edge = edges[event.edge_id]
                    assert isinstance(edge, SpaceEdge)
                    event.delta_v = edges[event.edge_id].delta_v
        return missions

    @root_validator(skip_on_failure=True)
    def _transport_events_reference_real_edges(
        cls, values: Dict[str, Any]
    ) -> Dict[str, Any]:
        edges = values["network"].edges
        missions: List[Mission] = values["mission_list"]
        for mission in missions:
            for event in mission.events:
                if isinstance(
                    event, (SpaceTransport, FlightTransport, SurfaceTransport)
                ):
                    assert (
                        event.edge_id in edges
                    ), f"event {event.name} referenced nonexistent edge {event.edge_id}"
        return values

    # TODO: validate events too somehow? that would require being able to decompose events
    # TODO: check that no additions will overflow as well?
