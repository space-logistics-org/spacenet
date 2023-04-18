"""
A network composes nodes and edges.
"""

from typing import List

from fastapi_camelcase import CamelModel
from pydantic import Field

from .edges import AllEdges
from .nodes import AllNodes


class Network(CamelModel):
    """
    Composition of nodes and edges.
    """

    nodes: List[AllNodes] = Field([], title="Nodes", description="Constituent nodes")
    edges: List[AllEdges] = Field([], title="Edges", description="Constituent edges")
