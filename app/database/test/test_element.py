import unittest
import json
import pkg_resources
import pytest

from spacenet.schemas import test

from app.database.api.models import element as models
from app.database.api.schemas import element as schemas
from app.database.api.database import Base, engine
from .utilities import TestingSessionLocal

pytestmark = [pytest.mark.unit, pytest.mark.element, pytest.mark.database]

class TestElementData(unittest.TestCase):
    
    element_data = json.loads(pkg_resources.resource_string(test.__name__, 'good_elements.json'))

    def setUp(self):
        
        Base.metadata.create_all(bind = engine)
        self.db = TestingSessionLocal()

    def tearDown(self):

        self.db.close()

    def test_model_good_elements(self):

        for element in self.element_data:

            if element["type"] == "Element":
                
                testelement = schemas.Element.parse_obj(element)
                db_element = models.Element(**testelement.dict())
                self.assertIsNone(db_element.id)
                self.db.add(db_element)
                self.db.commit()
                self.db.refresh(db_element)
                self.assertIsNotNone(db_element.id)
                self.assertIsNotNone(db_element.type)
                self.assertIsNotNone(db_element.name)
                self.assertIsNotNone(db_element.description)
                self.assertIsNotNone(db_element.class_of_supply)
                self.assertIsNotNone(db_element.environment)
                self.assertIsNotNone(db_element.accommodation_mass)
                self.assertIsNotNone(db_element.mass)
                self.assertIsNotNone(db_element.volume)
                self.db.delete(db_element)
                self.db.commit()

            elif element["type"] == "ResourceContainer":
                
                testelement = schemas.ResourceContainer.parse_obj(element)
                db_element = models.ResourceContainer(**testelement.dict())
                self.assertIsNone(db_element.id)
                self.db.add(db_element)
                self.db.commit()
                self.db.refresh(db_element)
                self.assertIsNotNone(db_element.id)
                self.assertIsNotNone(db_element.type)
                self.assertIsNotNone(db_element.name)
                self.assertIsNotNone(db_element.description)
                self.assertIsNotNone(db_element.class_of_supply)
                self.assertIsNotNone(db_element.environment)
                self.assertIsNotNone(db_element.accommodation_mass)
                self.assertIsNotNone(db_element.mass)
                self.assertIsNotNone(db_element.volume)
                self.assertIsNotNone(db_element.max_cargo_mass)
                self.assertIsNotNone(db_element.max_cargo_volume)
                self.db.delete(db_element)
                self.db.commit()

            elif element["type"] == "ElementCarrier":
                
                testelement = schemas.ElementCarrier.parse_obj(element)
                db_element = models.ElementCarrier(**testelement.dict())
                self.assertIsNone(db_element.id)
                self.db.add(db_element)
                self.db.commit()
                self.db.refresh(db_element)
                self.assertIsNotNone(db_element.id)
                self.assertIsNotNone(db_element.type)
                self.assertIsNotNone(db_element.name)
                self.assertIsNotNone(db_element.description)
                self.assertIsNotNone(db_element.class_of_supply)
                self.assertIsNotNone(db_element.environment)
                self.assertIsNotNone(db_element.accommodation_mass)
                self.assertIsNotNone(db_element.mass)
                self.assertIsNotNone(db_element.volume)
                self.assertIsNotNone(db_element.max_cargo_mass)
                self.assertIsNotNone(db_element.max_cargo_volume)
                self.assertIsNotNone(db_element.cargo_environment)
                self.db.delete(db_element)
                self.db.commit()

            elif element["type"] == "Propulsive":
                
                testelement = schemas.PropulsiveVehicle.parse_obj(element)
                db_element = models.PropulsiveVehicle(**testelement.dict())
                self.assertIsNone(db_element.id)
                self.db.add(db_element)
                self.db.commit()
                self.db.refresh(db_element)
                self.assertIsNotNone(db_element.id)
                self.assertIsNotNone(db_element.type)
                self.assertIsNotNone(db_element.name)
                self.assertIsNotNone(db_element.description)
                self.assertIsNotNone(db_element.class_of_supply)
                self.assertIsNotNone(db_element.environment)
                self.assertIsNotNone(db_element.accommodation_mass)
                self.assertIsNotNone(db_element.mass)
                self.assertIsNotNone(db_element.volume)
                self.assertIsNotNone(db_element.max_cargo_mass)
                self.assertIsNotNone(db_element.max_cargo_volume)
                self.assertIsNotNone(db_element.max_crew)
                self.assertIsNotNone(db_element.max_fuel)
                self.assertIsNotNone(db_element.isp)
                self.assertIsNotNone(db_element.propellant_id)
                self.db.delete(db_element)
                self.db.commit()

            elif element["type"] == "Surface":
                
                testelement = schemas.SurfaceVehicle.parse_obj(element)
                db_element = models.SurfaceVehicle(**testelement.dict())
                self.assertIsNone(db_element.id)
                self.db.add(db_element)
                self.db.commit()
                self.db.refresh(db_element)
                self.assertIsNotNone(db_element.id)
                self.assertIsNotNone(db_element.type)
                self.assertIsNotNone(db_element.name)
                self.assertIsNotNone(db_element.description)
                self.assertIsNotNone(db_element.class_of_supply)
                self.assertIsNotNone(db_element.environment)
                self.assertIsNotNone(db_element.accommodation_mass)
                self.assertIsNotNone(db_element.mass)
                self.assertIsNotNone(db_element.volume)
                self.assertIsNotNone(db_element.max_cargo_mass)
                self.assertIsNotNone(db_element.max_cargo_volume)
                self.assertIsNotNone(db_element.max_crew)
                self.assertIsNotNone(db_element.max_fuel)
                self.assertIsNotNone(db_element.max_speed)
                self.assertIsNotNone(db_element.fuel_id)
                self.db.delete(db_element)
                self.db.commit()

            elif element["type"] == "HumanAgent":
                
                testelement = schemas.HumanAgent.parse_obj(element)
                db_element = models.HumanAgent(**testelement.dict())
                self.assertIsNone(db_element.id)
                self.db.add(db_element)
                self.db.commit()
                self.db.refresh(db_element)
                self.assertIsNotNone(db_element.id)
                self.assertIsNotNone(db_element.type)
                self.assertIsNotNone(db_element.name)
                self.assertIsNotNone(db_element.description)
                self.assertIsNotNone(db_element.class_of_supply)
                self.assertIsNotNone(db_element.environment)
                self.assertIsNotNone(db_element.accommodation_mass)
                self.assertIsNotNone(db_element.mass)
                self.assertIsNotNone(db_element.volume)
                self.assertIsNotNone(db_element.active_time_fraction)
                self.db.delete(db_element)
                self.db.commit()

            elif element["type"] == "RoboticAgent":
                
                testelement = schemas.RoboticAgent.parse_obj(element)
                db_element = models.RoboticAgent(**testelement.dict())
                self.assertIsNone(db_element.id)
                self.db.add(db_element)
                self.db.commit()
                self.db.refresh(db_element)
                self.assertIsNotNone(db_element.id)
                self.assertIsNotNone(db_element.type)
                self.assertIsNotNone(db_element.name)
                self.assertIsNotNone(db_element.description)
                self.assertIsNotNone(db_element.class_of_supply)
                self.assertIsNotNone(db_element.environment)
                self.assertIsNotNone(db_element.accommodation_mass)
                self.assertIsNotNone(db_element.mass)
                self.assertIsNotNone(db_element.volume)
                self.assertIsNotNone(db_element.active_time_fraction)
                self.db.delete(db_element)
                self.db.commit()
