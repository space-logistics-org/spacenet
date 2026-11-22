=================
Campaign Analysis
=================

SpaceNet analyzes campaign-scale logistics: the campaign horizon, crew
consumables over time, cost, launch cadence, the design life of elements, and
campaign measures of efficiency and sustainability.

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

-----------------
Campaign Measures
-----------------

In addition to the measures of effectiveness of the reference implementation
(crew surface days, crew time, exploration capability, exploration mass
delivered, launch mass, and capacity utilization), the full simulation
reports measures of the efficiency and sustainability of a campaign. Each has
a total (``totals``) and a history by time and location (``measures``).

Launch mass per landed mass
    The mass launched from Earth divided by the *landed mass*: the total mass
    of the elements (including landers and their remaining propellant) which
    arrive by space or flight transports on the surface of a body other than
    Earth, from a node which is not on the surface of that body. Landed mass
    is recorded at arrival, i.e., after the burns of the transport and
    excluding staged elements. It is 0 if nothing is landed.

Logistics mass per crew-day
    The *logistics mass* (the mass of resources demanded by elements, crew,
    and missions at locations other than the surface of Earth, whether or not
    the demands are satisfied) divided by the *crew-days* away from the
    surface of Earth (including transports). Propellant burned by transports
    is not a demand and is not logistics mass. It is 0 without crew-days.

Days of supply on hand
    After each interval between events, at each location with demands for
    continuous resources over the interval, the time until the first of
    them runs out at the rate demanded over the interval: the amount which
    the elements at the location could supply (from their containers, tanks,
    and nested contents, following the substitution rules for generic
    resources) divided by the demand rate. The history records the limiting
    resource as the record type; the total is the fewest days of supply at
    any location and time (``minDaysOfSupply``, undefined without such
    demands). Discrete resources (e.g., spare parts) are excluded because
    their demands are lumpy over short intervals, as are mission-level
    demands, which are demanded at once. A value of 0 indicates demands which
    could not be satisfied; the fewest days of supply of a campaign which
    delivers exactly its demands approaches 0 before each resupply, so the
    measure is a reserve margin.

Earth independence
    The fraction of the mass of resources consumed beyond Earth orbit (to
    satisfy demands, or burned by vehicles) which was produced in situ by
    ISRU processes. Consumption at Earth's surface or orbital nodes, or on
    edges departing them (e.g., trans-lunar injection), is excluded;
    Lagrange nodes such as NRHO are beyond Earth orbit. Resources produced in
    situ are attributed to consumption of the same resource (by name) before
    resources delivered from Earth, in order of time but irrespective of
    location, and resources which ISRU processes consume (e.g., water
    electrolyzed to oxygen) are not consumption. The history records the
    consumed mass by source (``In Situ`` or ``Earth``). It is 0 without
    consumption beyond Earth orbit.

All are available as metrics of :doc:`trade_studies` (an undefined fewest
days of supply is not a number).

----------------------
In the Web Application
----------------------

The *Cost* view of the *Simulation* tab charts cost by year and tabulates it
by mission; the *Timeline* view charts where each element is over the
campaign (in transit, in orbit, on a surface beyond Earth, or on Earth)
through the scenario end date, which is set in the header. The element
template editor defines unit costs and design lives, and the edge editor
defines costs per transport and minimum departure intervals. The *Measures*
view charts the campaign measures over time by location (days of supply as
levels, the others accumulated), and the summary tabulates their totals.

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
