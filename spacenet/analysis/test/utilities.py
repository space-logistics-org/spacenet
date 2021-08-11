from hypothesis import strategies as st
from typing import Callable, TypeVar

from spacenet.schemas import Scenario

__all__ = ["T", "DrawFn", "build_validating_scenario"]

T = TypeVar("T")
DrawFn = Callable[[st.SearchStrategy[T]], T]


@st.composite
def build_validating_scenario(draw: DrawFn):
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
    return base_scenario
