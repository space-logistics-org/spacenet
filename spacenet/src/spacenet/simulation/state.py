"""
Simulation state.
"""

from typing import Union
from uuid import UUID

from ..schemas import Scenario, AllNodes, AllEdges, AllInstElements, AllElements

class State(object):
    def __init__(self, scenario: Scenario):
        self.time = sceneario.start_date
        self.network = scenario.network.copy(deep=True)
        self.elements = [
            element.copy(update=_get_element_template(element.template_id).dict(), deep=True)
            for element in scenario.instantiated_elements
        ]
        # TODO fix demand models

    def _get_element_template(id: UUID) -> AllElements:
        for template in scenario.element_templates:
            if template.id == id: return template
        return None

    def get_location(id: UUID) -> Union[AllNodes, AllEdges]:
        for node in self.network.nodes:
            if node.id == id: return node
        for edge in self.network.edges:
            if edge.id == id: return edge
        return None

    def get_element(id: UUID) -> Union[AllInstElements]:
        for element in self.elements:
            if element.id == id: return element
        return None
