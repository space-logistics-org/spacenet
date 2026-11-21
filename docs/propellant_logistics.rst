====================
Propellant Logistics
====================

SpaceNet models the propellant logistics of campaigns which refuel vehicles
in space, such as a Starship-class Human Landing System (HLS) refueled in low
Earth orbit from a depot filled by tanker flights.

-------------------
Modeling Propellant
-------------------

**Tanks.** The fuel tank (:class:`~spacenet.schemas.elements.propulsion.ResourceTank`)
of a propulsion system can define a ``boiloffRate``: the fraction of the tank
*capacity* lost per day (e.g., ``0.001`` for 0.1 %/day). Heat leaks into a
cryogenic tank in proportion to its surface area rather than its contents,
so the loss is a constant mass per day until the tank is empty. Boiloff is
removed over the time elapsed between events, except for vehicles on the
surface of Earth (which are assumed to be topped off before launch), and is
reported as a loss rather than as a demand.

**Bipropellant systems.** A propulsion system can burn oxidizer from a
separate ``oxidizerTank`` (or the ``sharedOxidizerTank`` of another system of
the same vehicle) in a fixed oxidizer-to-fuel ``mixtureRatio`` by mass. A burn
draws ``1 / (1 + MR)`` of the propellant mass from the fuel tank and
``MR / (1 + MR)`` from the oxidizer tank, and is limited by whichever runs out
first. Systems without an oxidizer tank burn a single (combined) propellant.

**Transfers.** A *Transfer Resources* event moves resources between resource
containers and the integral tanks of vehicles:

* ``originTank`` / ``destinationTank`` select a tank of a vehicle (``OMS Fuel``,
  ``OMS Oxidizer``, ``RCS Fuel``, ``RCS Oxidizer``); by default, the tanks
  which hold the transferred resources are used.
* ``transferMode`` transfers the listed amounts (``Amount``, the default), as
  much as possible to fill the destination (``Fill Destination``), or as much
  as possible to empty the origin (``Empty Origin``). The resource list is
  optional for the latter two: all resources of the origin are transferred
  to the destination tanks which hold them.
* ``lossFraction`` is the fraction of the removed resources lost in transfer.

--------
Analysis
--------

The full simulation (:class:`~spacenet.simulation.analysis.SimulationAnalysis`)
reports a :class:`~spacenet.simulation.analysis.PropellantAnalysis` with the
contents of each vehicle tank over time and a budget which closes:
loaded + added + transferred in − transferred out − transfer loss − burned −
boiloff − consumed = residual. The total propellant burned, lost to boiloff,
and lost in transfers are measures of effectiveness. Draft burn events report
the ``propellantShortfall``: the additional propellant a vehicle would need
to achieve the remaining delta-v (accounting for the mass of the added
propellant).

:func:`~spacenet.simulation.analysis.size_tankers` estimates the number of
tanker flights needed to aggregate a required propellant mass in a depot,
accounting for boiloff between flights and transfer losses.

In the web application, the *Propellant* view of the *Simulation* tab charts
tank contents and losses by vehicle, exports the budgets, and sizes tanker
campaigns; the element template editor defines boiloff rates and bipropellant
systems; and the transfer event editor previews each transfer.

--------------------------
Reference Artemis Campaign
--------------------------

``artemis/artemis_add_campaign.py`` generates a reference campaign following
the program of record in NASA's Moon-to-Mars Architecture Definition Document
(Artemis I-V, Gateway, and propellant aggregation for each landing). All values
are notional; change them with ``CampaignParameters`` (with the ``artemis``
directory on the Python path):

.. code-block:: python

    from artemis_add_campaign import CampaignParameters, build_scenario

    scenario = build_scenario(CampaignParameters(depot_boiloff_rate=0.001))
