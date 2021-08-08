__all__ = [
    "SimException",
    "EventDateOverflowError",
    "UnrecognizedEdgeEndpoint",
    "UnrecognizedID",
    "MismatchedIDType",
]


class SimException(Exception):
    pass


class EventDateOverflowError(SimException, OverflowError):
    pass


class UnrecognizedEdgeEndpoint(SimException, ValueError):
    pass


class UnrecognizedID(SimException, ValueError):
    pass


class MismatchedIDType(SimException, TypeError):
    pass
