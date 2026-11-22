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

-------
Results
-------

.. include:: validation_results.md
   :parser: myst_parser.sphinx_
