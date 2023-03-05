"""Defines object schemas for generic element templates."""


from enum import Enum


class ElementType(str, Enum):
    """
    Enumeration of element types.
    """

    ELEMENT = "Element"
    RESOURCE_CONTAINER = "Resource Container"
    ELEMENT_CARRIER = "Element Carrier"
    HUMAN_AGENT = "Human Agent"
    ROBOTIC_AGENT = "Robotic Agent"
    PROPULSIVE_VEHICLE = "Propulsive Vehicle"
    SURFACE_VEHICLE = "Surface Vehicle"
