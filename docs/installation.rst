.. role:: console(code)
  :language: console

.. role:: python(code)
  :language: python

============
Installation
============

Typical Usage
=============

SpaceNet uses the ``setuptools`` build system within Python to build the library from source.

The simplest way to install SpaceNet is via the terminal/shell command :console:`pip install -e .` from the ``spacenet/`` directory.

Then, SpaceNet is available for use in any Python script by importing :python:`import spacenet`.

Development Usage
=================

Using SpaceNet in a development environment (e.g., unit tests, documentation, etc.) require additional dependencies contained within the ``spacenet/requirements.dev.txt`` file.

Install the development tools via the terminal/shell command :console:`pip install -r requirements.dev.txt` from the ``spacenet/`` directory _prior_ to installing the library with :console:`pip install -e .`.

Run Unit Tests
--------------

Run unit tests from the project root directory with :console:`python -m unittest` or :console:`coverage run -m unittest`.

Build Documentation
-------------------

Build the documentation from the ``docs/`` directory with :console:`make html`.
