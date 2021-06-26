import doctest
from typing import Any, Dict

from app.database.api.database import Base
from app.database.api import models, schemas

__all__ = ["dictify_row", "SCHEMA_TO_MODEL", "MODEL_TO_PARENT"]


def dictify_row(row: Base) -> Dict[str, Any]:
    """
    Convert a database row to a dictionary.

    :param row: row to copy data into dictionary from
    :return: dictionary mapping column names to values
    >>> from sqlalchemy import Column, Integer, Float
    >>> class Example(Base):
    ...    __tablename__ = "example_table"
    ...    a = Column(Integer, primary_key=True)
    ...    b = Column(Float)
    >>> row = Example(a=5, b=1.1)
    >>> expected = {"a": 5, "b": 1.1}
    >>> expected == dictify_row(row)
    True
    """
    return {
        col.name: getattr(row, col.name)
        for col in row.__table__.columns
        if hasattr(row, col.name)
    }


SCHEMA_TO_MODEL = {
    schemas.Element: models.Element,
    schemas.ResourceContainer: models.ResourceContainer,
    schemas.ElementCarrier: models.ElementCarrier,
    schemas.HumanAgent: models.HumanAgent,
    schemas.RoboticAgent: models.RoboticAgent,
    schemas.PropulsiveVehicle: models.PropulsiveVehicle,
    schemas.SurfaceVehicle: models.SurfaceVehicle,
    schemas.FlightEdge: models.FlightEdge,
    schemas.SpaceEdge: models.SpaceEdge,
    schemas.SurfaceEdge: models.SurfaceEdge,
    schemas.LagrangeNode: models.LagrangeNode,
    schemas.OrbitalNode: models.OrbitalNode,
    schemas.SurfaceNode: models.SurfaceNode,
    schemas.ContinuousResource: models.ContinuousResource,
    schemas.DiscreteResource: models.DiscreteResource,
}

__models = [
    models.Element,
    models.ElementCarrier,
    models.ResourceContainer,
    models.SurfaceVehicle,
    models.PropulsiveVehicle,
    models.HumanAgent,
    models.RoboticAgent,
    models.Resource,
    models.ContinuousResource,
    models.DiscreteResource,
    models.Edge,
    models.SpaceEdge,
    models.FlightEdge,
    models.SurfaceEdge,
    models.Node,
    models.LagrangeNode,
    models.OrbitalNode,
    models.SurfaceNode,
]

MODEL_TO_PARENT = {
    child: parent
    for child in __models
    for parent in (models.Element, models.Resource, models.Edge, models.Node)
    if issubclass(child, parent)
}


if __name__ == "__main__":
    doctest.testmod()
