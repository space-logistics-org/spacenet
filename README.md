# SpaceNet

SpaceNet is a software platform for simulation and analysis of space exploration campaign logistics.

## Project Structure

The `app/` directory contains SpaceNet web applications. The `database` application provides an editor for a database of common space exploration components such as network locations, resource types, and exploration elements. The `campaign` application constructs and analyzes space exploration campaigns.

The `spacenet/` directory contains Python library functions to define SpaceNet objects and corresponding simulation and analysis routines.

## Dependencies, Installation, and Use

This project requires Python 3.7 with `setuptools`.

To install SpaceNet dependencies, run:
```shell
python setup.py install
```

To launch the SpaceNet application, run:
```shell
uvicorn app.main:app --reload-dir app --reload-dir spacenet
```
The default address is http://localhost:8000

## Credits

This project is a collaboration between Stevens Institute of Technology and Massachusetts Institute of Technology.
