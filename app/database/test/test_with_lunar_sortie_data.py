import pytest
from spacenet.schemas.test.utilities import (
    lunar_sortie_elements,
    lunar_sortie_edges,
    lunar_sortie_nodes,
    lunar_sortie_resources,
    KIND_TO_SCHEMA,
)
from .utilities import db
from ..api.models.utilities import SCHEMA_TO_MODEL

pytestmark = [pytest.mark.unit, pytest.mark.database, pytest.mark.lunar_sortie]


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
def test_database_with_lunar_sortie_data(domain_objects, db):
    for obj in domain_objects:
        obj_type = obj["type"]
        schema_cls = KIND_TO_SCHEMA[obj_type]
        domain_object = schema_cls.parse_obj(obj)
        model_ctor = SCHEMA_TO_MODEL[schema_cls]
        db_domain_obj = model_ctor(**domain_object.dict())
        db.add(db_domain_obj)
        db.commit()
        for attr, value in obj.items():
            assert value == getattr(db_domain_obj, attr)
        assert isinstance(db_domain_obj.id, int)
        db.delete(db_domain_obj)
        db.commit()
