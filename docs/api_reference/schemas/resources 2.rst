=========
Resources
=========

.. automodule:: spacenet.schemas.resources

Custom Resource Types
=====================

Discrete Resource
-----------------

.. autopydantic_model:: spacenet.schemas.DiscreteResource
  :members:
  :inherited-members: CamelModel

Continuous Resource
-------------------

.. autopydantic_model:: spacenet.schemas.ContinuousResource
  :members:
  :inherited-members: CamelModel

Custom Resources
================

Resource Amount
---------------

.. autopydantic_model:: spacenet.schemas.ResourceAmount
  :members:
  :inherited-members: CamelModel

Resource Amount Rate
--------------------

.. autopydantic_model:: spacenet.schemas.ResourceAmountRate
  :members:
  :inherited-members: CamelModel

Generic Resources
=================

Generic Resource Amount
-----------------------

.. autopydantic_model:: spacenet.schemas.GenericResourceAmount
  :members:
  :inherited-members: CamelModel

Generic Resource Amount Rate
----------------------------

.. autopydantic_model:: spacenet.schemas.GenericResourceAmountRate
  :members:
  :inherited-members: CamelModel

Environment
===========

.. autoenum:: spacenet.schemas.Environment

Class of Supply
===============

.. autoenum:: spacenet.schemas.ClassOfSupply
