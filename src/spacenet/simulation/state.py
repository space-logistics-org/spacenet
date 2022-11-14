"""
Simulation state.
"""

from typing import List
from uuid import UUID

from ..schemas import Scenario, AllLocations, AllInstElements, AllElements


class State:
    """
    Simulation state.
    """

    def __init__(self, scenario: Scenario):
        self.time = scenario.start_date
        self.network = scenario.network.copy(deep=True)
        self.elements = [
            element.copy(
                update=self._get_element_template(
                    element, scenario.element_templates
                ).dict(),
                deep=True,
            )
            for element in scenario.instantiated_elements
        ]
        # TODO fix demand models

    def _get_element_template(
        self, element: AllInstElements, templates: List[AllElements]
    ) -> AllElements:
        """
        Get the element template matching an element instance.

        Args:
            element (:obj:`AllInstElements`): the element instance
            templates (:obj:`List[AllElements]`): the list of element templates

        Returns:
            AllElements: The matching element template if it exists, otherewise `None`.
        """
        for template in templates:
            if template.id == element.template_id:
                return template
        return None

    def get_location(self, location_id: UUID) -> AllLocations:
        """
        Get the network location matching a unique identifier.

        Args:
            location_id (:obj:`uuid.UUID`): the unique identifier

        Returns:
            AllLocations: The matching location if it exists, otherewise `None`.
        """
        for node in self.network.nodes:
            if node.id == location_id:
                return node
        for edge in self.network.edges:
            if edge.id == location_id:
                return edge
        return None

    def get_element(self, element_id: UUID) -> AllInstElements:
        """
        Get the element matching a unique identifier.

        Args:
            element_id (:obj:`uuid.UUID`): the unique identifier

        Returns:
            AllInstElements: The matching element if it exists, otherewise `None`.
        """
        for element in self.elements:
            if element.id == element_id:
                return element
        return None
