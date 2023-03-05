# SpaceNet

SpaceNet is a software platform for simulation and analysis of space exploration campaign logistics.

## Project Structure

The `app/` directory contains SpaceNet web applications. The `database` application provides an editor for a database of common space exploration components such as network locations, resource types, and exploration elements. The `campaign` application constructs and analyzes space exploration campaigns.

The `spacenet/` directory contains Python library functions to define SpaceNet objects and corresponding simulation and analysis routines.

## Dependencies, Installation, and Use

This project requires Python 3.7 with `setuptools`.

To install the SpaceNet library, navigate to the top-level spacenet directory and run the following command:

```
pip install -e .
```

To install SpaceNet dependencies, run:
```shell
python -m pip install spacenet/
python -m pip install app/
```

To configure SpaceNet secrets for administrator accounts, set the following environment variables to their desired 
values:
```
SPACENET_ADMIN_EMAIL
SPACENET_ADMIN_PASSWORD
SPACENET_AUTH_SECRET
```

To launch the SpaceNet application, run:
```shell
uvicorn app.src.main:app --reload-dir app --reload-dir spacenet
```
The default address is http://localhost:8000.

## Running Tests

Modules within `spacenet` and `app` have separate `test` submodules. All tests can be run via `pytest`,
and most supported markers are described in the top-level `pytest.ini` file. In addition to the markers
supported by pytest, an additional `hypothesis` marker exists for running property-based tests.

## Credits

This project is a collaboration between Stevens Institute of Technology and Massachusetts Institute of Technology.
