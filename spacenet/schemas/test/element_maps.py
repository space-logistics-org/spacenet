from typing import Dict, List

from spacenet.schemas.constants import (
    ClassOfSupply,
    Environment,
    SQLITE_MAX_INT,
    SQLITE_MIN_INT,
)
from spacenet.schemas.element import ElementKind
from hypothesis import strategies as st

from spacenet.schemas.test.utilities import UNSERIALIZABLE_INTS

__all__ = [
    "VALID_ELEMENT_MAP",
    "VALID_ELEMENT_CARRIER_MAP",
    "VALID_RESOURCE_CONTAINER_MAP",
    "VALID_ROBOTIC_AGENT_MAP",
    "VALID_HUMAN_AGENT_MAP",
    "VALID_SURFACE_VEHICLE_MAP",
    "VALID_PROPULSIVE_VEHICLE_MAP",
    "INVALID_ELEMENT_MAP",
    "INVALID_ELEMENT_CARRIER_MAP",
    "INVALID_HUMAN_AGENT_MAP",
    "INVALID_ROBOTIC_AGENT_MAP",
    "INVALID_RESOURCE_CONTAINER_MAP",
    "INVALID_SURFACE_VEHICLE_MAP",
    "INVALID_PROPULSIVE_VEHICLE_MAP",
    "kw_strategy_from_maps_and_param"
]


def enum_values(enum_) -> List:
    return [variant.value for variant in enum_]


def kw_strategy_from_maps_and_param(
    valid_map: Dict, invalid_map: Dict, invalid_param: str
) -> st.SearchStrategy[Dict]:
    return st.fixed_dictionaries(
        mapping={**valid_map, invalid_param: invalid_map[invalid_param],}
    )


NON_NEGATIVE_FINITE_FLOATS = st.floats(min_value=0, allow_infinity=False, allow_nan=False)
NEGATIVE_AND_INFINITE_FLOATS = st.one_of(
    st.just(-float("inf")),
    st.just(float("inf")),
    st.just(float("nan")),
    st.floats(max_value=0, exclude_max=True),
)

CLASS_OF_SUPPLY_VALUES = set(enum_values(ClassOfSupply))
ENVIRONMENT_VALUES = set(enum_values(Environment))


VALID_ELEMENT_MAP = {
    "name": st.text(),
    "description": st.text(),
    "class_of_supply": st.sampled_from(ClassOfSupply),
    "type": st.just(ElementKind.Element),
    "environment": st.sampled_from(Environment),
    "accommodation_mass": NON_NEGATIVE_FINITE_FLOATS,
    "mass": NON_NEGATIVE_FINITE_FLOATS,
    "volume": NON_NEGATIVE_FINITE_FLOATS,
}
INVALID_ELEMENT_MAP = {
    "class_of_supply": st.text().filter(lambda s: s not in CLASS_OF_SUPPLY_VALUES),
    "type": st.sampled_from(ElementKind).filter(lambda ty: ty != ElementKind.Element),
    "environment": st.text().filter(lambda s: s not in ENVIRONMENT_VALUES),
    "accommodation_mass": NEGATIVE_AND_INFINITE_FLOATS,
    "mass": NEGATIVE_AND_INFINITE_FLOATS,
    "volume": NEGATIVE_AND_INFINITE_FLOATS,
}


VALID_RESOURCE_CONTAINER_MAP = dict(
    VALID_ELEMENT_MAP,
    type=st.just(ElementKind.ResourceContainer),
    max_cargo_mass=st.one_of(st.none(), NON_NEGATIVE_FINITE_FLOATS),
    max_cargo_volume=st.one_of(st.none(), NON_NEGATIVE_FINITE_FLOATS),
)
INVALID_RESOURCE_CONTAINER_MAP = dict(
    INVALID_ELEMENT_MAP,
    type=st.sampled_from(ElementKind).filter(
        lambda ty: ty != ElementKind.ResourceContainer
    ),
    max_cargo_mass=NEGATIVE_AND_INFINITE_FLOATS,
    max_cargo_volume=NEGATIVE_AND_INFINITE_FLOATS,
)


VALID_ELEMENT_CARRIER_MAP = dict(
    VALID_ELEMENT_MAP,
    type=st.just(ElementKind.ElementCarrier),
    cargo_environment=st.sampled_from(Environment),
    max_cargo_mass=st.one_of(st.none(), NON_NEGATIVE_FINITE_FLOATS),
    max_cargo_volume=st.one_of(st.none(), NON_NEGATIVE_FINITE_FLOATS),
)
INVALID_ELEMENT_CARRIER_MAP = dict(
    INVALID_ELEMENT_MAP,
    type=st.sampled_from(ElementKind).filter(
        lambda ty: ty != ElementKind.ElementCarrier
    ),
    cargo_environment=st.text().filter(lambda s: s not in ENVIRONMENT_VALUES),
    max_cargo_mass=NEGATIVE_AND_INFINITE_FLOATS,
    max_cargo_volume=NEGATIVE_AND_INFINITE_FLOATS,
)


VALID_HUMAN_AGENT_MAP = dict(
    VALID_ELEMENT_MAP,
    active_time_fraction=st.floats(min_value=0, max_value=1),
    type=st.just(ElementKind.HumanAgent),
)
INVALID_HUMAN_AGENT_MAP = dict(
    INVALID_ELEMENT_MAP,
    active_time_fraction=st.one_of(
        st.floats(max_value=0, exclude_max=True),
        st.floats(min_value=1, exclude_min=True),
    ),
    type=st.sampled_from(ElementKind).filter(lambda ty: ty != ElementKind.HumanAgent),
)


VALID_ROBOTIC_AGENT_MAP = dict(
    VALID_HUMAN_AGENT_MAP, type=st.just(ElementKind.RoboticAgent),
)
INVALID_ROBOTIC_AGENT_MAP = dict(
    INVALID_HUMAN_AGENT_MAP,
    type=st.sampled_from(ElementKind).filter(lambda ty: ty != ElementKind.RoboticAgent),
)


VALID_PROPULSIVE_VEHICLE_MAP = dict(
    VALID_ELEMENT_MAP,
    type=st.just(ElementKind.PropulsiveVehicle),
    max_crew=st.integers(min_value=0, max_value=SQLITE_MAX_INT),
    isp=NON_NEGATIVE_FINITE_FLOATS,
    max_fuel=NON_NEGATIVE_FINITE_FLOATS,
    propellant_id=st.integers(min_value=SQLITE_MIN_INT, max_value=SQLITE_MAX_INT),
    max_cargo_mass=st.one_of(st.none(), NON_NEGATIVE_FINITE_FLOATS),
    max_cargo_volume=st.one_of(st.none(), NON_NEGATIVE_FINITE_FLOATS),
)
INVALID_PROPULSIVE_VEHICLE_MAP = dict(
    INVALID_ELEMENT_MAP,
    type=st.sampled_from(ElementKind).filter(
        lambda ty: ty != ElementKind.PropulsiveVehicle
    ),
    max_crew=st.one_of(st.integers(max_value=-1), UNSERIALIZABLE_INTS),
    isp=NEGATIVE_AND_INFINITE_FLOATS,
    max_fuel=NEGATIVE_AND_INFINITE_FLOATS,
    propellant_id=UNSERIALIZABLE_INTS,
    max_cargo_mass=NEGATIVE_AND_INFINITE_FLOATS,
    max_cargo_volume=NEGATIVE_AND_INFINITE_FLOATS,
)

VALID_SURFACE_VEHICLE_MAP = dict(
    VALID_ELEMENT_MAP,
    type=st.just(ElementKind.SurfaceVehicle),
    max_crew=st.integers(min_value=0, max_value=SQLITE_MAX_INT),
    max_speed=NON_NEGATIVE_FINITE_FLOATS,
    max_fuel=NON_NEGATIVE_FINITE_FLOATS,
    fuel_id=st.integers(min_value=SQLITE_MIN_INT, max_value=SQLITE_MAX_INT),
    max_cargo_mass=st.one_of(st.none(), NON_NEGATIVE_FINITE_FLOATS),
    max_cargo_volume=st.one_of(st.none(), NON_NEGATIVE_FINITE_FLOATS),
)
INVALID_SURFACE_VEHICLE_MAP = dict(
    INVALID_ELEMENT_MAP,
    type=st.sampled_from(ElementKind).filter(
        lambda ty: ty != ElementKind.SurfaceVehicle
    ),
    max_crew=st.one_of(st.integers(max_value=-1), UNSERIALIZABLE_INTS),
    max_speed=NEGATIVE_AND_INFINITE_FLOATS,
    max_fuel=NEGATIVE_AND_INFINITE_FLOATS,
    fuel_id=UNSERIALIZABLE_INTS,
    max_cargo_mass=NEGATIVE_AND_INFINITE_FLOATS,
    max_cargo_volume=NEGATIVE_AND_INFINITE_FLOATS,
)
