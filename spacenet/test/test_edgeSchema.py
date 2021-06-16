import unittest
import json
import pkg_resources
from pydantic import ValidationError

from spacenet.schemas import edge as eos
from spacenet import test

class TestingData(unittest.TestCase):
    
    def test_FlightEdge(self): 
        
        edge_data = json.loads(
            pkg_resources.resource_string(
                test.__name__,
                'goodEdges.txt'
            )
        ) 
             
        for edge in edge_data: 
            
            if edge["type"] == "Flight" : 
                testedge = eos.FlightEdge(**edge)
                self.assertEqual(testedge.name , edge.get("name"))
                self.assertEqual(testedge.origin_id , edge.get("origin_id"))
                self.assertEqual(testedge.destination_id, edge.get("destination_id"))
                self.assertEqual(testedge.duration , edge.get("duration"))
                self.assertEqual(testedge.max_crew , edge.get("max_crew"))
                self.assertEqual(testedge.max_cargo , edge.get("max_cargo"))
                self.assertEqual(testedge.description , edge.get("description"))
                
    def test_SpaceEdge(self): 
        
        edge_data = json.loads(
            pkg_resources.resource_string(
                test.__name__,
                'goodEdges.txt'
            )
        ) 
             
        for edge in edge_data: 
            
            if edge["type"] == "Space" : 
                testedge = eos.SpaceEdge(**edge)
                self.assertEqual(testedge.name , edge.get("name"))
                self.assertEqual(testedge.origin_id , edge.get("origin_id"))
                self.assertEqual(testedge.destination_id, edge.get("destination_id"))
                self.assertEqual(testedge.duration , edge.get("duration"))
                self.assertEqual(testedge.description , edge.get("description"))

    def test_SurfaceEdge(self): 
        
        edge_data = json.loads(
            pkg_resources.resource_string(
                test.__name__,
                'goodEdges.txt'
            )
        )  
             
        for edge in edge_data: 
            
            if edge["type"] == "Surface" :        
                testedge = eos.SurfaceEdge(**edge)
                self.assertEqual(testedge.name , edge.get("name"))
                self.assertEqual(testedge.origin_id , edge.get("origin_id"))
                self.assertEqual(testedge.destination_id, edge.get("destination_id"))
                self.assertEqual(testedge.distance , edge.get("distance"))
                self.assertEqual(testedge.description , edge.get("description"))

    def test_BadFlightEdge(self):  
        edge = { "type" : "Flight", "name" : "Test1", "origin_id" : 1, "destination_id" : 2, "duration" : 25, "max_crew" : 6, "max_cargo" : -100, "description" : "Invalid max_cargo input." }    
        with self.assertRaises(ValidationError):
                bad_edge = eos.FlightEdge(**edge)
            
    def test_BadSurfaceEdge(self):  
        edge = { "type" : "Space", "name" : "Test3", "origin_id" : 3, "destination_id" : 2.5, "duration" : 25, "description" : "Invalid destination_id input." }         
        with self.assertRaises(ValidationError):
            bad_edge = eos.SurfaceEdge(**edge)

    def test_BadSpaceEdge(self):  
        edge = { "type" : "Surface", "name" : "Test5", "origin_id" : 5, "destination_id" : 2, "description" : "Invalid distance type."} 
        with self.assertRaises(ValidationError):
            bad_edge = eos.SpaceEdge(**edge)
       
# To test, run : python -m unittest spacenet.test.test_edgeSchema
