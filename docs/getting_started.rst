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