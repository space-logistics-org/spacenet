import json
import pkg_resources
import pytest
from typing import List, Tuple, Type
from uuid import UUID

from hypothesis import strategies as st
from hypothesis.strategies import SearchStrategy
from pydantic import BaseModel, ValidationError

from spacenet import schemas
from spacenet.schemas.constants import SQLITE_MAX_INT, SQLITE_MIN_INT
from spacenet.schemas.element import *
from spacenet.schemas.edge import FlightEdge, SpaceEdge, SurfaceEdge, EdgeType
from spacenet.schemas.node import SurfaceNode, OrbitalNode, LagrangeNode, NodeType
from spacenet.schemas.resource import DiscreteResource, ContinuousResource, ResourceType

__all__ = [
    "lunar_sortie_elements",
    "lunar_sortie_edges",
    "lunar_sortie_nodes",
    "lunar_sortie_resources",
    "success_from_kw",
    "xfail_from_kw",
    "KIND_TO_SCHEMA",
    "INVALID_UUIDS",
    "INVALID_INTS",
    "UNSERIALIZABLE_INTS",
    "valid_invalid_from_allowed",
]


@pytest.fixture(params=["altair", "ares_1", "ares_5", "orion", "sortie_elements"])
def lunar_sortie_elements(request):
    yield json.loads(
        pkg_resources.resource_string(
            schemas.__name__, f"lunar_sortie/{request.param}.json"
        )
    )


@pytest.fixture()
def lunar_sortie_edges():
    yield json.loads(
        pkg_resources.resource_string(
            schemas.__name__, "lunar_sortie/sortie_edges.json"
        )
    )


@pytest.fixture()
def lunar_sortie_nodes():
    yield json.loads(
        pkg_resources.resource_string(
            schemas.__name__, "lunar_sortie/sortie_nodes.json"
        )
    )


@pytest.fixture()
def lunar_sortie_resources():
    yield json.loads(
        pkg_resources.resource_string(schemas.__name__, "lunar_sortie/fuels.json")
    )


KIND_TO_SCHEMA = {
    ElementKind.Element: Element,
    ElementKind.ElementCarrier: ElementCarrier,
    ElementKind.ResourceContainer: ResourceContainer,
    ElementKind.HumanAgent: HumanAgent,
    ElementKind.RoboticAgent: RoboticAgent,
    ElementKind.PropulsiveVehicle: PropulsiveVehicle,
    ElementKind.SurfaceVehicle: SurfaceVehicle,
    EdgeType.Surface: SurfaceEdge,
    EdgeType.Flight: FlightEdge,
    EdgeType.Space: SpaceEdge,
    NodeType.Surface: SurfaceNode,
    NodeType.Orbital: OrbitalNode,
    NodeType.Lagrange: LagrangeNode,
    ResourceType.Discrete: DiscreteResource,
    ResourceType.Continuous: ContinuousResource,
}


def is_valid_uuid(s: str) -> bool:
    """
    Return true if s can be converted into a valid UUID, and false otherwise.

    :param s: value to check if can be converted into a valid UUID
    :return: true if s can be converted into a valid UUID, false otherwise
    >>> is_valid_uuid("hello")
    False
    >>> is_valid_uuid("123e4567-e89b-12d3-a456-426614174000")
    True
    """
    try:
        UUID(hex=s)
    except ValueError:
        return False
    else:
        return True


def is_valid_int(s: str) -> bool:
    """
    Return true if s can be converted into a valid integer, and false otherwise.

    :param s: value to check if can be converted into a valid integer
    :return: true if s can be converted into a valid integer, false otherwise
    >>> is_valid_int("hello")
    False
    >>> is_valid_int("506")
    True
    """
    try:
        int(s)
    except ValueError:
        return False
    else:
        return True


INVALID_UUIDS = st.text().filter(lambda s: not is_valid_uuid(s))
INVALID_INTS = st.text().filter(lambda s: not is_valid_int(s))
UNSERIALIZABLE_INTS = st.one_of(
    st.integers(max_value=SQLITE_MIN_INT - 1),
    st.integers(min_value=SQLITE_MAX_INT + 1),
)


def valid_invalid_from_allowed(
    allowed: List[str],
) -> Tuple[SearchStrategy, SearchStrategy]:
    """
    Construct valid and invalid search strategies from a given list of allowed values.

    :param allowed: values which are allowed
    :return: valid and invalid strategies, where valid strategies are those from allowed, and
        the text generated by the two strategies is disjoint
    """
    valid = st.sampled_from(allowed)
    invalid = st.text().filter(lambda s: s not in allowed)
    return valid, invalid


def success_from_kw(type_: Type[BaseModel], **kwargs) -> None:
    """
    Construct an instance of `type_` via provided keyword arguments, and expect both that
    construction is successful and all fields match their expected values in kwargs.

    :param type_: the type to construct
    :param kwargs: keyword arguments to type_ constructor
    """
    event = type_.parse_obj(kwargs)
    for name, val in kwargs.items():
        assert val == getattr(event, name)


def xfail_from_kw(type_: Type[BaseModel], **kwargs) -> None:
    """
    Construct an instance of `type_` via provided keyword arguments, and expect that
    construction fails, raising a ValidationError.

    :param type_: the type to construct
    :param kwargs: keyword arguments to type_ constructor
    """
    with pytest.raises(ValidationError):
        type_.parse_obj(kwargs)
