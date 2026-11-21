==================
Surface Operations
==================

SpaceNet models the electrical power of elements and the energy and fuel
which surface vehicles consume to traverse between sites, e.g., at the lunar
south pole.

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

--------
Analysis
--------

The full simulation reports a
:class:`~spacenet.simulation.analysis.PowerAnalysis` with the generation,
consumption, stored energy, and deficit of each power group over time, and
the total energy deficit as a measure of effectiveness. Element states
include their stored energy.

In the web application:

* the *Power* view of the *Simulation* tab charts the power and stored
  energy of each group and tabulates the energy totals of all groups;
* the *Network* tab maps the surface sites of each body other than Earth
  with the distances of surface edges;
* the element template editor defines power by state, energy storage, grid
  connection, and traverse consumption; the node editor defines illumination
  and the longest night; and the surface transport editor previews the
  distance, speed, fuel, and energy of a traverse.

The reference Artemis campaign (``artemis/artemis_add_campaign.py``) delivers
fission surface power, a science station, and a terrain vehicle to a grid at
the south pole and includes a terrain vehicle traverse between two sites.
