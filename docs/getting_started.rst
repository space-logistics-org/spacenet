.. role:: console(code)
   :language: console

===============
Getting Started
===============

------------
Installation
------------

To install SpaceNet, clone this repository and run the following console/terminal command from the project root directory:

.. code-block:: console
    :caption: Console command to install SpaceNet

    pip install -e .

The installer additionally provides the following optional dependencies:
 * :console:`pip install -e .[docs]`: dependencies required to build documentation
 * :console:`pip install -e .[lint]`: dependencies required for development
 * :console:`pip install -e .[test]`: dependencies required for running unit tests
 * :console:`pip install -e .[app]`: dependencies required for the web application

Multiple optional dependencies can be installed with a comma-delimited list (e.g., :console:`pip install -e .[lint,app]`)

-----
Usage
-----

To use the SpaceNet library in a Python script, import the ``spacenet`` package as follows:

.. code-block:: python
    :caption: Python statement to import SpaceNet library

    import spacenet

To run the SpaceNet web application (note: requires the :console:`pip install -e .[app]` installation), run the following console/terminal command from the project root directory:

.. code-block:: console
    :caption: Command to launch SpaceNet web application

    uvicorn spacenet_app.main:app --host 0.0.0.0 --port 8000

The application will be available in a browser at `<http://localhost:8000>`_.

--------------
User Interface
--------------

The web application serves a browser-based user interface to build a campaign scenario, create a manifest, and visualize simulation results. No login is required. The scenario is kept in the browser (and saved automatically between sessions): use *Open* and *Save* to load and store scenario files (JSON). All analysis and simulation is performed by the web application through its application programming interface (documented at `<http://localhost:8000/docs>`_ under the ``/api`` prefix).

 * *Load Database* reads a model database (Excel) such as ``quick_start/quick_start_1.xlsx`` which provides a library of nodes, edges, resources, and element templates. A propulsive vehicle defines an orbital maneuvering system (``oms_isp``, ``max_oms``, and ``oms_id`` columns) and/or a reaction control system (``rcs_isp``, ``max_rcs``, and ``rcs_id`` columns; without a fuel capacity it shares the fuel tank of the orbital maneuvering system) and each burn defines the ``type`` of propulsion system (OMS or RCS) which performs it. The objects of an opened scenario are also available as a library.
 * *Models* browses the library to add, edit, copy, and delete nodes, edges, resources, element templates (with their states, demand models, and parts), and demand models. Models of the scenario and new models are saved with the scenario; changes to models which are only part of the loaded database are kept in the browser. Models which are used by other objects cannot be deleted.
 * **Network**: select the nodes and edges of the scenario from the library (or add and edit them).
 * **Missions**: add missions and their events. The dialog of an event shows the elements which are at its location at its time and evaluates each change (errors, capacities, and the change in velocity achieved by a sequence of burns). Errors are reported for each mission and event as the scenario is edited.
 * **Demands**: review the demands of the scenario by element, mission, and location and compare them to the capacity of the transports which could supply them. Demands can be exported as delimited text.
 * **Manifest**: pack demands in logistics containers and load the containers in the carriers of transports, manually or automatically. The manifest is saved with the scenario and can be exported as delimited text.
 * **Simulation**: run the full simulation to review its errors, the location of elements over time, and the measures of effectiveness.

To try the user interface, open ``quick_start/completed_quick_start_2_w_db.json``, review the *Demands* tab, select *Auto-Manifest* in the *Manifest* tab, and select *Simulate* in the *Simulation* tab.

The user interface loads the Bootstrap and Plotly libraries from a content delivery network and therefore requires an internet connection.

-------------
Configuration
-------------

The SpaceNet web application accepts the following environment variables, optionally defined in a ``.env`` file placed in the project root directory:

 * ``SPACENET_ADMIN_EMAIL``: administrator user account email address (default: ``admin@example.com``)
 * ``SPACENET_ADMIN_PASSWORD``: administrator user password (default: ``admin``)
 * ``SPACENET_DB_URL``: user database uniform reference locator (default: ``sqlite+aiosqlite:///./spacenet-users.db``)
 * ``SPACENET_SESSION_SECRET``: secret for cryptographic encryption (default: ``change me``)
 * ``SPACENET_SESSION_LIFETIME``: session lifetime (seconds) for JSON web token (JWT) and cookie authentication (default: ``7200``)

.. code-block:: text
    :caption: Example .env File

    SPACENET_ADMIN_EMAIL=admin@custom.com
    SPACENET_ADMIN_PASSWORD=password