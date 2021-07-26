import unittest
import json
import pkg_resources
import pytest
from sqlalchemy.orm import sessionmaker

from spacenet.schemas import test

from app.database.api.models import node as models
from app.database.api.schemas import node as schemas
from app.database.api.database import Base, engine
from spacenet.schemas import NodeType

pytestmark = [pytest.mark.unit, pytest.mark.node, pytest.mark.database]

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class TestNodeData(unittest.TestCase):
    nodes_data = json.loads(
        pkg_resources.resource_string(
            test.__name__,
            'good_nodes.json'
        )
    )

    def setUp(self):
        Base.metadata.create_all(bind=engine)
        self.db = TestingSessionLocal()

    def tearDown(self):
        self.db.close()

    def test_model_good_nodes(self):

        for node in self.nodes_data:

            if node["type"] == NodeType.Orbital.value:
                testnode = schemas.OrbitalNode.parse_obj(node)
                db_node = models.OrbitalNode(**testnode.dict())
                self.assertIsNone(db_node.id)
                self.db.add(db_node)
                self.db.commit()
                self.db.refresh(db_node)
                self.assertIsNotNone(db_node.id)
                self.assertIsNotNone(db_node.name)
                self.assertIsNotNone(db_node.body_1)
                self.assertIsNotNone(db_node.apoapsis)
                self.assertIsNotNone(db_node.periapsis)
                self.assertIsNotNone(db_node.inclination)
                self.assertIsNotNone(db_node.description)
                self.db.delete(db_node)
                self.db.commit()

            elif node["type"] == NodeType.Surface.value:
                testnode = schemas.SurfaceNode.parse_obj(node)
                db_node = models.SurfaceNode(**testnode.dict())
                self.assertIsNone(db_node.id)
                self.db.add(db_node)
                self.db.commit()
                self.db.refresh(db_node)
                self.assertIsNotNone(db_node.id)
                self.assertIsNotNone(db_node.name)
                self.assertIsNotNone(db_node.body_1)
                self.assertIsNotNone(db_node.latitude)
                self.assertIsNotNone(db_node.longitude)
                self.assertIsNotNone(db_node.description)
                self.db.delete(db_node)
                self.db.commit()

            elif node["type"] == NodeType.Lagrange.value:
                testnode = schemas.LagrangeNode.parse_obj(node)
                db_node = models.LagrangeNode(**testnode.dict())
                self.assertIsNone(db_node.id)
                self.db.add(db_node)
                self.db.commit()
                self.db.refresh(db_node)
                self.assertIsNotNone(db_node.id)
                self.assertIsNotNone(db_node.name)
                self.assertIsNotNone(db_node.body_1)
                self.assertIsNotNone(db_node.body_2)
                self.assertIsNotNone(db_node.lp_number)
                self.assertIsNotNone(db_node.description)
                self.db.delete(db_node)
                self.db.commit()

# To test, run : python -m unittest app.database.test.test_nodeDatabaseModel
