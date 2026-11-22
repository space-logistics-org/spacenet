==========
Validation
==========

The engineering models of the reference Artemis campaign
(``artemis/artemis_add_campaign.py``) are compared with published NASA and
other data by ``artemis/validation.py`` (run ``python artemis/validation.py``
for a report; the comparisons are also unit tests). The generic tools are in
:mod:`spacenet.validation`.

Each comparison states how the published value relates to the model:

* **validated**: the model value is computed independently of the reference
  (e.g., a launch vehicle capability simulated from stage masses), so the
  comparison tests the model;
* **calibrated**: a model parameter is tuned to reproduce the reference, so
  the comparison only confirms the calibration;
* **input**: the published value is a model input, so the comparison
  confirms traceability.

A comparison passes if the model value lies within the published value (or
range, or bound) widened by its relative *tolerance*: "exact" (none) for
inputs and bounds, and otherwise chosen for the precision of the published
value or of the model (e.g., ±10% for a launch vehicle capability simulated
from stage masses with an equivalent ascent delta-v, ±1% for calibrations
and rounded published values). The *difference* is relative to the nearest
bound of the published value; "in range" denotes a value within a published
range or bound. Each report starts with the number of comparisons of each
kind and any which fail.

--------
Findings
--------

* **Launch vehicles.** Simulated with stage masses and an equivalent ascent
  delta-v of 9,500 m/s, SLS Block 1 sends 25.6 t through trans-lunar
  injection, 5% below the published "more than 27 t". One equivalent ascent
  delta-v cannot reproduce both Block 1 and Block 1B (the exploration upper
  stage burns during ascent), so the Block 1B ascent (10,325 m/s) is
  calibrated to the published 38 t.
* **Lunar transfers.** The delta-v of the 2024 scenario's lunar descent
  (1,712 m/s) and ascent (1,712 m/s) were 16% and 8% below the values which
  NASA publishes for south pole access from NRHO via low lunar orbit (2,050
  and 1,860 m/s), and Orion's NRHO insertion and departure (about 780 m/s)
  were 22% below the as-built 1,000 m/s. The campaign now uses the published
  values; with them, the notional 100 t HLS returns to NRHO with only 0.3% of
  its propellant remaining.
* **Orion.** The 2024 scenario loaded 9,276 kg of propellant in the European
  Service Module; the published usable propellant is 8,602 kg (now used).
  Orion retains a delta-v capability of 1,370 m/s without payload.
* **Propellant aggregation.** Sized for boiloff and transfer losses, the
  campaign needs 9 tanker flights per landing, within published estimates
  (from SpaceX statements of about 8 to 10 to the 14 implied by SpaceX's 2021
  proposal).
* **Crew consumables.** The default rates of the crew consumables demand
  model (from the reference implementation) agree with NASA's 2023 planning
  values for water (-10%) and food (+3%) but overstate oxygen by a factor of
  four (3.86 vs. 0.89 kg per crew-day) and include 2.2 kg per crew-day of
  nitrogen (vs. about 0.02 kg of cabin leakage). The campaign uses the NASA
  planning values; scenarios using the defaults overstate gas logistics.
* **Crew consumables timing.** The mission-level demand model of the
  reference implementation counts the days at a mission destination until
  the next mission starts: for the 10-day Artemis II flyby (whose destination
  is the splash-down site), it demanded 11.7 t of consumables for four crew
  over almost a year. With time-phased crew consumables (configuration
  ``timePhasedConsumables``, used by the campaign), consumables are demanded
  where and when each crew member is away from Earth: 1.0 t for Artemis II,
  matching four crew for 10 days at the planning rates plus carried items,
  reserves, and equipment.
* **Cost.** With the NASA OIG's production and operations costs of SLS ($2.2B),
  Orion ($1.0B), the ESM ($0.3B), and ground systems ($568M per year, one
  launch per year), the simulated cost of an SLS/Orion mission is $4.07B,
  within 1% of the OIG's $4.1B per launch. Published HLS and Gateway contract
  values are inputs; the campaign totals $29.4B (then-year, excluding
  development of SLS and Orion and the uncosted surface systems).
* **Gateway logistics.** One Dragon XL delivery (low-energy transfer of 120
  days, 12 months berthed) supplies the crew at Gateway during Artemis IV and
  V, as the ADD requires (at least one delivery for each Gateway mission of
  30 days); the Artemis III crew in NRHO (before Gateway logistics) and the
  crew in transit or on the surface remain supplied by the manifest.
* **Surface systems.** Fission Surface Power (40 kWe, at most 6,000 kg), the
  terrain vehicle (two suited crew, 10 km walk-back), the pressurized rover
  (two crew, 28-day missions), surface stays (about 6 days), and the
  illumination of the connecting ridge (85%, below the published maximum of
  90%) follow published values.
* **ISRU.** The pilot plant reproduces NASA's lunar water pilot plant design
  (1,000 kg of oxygen per year, 1,165 kg) on fission surface power without
  power or storage limits. Its 8:1 oxygen-to-hydrogen split is within 1% of
  the stoichiometry of water electrolysis (7.94), and its 36 kWh per kg of
  oxygen (the published plant power over 225 days per year, an upper bound)
  exceeds the minimum energy of water electrolysis (4.96 kWh per kg).

------------
Verification
------------

Validation compares the models with published data; verification checks that
the simulator implements them consistently. Besides unit tests of each model,
``tests/simulation/test_invariants.py`` checks invariants which every
simulation must satisfy, for the reference scenarios and for random
scenarios generated from seeds (``tests/simulation/generator.py``):

* time never decreases, and no event executes after the scenario end date;
* each element is in exactly one container, consistent with its parent;
* tanks, resource containers, and energy storage stay within their bounds;
* every change to a vehicle tank is recorded, so the propellant ledger of
  each tank closes (initial contents plus recorded flows equal the final
  contents);
* burns achieve the delta-v of the rocket equation for the propellant used;
* transfers conserve resources (removed equals delivered plus lost);
* the compressed network history composes the simulated states;
* the total mass of closed scenarios (without demands, burns, boiloff, or
  losses) is constant;
* simulations are deterministic (also after a round trip through JSON) and
  do not modify their scenario; and
* the simulators agree on the errors and final locations of a scenario.

Random scenarios include events which fail by design (e.g., over capacity)
so that the invariants are also checked after errors. Each run checks 40 open
and 40 closed scenarios; a slow test (excluded from continuous integration)
checks 960 more of each. A failure names its seed, which reproduces the
scenario with ``random_scenario(seed)``.

------------------------------
Parity with the Reference Code
------------------------------

The simulation was ported from the reference (Java) implementation of
SpaceNet. ``tests/parity/test_java_parity.py`` compares the outputs of the
reference implementation's headless modes (raw demands, aggregated demands,
and automatic manifests, each with and without consuming existing resources)
with the Python implementation for the reference scenarios which it can read
and for random scenarios restricted to the features both share. The outputs
of the reference implementation are stored as fixtures in
``tests/parity/fixtures`` (with the commit which produced them), so the tests
do not require Java; ``python -m tests.parity.generate_fixtures`` regenerates
them (see ``tests/parity/java.py`` to locate the reference implementation).

Raw and aggregated demands match exactly, as do the amounts of each resource
packed for each supply point by the automatic manifest. The containers and
the mass loaded on each transport differ in some scenarios for three known
reasons, which the tests list and check:

* the Python manifest packs any amount of a demand which fits in a container
  (the reference implementation only packs a demand in a container which fits
  all of it), so containers are filled and loaded differently;
* the Python manifest does not load containers on flights which exceed their
  cargo mass capacity (and would then fail during simulation); and
* the reference implementation manifests demands on the surface of Earth,
  carrying them on a round trip from Earth.

Features which the reference implementation lacks (e.g., bipropellant and
multiple propulsion systems, boiloff, power, ISRU, transfers to vehicle tanks,
end dates, time-phased consumables, and part failures) or models in other
units (surface transports) are tested only in the Python implementation.

-------
Results
-------

.. include:: validation_results.md
   :parser: myst_parser.sphinx_
