from spacenet.schemas import ReadSchema, State, OptionalFields


__all__ = ["State", "StateUpdate", "StateRead"]


class StateUpdate(State, OptionalFields):
    """
    A variant of the State schema which is used for Update queries.
    """

    pass


class StateRead(State, ReadSchema):
    """
    The variant of the State schema returned from queries; includes an ID.
    """

    pass
