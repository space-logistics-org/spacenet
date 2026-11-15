==========
Simulation
==========

.. automodule:: spacenet.simulation

A simulator executes the events of a :class:`spacenet.schemas.Scenario` as a
discrete event simulation. The scenario is never modified: each simulation
builds a new :class:`spacenet.simulation.State` composed of mutable simulation
objects (network, elements, missions, and events). Simulation time is
expressed in days relative to the scenario start date.

.. code-block:: python
    :caption: Example simulation of a scenario

    from spacenet.schemas import Scenario
    from spacenet.simulation import (
        AggregatedDemandsAnalysis,
        DemandSimulator,
        FullSimulator,
    )

    with open("scenario.json", encoding="utf-8") as scenario_file:
        scenario = Scenario.model_validate_json(scenario_file.read())

    # simulate the scenario and report errors and measures of effectiveness
    simulator = FullSimulator(scenario)
    simulator.simulate()
    for error in simulator.spatial_errors:
        print(error.time, error)
    print(simulator.total_launch_mass, simulator.total_crew_surface_days)

    # log all demands (without consuming available resources) and aggregate
    # them to the transports which could supply them
    simulator = DemandSimulator(scenario, demands_satisfied=False)
    simulator.simulate()
    analysis = AggregatedDemandsAnalysis.create(simulator)
    print(analysis.model_dump_json(by_alias=True, indent=2))

Simulators collect warnings, errors, and unsatisfied demands rather than
raising exceptions. Events additionally report their progress using the
``spacenet.simulation`` logger at the ``INFO`` level (and warnings and errors
at the ``WARNING`` level) which can be displayed by configuring logging (e.g.,
``logging.basicConfig(level=logging.INFO)``).

Simulators
==========

.. autoclass:: spacenet.simulation.Simulator
  :members:

.. autoclass:: spacenet.simulation.FullSimulator
  :members:

.. autoclass:: spacenet.simulation.DemandSimulator
  :members:

.. autoclass:: spacenet.simulation.PreSimulator
  :members:

.. autoclass:: spacenet.simulation.MiniSimulator
  :members:

State
=====

.. autoclass:: spacenet.simulation.State
  :members:

.. autoclass:: spacenet.simulation.Settings
  :members:

.. autoclass:: spacenet.simulation.SimMission
  :members:

Network
=======

.. autoclass:: spacenet.simulation.SimNetwork
  :members:

.. autoclass:: spacenet.simulation.SimLocation
  :members:
  :inherited-members:

.. autoclass:: spacenet.simulation.SimNode
  :members:

.. autoclass:: spacenet.simulation.SimEdge
  :members:

.. autoclass:: spacenet.simulation.SimBurn
  :members:

Resources
=========

.. autoclass:: spacenet.simulation.SimResource
  :members:

.. autoclass:: spacenet.simulation.Demand
  :members:

.. autoclass:: spacenet.simulation.DemandSet
  :members:

Elements
========

.. autoclass:: spacenet.simulation.SimElement
  :members:

.. autoclass:: spacenet.simulation.SimCarrier
  :members:

.. autoclass:: spacenet.simulation.SimPropulsiveVehicle
  :members:

.. autoclass:: spacenet.simulation.SimPropulsionSystem
  :members:

.. autoclass:: spacenet.simulation.SimSurfaceVehicle
  :members:

.. autoclass:: spacenet.simulation.SimResourceContainer
  :members:

.. autoclass:: spacenet.simulation.SimResourceTank
  :members:

.. autoclass:: spacenet.simulation.SimCrewMember
  :members:

.. autoclass:: spacenet.simulation.SimRoboticAgent
  :members:

.. autoclass:: spacenet.simulation.OperationalState
  :members:

.. autoclass:: spacenet.simulation.PartApplication
  :members:

Demand Models
=============

.. autoclass:: spacenet.simulation.SimDemandModel
  :members:

.. autoclass:: spacenet.simulation.SimTimedImpulseDemandModel
  :members:

.. autoclass:: spacenet.simulation.SimRatedDemandModel
  :members:

.. autoclass:: spacenet.simulation.SimSparingByMassDemandModel
  :members:

.. autoclass:: spacenet.simulation.SimCrewConsumablesDemandModel
  :members:

Events
======

.. autoclass:: spacenet.simulation.SimEvent
  :members:

.. autoclass:: spacenet.simulation.MissionEvent

.. autoclass:: spacenet.simulation.CreateEvent

.. autoclass:: spacenet.simulation.MoveEvent

.. autoclass:: spacenet.simulation.RemoveEvent

.. autoclass:: spacenet.simulation.ReconfigureEvent

.. autoclass:: spacenet.simulation.ReconfigureGroupEvent

.. autoclass:: spacenet.simulation.AddEvent

.. autoclass:: spacenet.simulation.TransferEvent

.. autoclass:: spacenet.simulation.DemandEvent

.. autoclass:: spacenet.simulation.BurnEvent

.. autoclass:: spacenet.simulation.EvaEvent

.. autoclass:: spacenet.simulation.ExplorationProcess
  :members: number_eva, hours_between_eva

.. autoclass:: spacenet.simulation.TransportEvent
  :members: elements, duration, origin, destination

.. autoclass:: spacenet.simulation.SpaceTransportEvent

.. autoclass:: spacenet.simulation.FlightTransportEvent

.. autoclass:: spacenet.simulation.SurfaceTransportEvent
  :members: is_reversed

Errors and Warnings
===================

.. autoclass:: spacenet.simulation.SimError

.. autoclass:: spacenet.simulation.SimSpatialError

.. autoclass:: spacenet.simulation.SimDemand

.. autoclass:: spacenet.simulation.SimWarning

Records
=======

.. autoclass:: spacenet.simulation.NetworkSnapshot
  :members:

.. autoclass:: spacenet.simulation.ElementSnapshot
  :members:

.. autoclass:: spacenet.simulation.LocationSnapshot
  :members:

.. autoclass:: spacenet.simulation.SimRepair

.. autoclass:: spacenet.simulation.SimScavenge

.. autoclass:: spacenet.simulation.MoeCrewSurfaceDays

.. autoclass:: spacenet.simulation.MoeCrewTime

.. autoclass:: spacenet.simulation.MoeExplorationCapability

.. autoclass:: spacenet.simulation.MoeExplorationMassDelivered

.. autoclass:: spacenet.simulation.MoeLaunchMass

.. autoclass:: spacenet.simulation.MoeMassCapacityUtilization

Supply Network
==============

.. autoclass:: spacenet.simulation.SupplyEdge
  :members:

.. autoclass:: spacenet.simulation.SupplyPoint
  :members:

.. autoclass:: spacenet.simulation.RepairItem
  :members:

Demand Analysis
===============

.. autopydantic_model:: spacenet.simulation.RawDemandsAnalysis
  :members:
  :inherited-members: CamelModel

.. autopydantic_model:: spacenet.simulation.RawDemand
  :members:
  :inherited-members: CamelModel

.. autopydantic_model:: spacenet.simulation.AggregatedDemandsAnalysis
  :members:
  :inherited-members: CamelModel

.. autopydantic_model:: spacenet.simulation.NodeDemand
  :members:
  :inherited-members: CamelModel

.. autopydantic_model:: spacenet.simulation.EdgeDemand
  :members:
  :inherited-members: CamelModel

.. autopydantic_model:: spacenet.simulation.DemandsAnalysis
  :members:
  :inherited-members: CamelModel

Manifest
========

A manifest packs the demands aggregated by a demand simulator in logistics
containers and loads the containers in the carriers of transports. The full
simulator loads the containers of the scenario manifest at the departure of
each transport.

.. code-block:: python
    :caption: Example automatic manifest of a scenario

    from spacenet.simulation import FullSimulator, SimManifest

    manifest = SimManifest.create(scenario)
    manifest.auto_manifest()
    scenario = scenario.model_copy(update={"manifest": manifest.to_schema()})
    simulator = FullSimulator(scenario)
    simulator.simulate()

.. autoclass:: spacenet.simulation.SimManifest
  :members:

.. autoclass:: spacenet.simulation.SimManifestContainer
  :members:

.. autoclass:: spacenet.simulation.ManifestDemand
  :members:

.. autofunction:: spacenet.simulation.container_factory

.. autoclass:: spacenet.simulation.ManifestEvent
  :members:

Analysis
========

Analyses report the results of simulations as object schemas, e.g., for the
application programming interface of the web application.

.. autopydantic_model:: spacenet.simulation.SimIssue
  :members:
  :inherited-members: CamelModel

.. autopydantic_model:: spacenet.simulation.MissionsAnalysis
  :members:
  :inherited-members: CamelModel

.. autopydantic_model:: spacenet.simulation.StateAnalysis
  :members:
  :inherited-members: CamelModel

.. autopydantic_model:: spacenet.simulation.EventEvaluation
  :members:
  :inherited-members: CamelModel

.. autopydantic_model:: spacenet.simulation.ManifestAnalysis
  :members:
  :inherited-members: CamelModel

.. autopydantic_model:: spacenet.simulation.SimulationAnalysis
  :members:
  :inherited-members: CamelModel

.. autoclass:: spacenet.simulation.ScenarioError
  :members:
