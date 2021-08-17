"""
This module contains tests that the lunar sortie schema parses.
"""
import pytest

from .utilities import (
    lunar_sortie_elements,
    lunar_sortie_edges,
    lunar_sortie_nodes,
    lunar_sortie_resources,
    KIND_TO_SCHEMA,
)

pytestmark = [pytest.mark.unit, pytest.mark.schema, pytest.mark.lunar_sortie]


@pytest.mark.parametrize(
    "domain_objects",
    (
        pytest.param(
            pytest.lazy_fixture("lunar_sortie_" + obj_type + "s"),
            marks=getattr(pytest.mark, obj_type),
        )
        for obj_type in ["element", "edge", "node", "resource"]
    ),
)
def test_schema_with_lunar_sortie_data(domain_objects):
    for obj in domain_objects:
        schema_cls = KIND_TO_SCHEMA[obj["type"]]
        domain_object = schema_cls.parse_obj(obj)
        for attr, value in obj.items():
            assert value == getattr(domain_object, attr)
