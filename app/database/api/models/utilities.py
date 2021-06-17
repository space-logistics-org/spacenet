from typing import Any, Dict

from app.database.api.database import Base


def dictify_row(row: Base) -> Dict[str, Any]:
    """
    Convert a database row to a dictionary.

    :param row: row to copy data into dictionary from
    :return: dictionary mapping column names to values
    """
    return {col.name: getattr(row, col.name) for col in row.__table__.columns if hasattr(row, col.name)}
