"""
Numerical precision and analysis options shared by all simulation objects.
"""

import math

from ..schemas import Configuration


def java_round(value: float) -> float:
    """
    Rounds a value to the nearest integer with ties rounded towards positive
    infinity. Python's built-in `round` uses banker's rounding which would
    produce different results from the reference (Java) implementation.

    Args:
        value (float): The value to round.

    Returns:
        float: The rounded value.
    """
    if not math.isfinite(value):
        return value
    return float(math.floor(value + 0.5))


class Settings:
    """
    Wraps a scenario configuration to provide the rounding functions used by
    simulation objects. Undefined attributes are delegated to the underlying
    configuration (e.g., `settings.volume_constrained`).
    """

    #: Number of decimal places (as a power of ten) retained for time values.
    DECIMAL_PRECISION = 1000

    def __init__(self, configuration: Configuration = None):
        self.configuration = (
            configuration if configuration is not None else Configuration()
        )

    def __getattr__(self, name):
        # only called for attributes not found through normal lookup
        if name == "configuration":
            raise AttributeError(name)
        return getattr(self.configuration, name)

    @staticmethod
    def _round(value: float, precision: float) -> float:
        if precision is None or precision <= 0:
            return value
        return java_round(value / precision) * precision

    def round_time(self, time: float) -> float:
        """
        Rounds a time or duration to the scenario time precision.

        Args:
            time (float): The time (days).

        Returns:
            float: The rounded time (days).
        """
        precision = self.configuration.time_precision
        if precision is None or precision <= 0 or not math.isfinite(time):
            return time
        return (
            java_round(
                java_round(time / precision) * precision * self.DECIMAL_PRECISION
            )
            / self.DECIMAL_PRECISION
        )

    def round_demand(self, amount: float) -> float:
        """
        Rounds a resource amount to the scenario demand precision.

        Args:
            amount (float): The resource amount (units).

        Returns:
            float: The rounded resource amount (units).
        """
        return self._round(amount, self.configuration.demand_precision)

    def round_mass(self, mass: float) -> float:
        """
        Rounds a mass to the scenario mass precision.

        Args:
            mass (float): The mass (kg).

        Returns:
            float: The rounded mass (kg).
        """
        return self._round(mass, self.configuration.mass_precision)

    def round_volume(self, volume: float) -> float:
        """
        Rounds a volume to the scenario volume precision.

        Args:
            volume (float): The volume (m^3).

        Returns:
            float: The rounded volume (m^3).
        """
        return self._round(volume, self.configuration.volume_precision)
