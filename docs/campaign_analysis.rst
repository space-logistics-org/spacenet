=================
Campaign Analysis
=================

SpaceNet analyzes campaign-scale logistics: the campaign horizon, crew
consumables over time, cost, launch cadence, and the design life of elements.

-----------------
Scenario End Date
-----------------

By default (as in the reference implementation), a simulation ends with its
last event, so elements which remain in place afterwards (e.g., a surface
outpost or Gateway) generate no further demands. A scenario can define an
``endDate`` to set the campaign horizon instead: after the last event, the
simulators advance to the end date, over which elements generate demands
(including part failures and time-phased crew consumables), power groups
balance their energy, ISRU processes operate, tanks boil off, and the design
life of elements is checked. Crew time and crew surface days accumulate to
the end date. Demands at a node after its last arrival are aggregated to that
arrival (supply point) for the manifest.

Events after the end date are not simulated (events at the end date are),
including the remainder of transports in progress; the simulator warns which
missions have events after the end date. The end date must be after the
start date. The :class:`~spacenet.simulation.PreSimulator` honors a time
after the end date (to inspect the state before an event which is not
simulated) but otherwise stops at the end date.

----------------------------
Time-Phased Crew Consumables
----------------------------

By default (as in the reference implementation), a mission's crew
consumables demand model demands all consumables on arrival at the mission
destination, for durations derived from the mission's transports. With the
configuration option ``timePhasedConsumables``, the simulator instead
demands, over each interval between events, the daily consumables (water,
food, gases, hygiene, clothing, and waste) of each crew member of the mission
where the crew member is (outside the surface of Earth, including
transports). The items which each crew member carries (kits, personal
items, suits, and equipment), with reserves, and the equipment shared by the
mission are demanded when the crew first leaves Earth; EVA consumables remain
demanded on arrival. Demands are satisfied by resources at the crew's
location (e.g., logistics delivered to Gateway) or left to the manifest.

----
Cost
----

Element templates (and instances) can define a ``unitCost``, incurred when
an element is first created, and edges a ``costPerTransport``, incurred for
each transport along the edge (e.g., a launch service or ground operations).
Costs are in millions of US dollars as defined (then-year, not
inflation-adjusted). The simulation reports a
:class:`~spacenet.simulation.analysis.CostAnalysis` with costs by mission,
year, and category, and the campaign cost as a measure of effectiveness.

--------------------------
Cadence and Design Life
--------------------------

An edge can define a ``minDepartureInterval`` (days), e.g., the cadence of a
launch pad; the simulator warns when a transport departs sooner after the
previous transport along the edge. An element can define a ``designLife``
(years); the simulator warns (once) when an element is used beyond it.

----------------------
In the Web Application
----------------------

The *Cost* view of the *Simulation* tab charts cost by year and tabulates it
by mission; the *Timeline* view charts where each element is over the
campaign (in transit, in orbit, on a surface beyond Earth, or on Earth)
through the scenario end date, which is set in the header. The element
template editor defines unit costs and design lives, and the edge editor
defines costs per transport and minimum departure intervals.

--------------------------
Reference Artemis Campaign
--------------------------

The reference campaign uses published costs (NASA OIG production and
operations costs of SLS and Orion, HLS contract values, and Gateway contract
and launch values), the ADD's annual cadence of crewed SLS launches, the
design lives of Gateway (15 years), Fission Surface Power (10 years), and the
terrain vehicle (10 years), time-phased crew consumables, and Gateway
logistics deliveries (Dragon XL) which supply the crew at Gateway. See
:doc:`validation`.
