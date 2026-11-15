=================
Element Templates
=================

.. automodule:: spacenet.schemas.elements.templates

Element
=======

.. autopydantic_model:: spacenet.schemas.Element
  :members:
  :inherited-members: CamelModel

Resource Container
==================

.. autopydantic_model:: spacenet.schemas.ResourceContainer
  :members:
  :inherited-members: CamelModel

Element Carrier
===============

.. autopydantic_model:: spacenet.schemas.ElementCarrier
  :members:
  :inherited-members: CamelModel

Propulsive Vehicle
==================

.. autopydantic_model:: spacenet.schemas.PropulsiveVehicle
  :members:
  :inherited-members: CamelModel

Propulsion System
=================

A propulsive vehicle nests one or more propulsion systems with distinct types
(orbital maneuvering system or reaction control system). Each propulsion
system has a specific impulse and burns fuel from its own fuel tank or from
the fuel tank of another propulsion system of the vehicle. A burn fires the
propulsion system which matches its type.

.. autoclass:: spacenet.schemas.PropulsionType
  :members:
  :undoc-members:

.. autopydantic_model:: spacenet.schemas.PropulsionSystem
  :members:
  :inherited-members: CamelModel

Resource Tank
=============

.. autopydantic_model:: spacenet.schemas.ResourceTank
  :members:
  :inherited-members: CamelModel

Surface Vehicle
===============

.. autopydantic_model:: spacenet.schemas.SurfaceVehicle
  :members:
  :inherited-members: CamelModel

Robotic Agent
=============

.. autopydantic_model:: spacenet.schemas.RoboticAgent
  :members:
  :inherited-members: CamelModel

Human Agent
===========

.. autopydantic_model:: spacenet.schemas.HumanAgent
  :members:
  :inherited-members: CamelModel

Miscellaneous
=============

State Type
----------

.. autoenum:: spacenet.schemas.StateType

State
-----

.. autopydantic_model:: spacenet.schemas.State
  :members:
  :inherited-members: CamelModel

Part
----

.. autopydantic_model:: spacenet.schemas.Part
  :members:
  :inherited-members: CamelModel