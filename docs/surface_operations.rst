==================
Surface Operations
==================

SpaceNet models the electrical power of elements, the energy and fuel which
surface vehicles consume to traverse between sites, e.g., at the lunar south
pole, and the in-situ production of resources.

-----
Power
-----

**Generation and consumption.** Each operational state of an element can
define a ``powerConsumption`` and a ``powerGeneration`` (kW). Generation is
``Constant`` by default (e.g., fission or radioisotope power) or ``Solar``,
in which case the generated power is scaled by the ``illumination`` of the
location (the average fraction of time in sunlight of a surface node; 1
elsewhere).

**Energy storage.** An element template (or instance) can define an
``energyStorage`` with a ``capacity`` and an initial ``charge`` (kWh; full by
default).

**Power groups.** Between events, the simulator balances the energy of each
power group: a top-level element with its (nested) contents, except that all
elements which are ``gridConnected`` at the same surface node share one grid.
Surplus energy charges the storage of the group (up to its capacity) and
deficits discharge it. Energy which cannot be supplied is reported as a
deficit (with one warning per group). Power is not constrained on the surface
of Earth.

**Lunar night.** A surface node can define its ``maxNightDuration`` (hours of
the longest continuous darkness). A solar-powered group which stays at a node
for at least a day-night cycle (29.5 days on the Moon, 1.03 days on Mars)
must store enough energy to supply its load (less constant generation)
through the longest night; otherwise the simulator warns. Shorter stays can
be scheduled in sunlight.

--------------
Surface Travel
--------------

A surface vehicle can define the ``fuelConsumption`` (units per km) drawn
from its fuel tank and the ``energyConsumption`` (kWh per km) drawn from its
energy storage when it departs on a surface transport. A transport fails if
the vehicle lacks the fuel or energy for the distance of the surface edge,
and warns if its speed exceeds the ``maxSpeed`` of the vehicle.

**Crewed traverses.** Crew members inside a surface vehicle travel with it.
A surface vehicle can define its ``maxCrewedDuration`` (hours), the longest
traverse with crew aboard (e.g., the EVA suit endurance of an unpressurized
rover or the life support of a pressurized rover); a longer crewed traverse
fails. Crew of an unpressurized rover (whose cargo environment is
unpressurized) must also stay within its ``walkBackDistance`` (km) of a
pressurized safe haven: a pressurized carrier with room for the crew (e.g., a
lander, habitat, or pressurized rover) at the origin or destination. With a
safe haven at one end, the crew travels up to the distance of the edge from
it; with safe havens at both ends, up to half of it. The simulator warns if
this exceeds the walk-back distance or if there is no safe haven. A
pressurized rover is its own safe haven and is limited only by its crew
capacity and crewed duration.

--------------------------------
In-Situ Resource Utilization
--------------------------------

An ``ISRU Process`` demand model of an element state converts input resources
and electrical power to output resources, replacing the negative rates of a
``Rated`` demand model (which produce resources from nothing). At its full
rate, a process consumes its ``inputs`` and produces its ``outputs`` (units
per day) with its ``power`` (kW). Between events, the simulator operates each
process of an element in its current state at the rate allowed by:

* its inputs, drawn from the element, its carrier, or other elements at its
  location (resource containers and vehicle tanks); feedstock collected in
  situ (e.g., regolith or icy regolith) is not modeled as an input;
* the storage for its outputs: the element itself (if it is a resource
  container) or tanks and containers which already hold the output resource,
  e.g., the propellant tanks of a lander at the same site;
* its power: processes use the power which remains in their power group after
  other consumption (proportionally to their requests) without discharging
  energy storage, so production follows the average illumination of a
  solar-powered site.

A process which cannot operate at all (no input, storage, or power) warns
once for each constraint. A process whose input is the output of another
process uses the stock at the start of each interval.

--------
Analysis
--------

The full simulation reports a
:class:`~spacenet.simulation.analysis.PowerAnalysis` with the generation,
consumption, stored energy, and deficit of each power group over time, and
the total energy deficit as a measure of effectiveness. Element states
include their stored energy. An
:class:`~spacenet.simulation.analysis.ISRUAnalysis` reports the rate, limiting
constraint, power, and cumulative production of each ISRU process over time,
its energy per kg of its first output, and the total production and energy as
measures of effectiveness.

In the web application:

* the *Power* view of the *Simulation* tab charts the power and stored
  energy of each group and tabulates the energy totals of all groups;
* the *ISRU* view charts the cumulative production and rate of each process
  and tabulates the production, energy, and limiting constraints of all
  processes; the demand model editors define the inputs, outputs, and power
  of a process;
* the *Network* tab maps the surface sites of each body other than Earth
  with the distances of surface edges;
* the element template editor defines power by state, energy storage, grid
  connection, and traverse consumption; the node editor defines illumination
  and the longest night; and the surface transport editor previews the
  distance, speed, fuel, and energy of a traverse.

The reference Artemis campaign (``artemis/artemis_add_campaign.py``) delivers
fission surface power, a science station, a terrain vehicle, and an ISRU
pilot plant to a grid at the south pole. During Artemis V, the crew drives the
terrain vehicle to a second site within its walk-back distance for an EVA and
returns.

The pilot plant follows NASA's lunar water pilot plant conceptual design
(Linne et al., ASCEND 2020): 1,000 kg of oxygen per year from 1,125 kg of
water extracted from icy regolith in a permanently shadowed region and
electrolyzed, liquefied, and stored on a ridge, with 1,165 kg of plant mass
and 6.7 kW of power during 225 days of operation per year. On fission surface
power, the plant operates continuously at the same annual production and
energy (4.13 kW), or 36 kWh per kg of oxygen (an upper bound, since the
published powers include intermittent loads). The Artemis V HLS loads the
oxygen produced before its arrival (about 490 kg) before ascent; at pilot
scale, this is less than 0.1% of the oxygen of a Starship-class HLS, which
illustrates the scale of production needed to refuel landers on the surface.
