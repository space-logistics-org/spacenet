=============
Trade Studies
=============

A trade study simulates variations of a scenario and compares their
measures of effectiveness (:mod:`spacenet.trades`).

---------
Variables
---------

A variable sets a field of the scenario, addressed by a path in its JSON
representation, to each of a list of values. Paths separate keys, list
indices, and list selectors with ``/``; a selector ``key=value`` selects the
first list item whose key equals the value, for example:

* ``elementTemplates/name=HLS/mass`` (the dry mass of the HLS template);
* ``elementTemplates/name=HLS/propulsionSystems/0/fuelTank/boiloffRate``;
* ``network/edges/name=LLO-LSP/burns/1/deltaV`` (the lunar descent burn);
* ``configuration/timePhasedConsumables``.

A study combines its variables in a full-factorial design (every
combination) or one at a time (each value of each variable with the others
at their values in the scenario). Each case reports its errors, warnings,
unsatisfied demands (count and mass), and the total measures of
effectiveness (e.g., launch mass, propellant boiloff, energy deficit, and
campaign cost). Cases with invalid values report an error instead.

.. code-block:: python

    from spacenet.trades import TradeStudy, Variable, run_trade

    study = TradeStudy(
        variables=[
            Variable(
                name="descent",
                path="network/edges/name=LLO-LSP/burns/1/deltaV",
                values=[1900, 2050, 2200],
            )
        ],
        metrics=["errorCount", "propellantBurnedMass"],
    )
    result = run_trade(scenario, study, workers=4)

In the web application, the *Trades* tab defines variables by object, item,
and numeric field, runs the study on the server (in parallel processes for
six or more cases), and charts a metric against the first variable with one
line for each value of the second.

-----------------------------------
Sensitivity of the Artemis Campaign
-----------------------------------

Some parameters of the reference campaign change its structure (e.g., the
number of tanker flights), so ``artemis/trades.py`` varies the parameters of
the campaign generator one at a time, regenerates, and simulates the
campaign. The HLS dry mass is the dominant uncertainty: with the published
delta-v budget, the notional 100 t HLS returns with 3.7 t of propellant, an
85 t HLS with 17 t, and a 110 t HLS cannot complete its mission. A tanker
delivery of 100 t requires 13 tanker flights per landing (near the 14 of the
2021 GAO estimate), and depot boiloff of 0.2% per day nearly triples the
propellant lost to boiloff over the campaign without changing the number of
tanker flights.

.. include:: trade_results.md
   :parser: myst_parser.sphinx_

-----------------------
Monte Carlo Reliability
-----------------------

Parts of element templates can define a mean time to failure (MTTF) and a
duty cycle. With part failures enabled (configuration ``partFailures``), each
unit of a part fails at a constant rate while it operates (for its duty
cycle while its element is in an active state, except on the surface of
Earth), and each failure demands a spare part from the element, its carrier,
or the elements at its location. Failures are either ``Expected`` (the mean
number of failures, for deterministic demand estimates) or ``Random`` (a
Poisson-distributed number with the ``randomSeed``). A failure without an
available spare is an unsatisfied demand (a shortfall); it does not change
the operation of the element.

A Monte Carlo study (:mod:`spacenet.reliability`) simulates a scenario
repeatedly with random failures (run ``i`` uses the seed ``seed + i``) and
reports, for each part, the expected number of failures, the mean, standard
deviation, percentiles, and histogram of the simulated failures, and the
probability and mean size of a shortfall of spares, as well as the
probability that any part runs short.

.. code-block:: python

    from spacenet.reliability import MonteCarloStudy, run_monte_carlo

    result = run_monte_carlo(scenario, MonteCarloStudy(runs=500, seed=0), workers=4)
    for part in result.parts:
        print(part.part, part.mean, part.shortfall_probability)

In the web application, the *Trades* tab runs a Monte Carlo study on the
server and tabulates the parts with a histogram of the failures of each, and
the *Options* dialog sets the part failure model of the scenario.

The reference campaign gives the ISRU pilot plant a notional electrolyzer
stack (MTTF 20,000 h) and four excavator drive actuators (MTTF 25,000 h each)
with a spares kit of one stack and three actuators. ``artemis/reliability.py``
simulates the campaign 500 times: over the 509 days that the plant operates,
the simulated probabilities of exhausting the spares agree with the Poisson
distribution of failures (a verification of the model), one in four runs
exhausts the spares of at least one part, and one more spare of each part
would reduce the risk of each shortfall below 5%.

.. include:: reliability_results.md
   :parser: myst_parser.sphinx_
