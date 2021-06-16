import unittest
import json
import pkg_resources
from pydantic import ValidationError


from spacenet.schemas import node as nos
from spacenet import test

class TestingData(unittest.TestCase):
    
    def test_OrbitalNode(self): 
        
        nodes_data = json.loads(
            pkg_resources.resource_string(
                test.__name__,
                'goodNodes.txt'
            )
        )  
             
        for nodes in nodes_data: 
            
            if nodes["type"] == "Orbital" : 
                testnode = nos.OrbitalNode(**nodes)
                self.assertEqual(testnode.name , nodes.get("name"))
                self.assertEqual(testnode.description , nodes.get("description"))
                self.assertEqual(testnode.body_1 , nodes.get("body_1"))
                self.assertEqual(testnode.type , nodes.get("type"))
                self.assertEqual(testnode.apoapsis , nodes.get("apoapsis"))
                self.assertEqual(testnode.periapsis , nodes.get("periapsis"))
                self.assertEqual(testnode.inclination , nodes.get("inclination"))
                
    def test_SurfaceNode(self): 
        
        nodes_data = json.loads(
            pkg_resources.resource_string(
                test.__name__,
                'goodNodes.txt'
            )
        ) 
             
        for nodes in nodes_data: 
            
            if nodes["type"] == "Surface" : 
                testnode = nos.SurfaceNode(**nodes)
                self.assertEqual(testnode.name , nodes.get("name"))
                self.assertEqual(testnode.description , nodes.get("description"))
                self.assertEqual(testnode.body_1 , nodes.get("body_1"))
                self.assertEqual(testnode.type , nodes.get("type"))
                self.assertEqual(testnode.latitude , nodes.get("latitude"))
                self.assertEqual(testnode.longitude , nodes.get("longitude"))

    def test_LagrangeNode(self): 
        
        nodes_data = json.loads(
            pkg_resources.resource_string(
                test.__name__,
                'goodNodes.txt'
            )
        ) 
             
        for nodes in nodes_data: 
            
            if nodes["type"] == "Lagrange" :        
                testnode = nos.LagrangeNode(**nodes)
                self.assertEqual(testnode.name , nodes.get("name"))
                self.assertEqual(testnode.description , nodes.get("description"))
                self.assertEqual(testnode.body_1 , nodes.get("body_1"))
                self.assertEqual(testnode.type , nodes.get("type"))
                self.assertEqual(testnode.body_2 , nodes.get("body_2"))
                self.assertEqual(testnode.lp_number , nodes.get("lp_number"))

    def test_BadOrbitalNode(self):  
        node={"type" : "Orbtial", "name" : "test", "body_1" : "Mars", "apoapsis" : 10000, "periapsis" : "3000", "inclination" : 70, "description" : "String is not valid periapsis"}
        with self.assertRaises(ValidationError):
            bad_node = nos.OrbitalNode(**node)
            
    def test_BadSurfaceNode(self):  
        node = {"type" : "Surface", "name" : "Test1", "body_1" : "Earth", "latitude" : True, "longitude" : True, "description" : "True is not valid Long/Lat"}
        with self.assertRaises(ValidationError):
            bad_node = nos.OrbitalNode(**node)

    def test_BadLagrangeNode(self):  
        node = {"type" : "Lagrange", "name" : "Test5", "body_1" : "Mars", "body_2" : "Sun", "lp_number" : 6, "description" : "6 is not valid LP number"}
        with self.assertRaises(ValidationError):
            bad_node = nos.LagrangeNode(**node)
       
# To test, run : python -m unittest spacenet.test.test_nodeSchema
                
            
