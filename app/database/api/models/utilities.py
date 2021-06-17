from typing import Any, Dict

from app.database.api.database import Base


def dictify_model(model: Base) -> Dict[str, Any]:
    return {col.name: getattr(model, col.name) for col in model.__table__.columns}
