"""
Planetary bodies define the celestial objects as the basis
of orbits and surface exploration.
"""

from enum import Enum

import enum_tools.documentation

enum_tools.documentation.INTERACTIVE = True


@enum_tools.documentation.document_enum
class Body(str, Enum):
    """
    An enumeration of planetary bodies.
    """

    SUN = "Sun"  # doc: Sun
    EARTH = "Earth"  # doc: Earth
    MOON = "Moon"  # doc: Moon
    MARS = "Mars"  # doc: Mars
