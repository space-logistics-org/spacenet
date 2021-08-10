__all__ = [
    "SimException",
    "EventDateOverflowError",
    "UnrecognizedEdgeEndpoint",
    "UnrecognizedID",
    "MismatchedIDType",
]


class SimException(Exception):
    """
    Base class for exceptions raised during simulation.
    """

    pass


class EventDateOverflowError(SimException, OverflowError):
    """
    Exception representing the dates in an event being too large to be represented in a
    datetime object.
    """

    pass


class UnrecognizedEdgeEndpoint(SimException, ValueError):
    """
    Exception representing that an edge has an endpoint which is not a node in the network.
    """

    pass


class UnrecognizedID(SimException, ValueError):
    """
    Exception representing that an ID was found which does not refer to an entity in
    simulation.
    """

    pass


class MismatchedIDType(SimException, TypeError):
    """
    Exception representing that the type of the entity being referenced by the ID is not
    suitable as it's being used, although the UUID does refer to an entity in the simulation.
    """

    pass
