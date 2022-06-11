"""
This module contains utilities for testing spacenet's analysis and simulation components.
"""
from hypothesis import assume, strategies as st
from typing import Callable, TypeVar

from ...src.analysis.checked_scenario import CheckedScenario
from ...src.schemas import ElementTransportEvent, Scenario, UUIDSpaceEdge

__all__ = ["T", "DrawFn", "build_validating_scenario", "build_checked_scenario"]

T = TypeVar("T")
DrawFn = Callable[[st.SearchStrategy[T]], T]


@st.composite
def build_validating_scenario(draw: DrawFn):
    """
    Construct a scenario which would validate if converted to a checked scenario.

    :param draw: function to use for drawing samples; error to provide manually
    :return: a scenario which would validate if converted to a checked scenario
    """
    base_scenario = draw(st.builds(Scenario))
    start_date = min(
        (mission.start_date for mission in base_scenario.missionList),
        default=base_scenario.startDate,
    )
    base_scenario.startDate = start_date
    # Overwrite edge endpoints s.t. all edge endpoints are also nodes
    new_edges = {}
    node_id_set = set(base_scenario.network.nodes.keys())
    node_id_list = list(base_scenario.network.nodes.keys())
    if node_id_list:
        for edge_id, edge in base_scenario.network.edges.items():
            origin_id = edge.origin_id
            if origin_id not in node_id_set:
                origin_id = draw(st.sampled_from(node_id_list))
            destination_id = edge.destination_id
            if destination_id not in node_id_set:
                destination_id = draw(
                    st.sampled_from(node_id_list).filter(
                        lambda node_id: node_id != origin_id
                    )
                )
            new_edge_dict = edge.dict()
            new_edge_dict["origin_id"] = origin_id
            new_edge_dict["destination_id"] = destination_id
            new_edge = edge.parse_obj(new_edge_dict)
            new_edges[edge_id] = new_edge
    base_scenario.network.edges = new_edges
    mission_list = base_scenario.missionList
    new_edge_ids = list(new_edges.keys())
    for mission in mission_list:
        for event in mission.events:
            if isinstance(event, ElementTransportEvent):
                assume(new_edge_ids)
                edge = draw(
                    st.builds(
                        UUIDSpaceEdge,
                        origin_id=st.sampled_from(node_id_list),
                        destination_id=st.sampled_from(node_id_list),
                    )
                )
                edge_id = draw(st.uuids().filter(lambda id_: id_ not in new_edges))
                new_edges[edge_id] = edge
                event.edge_id = edge_id
                event.origin_node_id = edge.origin_id
                event.destination_node_id = edge.destination_id
    return base_scenario


build_checked_scenario = build_validating_scenario().map(
    lambda scenario: CheckedScenario.parse_obj(scenario.dict())
)
