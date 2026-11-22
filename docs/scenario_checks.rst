===============
Scenario Checks
===============

Before a scenario is simulated, SpaceNet checks it for **errors**, which
prevent its simulation or would make it invalid, and **warnings**, which
are likely mistakes. All issues are reported at once, each with a stable
code, a description, and the path of the field in the JSON representation
of the scenario (as used by :doc:`trade_studies`), e.g.
``missionList/0/events/2/missionTime``.

Errors prevent simulation: the simulators raise a
:class:`~spacenet.simulation.ScenarioError` (with all errors attached), and
the web application responds with status 422 and one item per error, which
it shows above the tabs. Warnings are logged by the simulators as warnings
of their events (or missions), e.g., in the *Missions* tab.

--------------
Running Checks
--------------

.. code-block:: python

    from spacenet.lint import lint_scenario

    for issue in lint_scenario(scenario):
        print(issue)  # e.g., Error [negative-time] missionList/0/events/0/missionTime: ...

From the command line, ``python -m spacenet.lint scenario.json`` prints the
issues of one or more scenario files and exits with status 1 if any has
errors (or does not match the object schema), e.g., to check scenario files
in continuous integration. The endpoint ``POST /api/scenario/lint`` returns
the issues of a scenario.

------
Errors
------

==========================  ===================================================
Code                        Problem
==========================  ===================================================
duplicate-id                Two nodes or edges, elements, element templates,
                            resources, demand models, or burns share a unique
                            identifier, or a location shares one with an
                            element (an element may share the identifier of
                            its template).
unknown-node                An edge or a mission references a missing node.
unknown-location            An event references a missing location.
unknown-element             An event, a location, or a carrier references a
                            missing element.
unknown-edge                A transport references a missing edge.
unknown-burn                A propulsive burn references a missing burn.
unknown-template            An element instantiates a missing element template.
unknown-resource            A resource amount, a tank, or a part references a
                            missing resource.
unknown-demand-model        A demand model instantiates a missing demand model.
demand-model-type-mismatch  A demand model has a different type than the demand
                            model it instantiates.
wrong-element-type          An element cannot fill its role: a container
                            which is not a location or an element carrier, a
                            crew habitat which is not an element carrier, or
                            a surface transport vehicle which is not a
                            surface vehicle.
wrong-edge-type             A transport references an edge of another type.
invalid-state-index         An element's current state, a reconfiguration, a
                            crew activity, or a surface transport selects a
                            state which the element does not have.
negative-time               An event is before the start of its mission, or a
                            burn before the start of its transport.
before-scenario-start       A mission starts before the scenario start date.
negative-amount             Added or transferred resources, the initial
                            contents of a resource container, or a tank have
                            a negative amount. (Consumed resources may be
                            negative, which produces them.)
multiple-containers         An element is initially inside more than one
                            carrier or location.
containment-cycle           A carrier (recursively) contains itself.
==========================  ===================================================

--------
Warnings
--------

==========================  ===================================================
Code                        Problem
==========================  ===================================================
loop-edge                   An edge has the same origin and destination.
burn-after-arrival          A burn of a space edge is after the end of its
                            transport.
duplicate-name              Resources share a name.
over-capacity               The initial contents of a resource container or
                            a tank exceed its capacity.
template-type-mismatch      An element has a different type than its template.
transport-location          A flight or space transport is not located at the
                            origin of its edge (or a surface transport at
                            either end).
burn-not-on-edge            A space transport sequences a burn which is not a
                            burn of its edge, so the sequence is ignored.
not-propulsive              A burn action fires an element which is not a
                            propulsive vehicle.
created-twice               An element is created by more than one event.
==========================  ===================================================

Events after the scenario end date are reported by the simulators rather
than by these checks (see :doc:`campaign_analysis`).

-----------------
Capacity Messages
-----------------

When an element or a resource cannot be added to a carrier, a resource
container, or a tank during simulation, the error describes the constraint
which prevents it, e.g., "Heavy could not be added to Carrier: its cargo
mass would be 6,000.00 kg, above its capacity of 5,000.00 kg." The
constraints are the crew capacity, the cargo mass (including the capacity of
the carrier in which a carrier is nested), the cargo volume and environment
(when the configuration enables volume and environment constraints), and the
contents of a tank.
