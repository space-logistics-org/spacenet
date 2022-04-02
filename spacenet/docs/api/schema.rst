.. _schema:

================
SpaceNet Schemas
================

.. toctree::
   :maxdepth: 1

Database
===============

.. automodule:: spacenet.schemas
   :members:

Nodes
------

.. autoclass:: spacenet.schemas.node.NodeType
   :members:

.. autoclass:: spacenet.schemas.node.NodeUUID
   :members:

.. autoclass:: spacenet.schemas.node.Node
   :members:

.. autoclass:: spacenet.schemas.node.SurfaceNode
   :members:

.. autoclass:: spacenet.schemas.node.OrbitalNode
   :members:

.. autoclass:: spacenet.schemas.node.LagrangeNode
   :members:



Edges
-------

.. autoclass:: spacenet.schemas.edge.EdgeType
   :members:

.. autoclass:: spacenet.schemas.edge.EdgeUUID
   :members:

.. autoclass:: spacenet.schemas.edge.SpaceEdge
   :members:

.. autoclass:: spacenet.schemas.edge.SurfaceEdge
   :members:

.. autoclass:: spacenet.schemas.edge.FlightEdge
   :members:



Elements
--------

.. autoclass:: spacenet.schemas.element.ElementKind
   :members: 

.. autoclass:: spacenet.schemas.element.ElementUUID
   :members:  

.. autoclass:: spacenet.schemas.element.Element
   :members:  

.. autoclass:: spacenet.schemas.element.ResourceContainer
   :members:  

.. autoclass:: spacenet.schemas.element.Element
   :members:  

.. autoclass:: spacenet.schemas.element.ResourceContainer
   :members: 

.. autoclass:: spacenet.schemas.element.ElementCarrier
   :members:  

.. autoclass:: spacenet.schemas.element.HumanAgent
   :members: 

.. autoclass:: spacenet.schemas.element.RoboticAgent
   :members:  

.. autoclass:: spacenet.schemas.element.PropulsiveVehicle
   :members: 

.. autoclass:: spacenet.schemas.element.SurfaceVehicle
   :members: 


Instantiated Elements
----------------------

.. autoclass:: spacenet.schemas.inst_element.InstElementUUID
   :members:  

.. autoclass:: spacenet.schemas.inst_element.InstElement
   :members:  

.. autoclass:: spacenet.schemas.inst_element.InstResourceContainer
   :members:  

.. autoclass:: spacenet.schemas.inst_element.InstElement
   :members:  

.. autoclass:: spacenet.schemas.inst_element.InstResourceContainer
   :members: 

.. autoclass:: spacenet.schemas.inst_element.InstElementCarrier
   :members:  

.. autoclass:: spacenet.schemas.inst_element.InstHumanAgent
   :members: 

.. autoclass:: spacenet.schemas.inst_element.InstRoboticAgent
   :members:  

.. autoclass:: spacenet.schemas.inst_element.InstPropulsiveVehicle
   :members: 

.. autoclass:: spacenet.schemas.inst_element.InstSurfaceVehicle
   :members: 


Resources
----------

.. autoclass:: spacenet.schemas.resource.ResourceType
   :members:

.. autoclass:: spacenet.schemas.resource.ResourceUUID
   :members:

.. autoclass:: spacenet.schemas.resource.Resource
   :members:

.. autoclass:: spacenet.schemas.resource.ContinuousResource
   :members:

.. autoclass:: spacenet.schemas.resource.DiscreteResource
   :members:

States
-------

.. autoclass:: spacenet.schemas.state.StateType
   :members:

.. autoclass:: spacenet.schemas.state.StateUUID
   :members:

.. autoclass:: spacenet.schemas.state.State
   :members:



Campaign
=========

Element Events
----------------

.. autoclass:: spacenet.schemas.element_events.MakeElements
   :members:

.. autoclass:: spacenet.schemas.element_events.MoveElements
   :members:

.. autoclass:: spacenet.schemas.element_events.RemoveElements
   :members:

.. autoclass:: spacenet.schemas.element_events.ReconfigureElements
   :members:

Transport Events
-----------------

.. autoclass:: spacenet.schemas.flight_transport.FlightTransport
   :members:

.. autoclass:: spacenet.schemas.space_transport.SpaceTransport
   :members:

.. autoclass:: spacenet.schemas.surface_transport.SurfaceTransport
   :members:

.. autoclass:: spacenet.schemas.propulsive_burn.PropulsiveBurn
   :members:

.. autoclass:: spacenet.schemas.burn.Burn
   :members:

Resource Events
-----------------

.. autoclass:: spacenet.schemas.transfer_resources.TransferResources
   :members:

.. autoclass:: spacenet.schemas.consume_resource.ConsumeResource
   :members:

Mission Demand Models
----------------------

.. autoclass:: spacenet.schemas.mission_demand_model.MissionDemandUUID
   :members:

.. autoclass:: spacenet.schemas.mission_demand_model.TimedImpulseDemandModel
   :members:

.. autoclass:: spacenet.schemas.mission_demand_model.RatedDemandModel
   :members:

.. autoclass:: spacenet.schemas.mission_demand_model.CrewConsumablesDemandModel
   :members:

Element Demand Models
----------------------

.. autoclass:: spacenet.schemas.element_demand_model.DemandModelUUID
   :members:

.. autoclass:: spacenet.schemas.element_demand_model.CrewConsumablesDemandModel
   :members:

.. autoclass:: spacenet.schemas.element_demand_model.TimedImpulseDemandModel
   :members:

.. autoclass:: spacenet.schemas.element_demand_model.RatedDemandModel
   :members:

.. autoclass:: spacenet.schemas.element_demand_model.SparingByMassDemandModel
   :members:


Exploration Events
-------------------

.. autoclass:: spacenet.schemas.crewed_eva.CrewedEVA
   :members:

.. autoclass:: spacenet.schemas.crewed_exploration.CrewedExploration
   :members:


High Level Schemas
-------------------

.. autoclass:: spacenet.schemas.mission.Mission
   :members:

.. autoclass:: spacenet.schemas.scenario.Scenario
   :members: