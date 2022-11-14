"""
Planetary bodies define the celestial objects as the basis
of orbits and surface exploration.
"""

from enum import Enum


class Body(str, Enum):
    """
    An enumeration of planetary bodies.
    """

    SUN = "Sun"
    EARTH = "Earth"
    MOON = "Moon"
    MARS = "Mars"
