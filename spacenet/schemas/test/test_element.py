from typing import Callable, Dict, Tuple

import pytest
from hypothesis import given, strategies as st
from pydantic import BaseModel
from typing_extensions import Type

from spacenet.schemas import (
    Element,
    ElementCarrier,
    HumanAgent,
    PropulsiveVehicle,
    ResourceContainer,
    RoboticAgent,
    SurfaceVehicle,
)
from .utilities import (
    success_from_kw,
    xfail_from_kw,
)
from .element_maps import *

pytestmark = [pytest.mark.schema, pytest.mark.element, pytest.mark.unit]


def kw_strategy_from_maps_and_param(
    valid_map: Dict, invalid_map: Dict, invalid_param: str
) -> st.SearchStrategy[Dict]:
    return st.fixed_dictionaries(
        mapping={**valid_map, invalid_param: invalid_map[invalid_param],}
    )


def make_tests_from_type_and_maps(
    ty_: Type[BaseModel], valid_map: Dict, invalid_map: Dict
) -> Tuple[Callable[[Dict], None], Callable[[st.DataObject, str], None]]:
    @given(kw=st.fixed_dictionaries(valid_map))
    def success(kw: Dict):
        success_from_kw(ty_, **kw)

    @pytest.mark.parametrize("invalid_param", list(invalid_map.keys()))
    @given(data=st.data())
    def failure(data: st.DataObject, invalid_param: str):
        kw = data.draw(
            kw_strategy_from_maps_and_param(valid_map, invalid_map, invalid_param)
        )
        xfail_from_kw(ty_, **kw)

    return success, failure


test_element_success, test_element_failure = make_tests_from_type_and_maps(
    Element, VALID_ELEMENT_MAP, INVALID_ELEMENT_MAP
)

(
    test_resource_container_success,
    test_resource_container_failure,
) = make_tests_from_type_and_maps(
    ResourceContainer, VALID_RESOURCE_CONTAINER_MAP, INVALID_RESOURCE_CONTAINER_MAP
)

(
    test_element_carrier_success,
    test_element_carrier_failure,
) = make_tests_from_type_and_maps(
    ElementCarrier, VALID_ELEMENT_CARRIER_MAP, INVALID_ELEMENT_CARRIER_MAP
)

test_human_agent_success, test_human_agent_failure = make_tests_from_type_and_maps(
    HumanAgent, VALID_HUMAN_AGENT_MAP, INVALID_HUMAN_AGENT_MAP
)

test_robotic_agent_success, test_robotic_agent_failure = make_tests_from_type_and_maps(
    RoboticAgent, VALID_ROBOTIC_AGENT_MAP, INVALID_ROBOTIC_AGENT_MAP
)

(
    test_propulsive_vehicle_success,
    test_propulsive_vehicle_failure,
) = make_tests_from_type_and_maps(
    PropulsiveVehicle, VALID_PROPULSIVE_VEHICLE_MAP, INVALID_PROPULSIVE_VEHICLE_MAP
)

(
    test_surface_vehicle_success,
    test_surface_vehicle_failure,
) = make_tests_from_type_and_maps(
    SurfaceVehicle, VALID_SURFACE_VEHICLE_MAP, INVALID_SURFACE_VEHICLE_MAP
)
