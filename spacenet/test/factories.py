import random
from abc import ABC, abstractmethod
from typing import Any, Dict, Tuple

from spacenet.constants import Environment
from spacenet.schemas.element import ElementKind

STRINGS = ["foo", "bar", "baz"]
NON_NEG_INTS = list(range(10))
NEG_INTS = [-1 * (n + 1) for n in NON_NEG_INTS]
NON_NEG_FLOATS = [i / 2 for i in range(10)]
NEG_FLOATS = [float(-1 * i) for i in range(1, 10)]
FLOATS_IN_UNIT_INTERVAL = [i / 9 for i in range(10)]

__all__ = [
    "get_invalid_types",
    "ValidElementArgsFactory",
    "ValidElementCarrierArgsFactory",
    "ValidVehicleArgsFactory",
    "ValidSurfaceArgsFactory",
    "ValidPropulsiveArgsFactory",
    "ValidAgentArgsFactory",
    "ValidCargoCarrierArgsFactory",
    "InvalidVehicleArgsFactory",
    "InvalidPropulsiveArgsFactory",
    "InvalidSurfaceArgsFactory",
    "InvalidAgentArgsFactory",
    "InvalidCargoCarrierArgsFactory",
    "InvalidElementArgsFactory",
    "InvalidElementCarrierArgsFactory",
    "InvalidArgsFactory",
    "ValidArgsFactory",
]


def get_invalid_types(my_type: ElementKind) -> Tuple[ElementKind, ...]:
    """
    Get a list of all invalid type discriminants, given that the only valid type discriminant
    is the provided "myType".

    :param my_type: the valid type discriminant
    :return:  all invalid type discriminants
    """
    return tuple(kind for kind in ElementKind if kind != my_type)


def with_id(kw: Dict) -> Dict:
    """
    Construct a new dictionary which adds a field "id_" with a value of type uuid to the
    provided dictionary.

    :param kw: input dictionary
    :return: copy of input dictionary with new field "id_"
    """
    return {**kw, "id_": int(random.random() * 5000)}


class ValidArgsFactory(ABC):
    """
    Interface defining behavior of a keyword argument factory which provides valid keyword
    arguments.
    """

    @staticmethod
    @abstractmethod
    def make_keywords() -> Dict[str, Any]:
        """
        Make valid keyword arguments for constructing an element model.

        :return: the resulting keyword argument dictionary
        """
        pass


class InvalidArgsFactory(ABC):
    """
    Interface defining behavior of a keyword argument factory which provides invalid keyword
    arguments.
    """

    @staticmethod
    @abstractmethod
    def make_keywords() -> Dict[str, Any]:
        """
        Make invalid keyword arguments for constructing an element model.

        :return: the resulting keyword argument dictionary
        """
        pass


class ValidElementArgsFactory(ValidArgsFactory):
    """
    Factory class for constructing dictionaries consisting of valid arguments for constructing
    an element model, excepting the "type" field.
    """

    validNames = STRINGS
    validDescs = STRINGS
    validCoS = list(range(11))
    validEnvironments = [str(variant.value) for variant in Environment]
    validAccMasses = NON_NEG_INTS + NON_NEG_FLOATS
    validMasses = NON_NEG_INTS + NON_NEG_FLOATS
    validVolumes = validMasses

    @staticmethod
    def make_keywords() -> Dict[str, Any]:
        kw = {
            "name": random.choice(ValidElementArgsFactory.validNames),
            "description": random.choice(ValidElementArgsFactory.validDescs),
            "class_of_supply": random.choice(ValidElementArgsFactory.validCoS),
            "environment": random.choice(ValidElementArgsFactory.validEnvironments),
            "accommodation_mass": random.choice(ValidElementArgsFactory.validAccMasses),
            "mass": random.choice(ValidElementArgsFactory.validMasses),
            "volume": random.choice(ValidElementArgsFactory.validVolumes),
        }
        return kw


class InvalidElementArgsFactory(InvalidArgsFactory):
    """
    Factory class for constructing dictionaries consisting of invalid or badly-typed
    arguments for constructing an element model, excepting the "type" field.
    """

    invalidNames = []
    badlyTypedNames = []
    invalidDescs = []
    badlyTypedDescs = []
    invalidCoS = list(range(11, 99))
    badlyTypedCoS = STRINGS
    invalidEnvironments = STRINGS
    badlyTypedEnvironments = NON_NEG_INTS + NON_NEG_FLOATS
    invalidAccMasses = NEG_INTS + NEG_FLOATS
    badlyTypedAccMasses = STRINGS
    invalidMasses = NEG_INTS + NEG_FLOATS
    badlyTypedMasses = STRINGS
    invalidVolumes = invalidMasses
    badlyTypedVolumes = badlyTypedMasses

    @staticmethod
    def make_keywords() -> Dict[str, Any]:
        """
        Make invalid or badly-typed keyword arguments for constructing an element model.

        :return: the resulting keyword argument dictionary

        This implementation first randomly checks if an attribute should be given an invalid
        value, and if said process assigns no invalid values, selects exactly 1 attribute to
        have an invalid value.
        """
        invalid_selected = 0
        attrs = [
            "Names",
            "Descs",
            "CoS",
            "Environments",
            "AccMasses",
            "Masses",
            "Volumes",
        ]
        field_names = [
            "name",
            "description",
            "class_of_supply",
            "environment",
            "accommodation_mass",
            "mass",
            "volume",
        ]
        kw = {}
        for attr, field_name in zip(attrs, field_names):
            options = InvalidElementArgsFactory.get_options(attr)
            ix = random.randrange(len(options))
            if ix != 0:
                invalid_selected += 1
            option = options[ix]
            attr_value = random.choice(option)
            kw[field_name] = attr_value
        if invalid_selected == 0:
            bad_attr_ix = random.randrange(
                2, len(attrs)
            )  # exclude name and description
            attr, field_name = attrs[bad_attr_ix], field_names[bad_attr_ix]
            options = InvalidElementArgsFactory.get_options(attr)[
                1:
            ]  # exclude first valid
            option = random.choice(options)
            attr_value = random.choice(option)
            kw[field_name] = attr_value
        return kw

    @staticmethod
    def get_options(attr: str) -> list:
        options = [
            getattr(ValidElementArgsFactory, f"valid{attr}"),
            getattr(InvalidElementArgsFactory, f"badlyTyped{attr}"),
            getattr(InvalidElementArgsFactory, f"invalid{attr}"),
        ]
        return [opt for opt in options if len(opt) > 0]


class ValidCargoCarrierArgsFactory(ValidArgsFactory):
    """
    Factory class for constructing dictionaries consisting of valid arguments for
    constructing a resource container or element carrier model, excepting the "type" field.
    """

    validMaxCargoMass = NON_NEG_FLOATS + [None]
    validMaxCargoVolume = NON_NEG_FLOATS + [None]

    @staticmethod
    def make_keywords() -> Dict[str, Any]:
        kw = ValidElementArgsFactory.make_keywords()
        kw["max_cargo_mass"] = random.choice(
            ValidCargoCarrierArgsFactory.validMaxCargoMass
        )
        kw["max_cargo_volume"] = random.choice(
            ValidCargoCarrierArgsFactory.validMaxCargoVolume
        )
        return kw


class InvalidCargoCarrierArgsFactory(InvalidArgsFactory):
    """
    Factory class for constructing dictionaries consisting of invalid arguments for
    constructing a resource container or element carrier model, excepting the "type" field.
    """

    invalidMaxCargoMass = NEG_INTS + NEG_FLOATS
    badlyTypedMaxCargoMass = STRINGS
    invalidMaxCargoVolume = NEG_INTS + NEG_FLOATS
    badlyTypedMaxCargoVolume = STRINGS

    @staticmethod
    def make_keywords() -> Dict[str, Any]:
        kw = ValidCargoCarrierArgsFactory.make_keywords()
        rand = random.random()
        if rand < 0.25:
            kw["max_cargo_mass"] = random.choice(
                InvalidCargoCarrierArgsFactory.invalidMaxCargoMass
                + InvalidCargoCarrierArgsFactory.badlyTypedMaxCargoMass
            )
            kw["max_cargo_volume"] = random.choice(
                InvalidCargoCarrierArgsFactory.invalidMaxCargoVolume
                + InvalidCargoCarrierArgsFactory.badlyTypedMaxCargoVolume
            )
        elif rand < 0.5:
            kw["max_cargo_mass"] = random.choice(
                InvalidCargoCarrierArgsFactory.invalidMaxCargoMass
                + InvalidCargoCarrierArgsFactory.badlyTypedMaxCargoMass
            )
        else:
            kw["max_cargo_volume"] = random.choice(
                InvalidCargoCarrierArgsFactory.invalidMaxCargoVolume
                + InvalidCargoCarrierArgsFactory.badlyTypedMaxCargoVolume
            )
        return kw


class ValidElementCarrierArgsFactory(ValidArgsFactory):
    """
    Factory class for constructing dictionaries consisting of valid arguments for
    constructing a element carrier model, excepting the "type" field.
    """

    @staticmethod
    def make_keywords() -> Dict[str, Any]:
        kw = ValidCargoCarrierArgsFactory.make_keywords()
        kw["cargo_environment"] = random.choice(
            [variant.value for variant in Environment]
        )
        return kw


class InvalidElementCarrierArgsFactory(InvalidArgsFactory):
    """
    Factory class for constructing dictionaries consisting of invalid arguments for
    constructing an element carrier model, excepting the "type" field.
    """

    invalidCargoEnvironments = ["Foo", "Bar", "Baz"]
    badlyTypedCargoEnvironments = list(range(10))

    @staticmethod
    def make_keywords() -> Dict[str, Any]:
        kw = random.choice(
            (ValidCargoCarrierArgsFactory, InvalidCargoCarrierArgsFactory)
        ).make_keywords()
        kw["cargo_environment"] = random.choice(
            InvalidElementCarrierArgsFactory.invalidCargoEnvironments
            + InvalidElementCarrierArgsFactory.badlyTypedCargoEnvironments
        )
        return kw


class ValidAgentArgsFactory(ValidArgsFactory):
    """
    Factory class for constructing dictionaries consisting of valid arguments for
    constructing an agent model, excepting the "type" field.
    """

    validTImeFractions = FLOATS_IN_UNIT_INTERVAL

    @staticmethod
    def make_keywords() -> Dict[str, Any]:
        kw = ValidElementArgsFactory.make_keywords()
        kw["active_time_fraction"] = random.choice(
            ValidAgentArgsFactory.validTImeFractions
        )
        return kw


class InvalidAgentArgsFactory(InvalidArgsFactory):
    """
    Factory class for constructing dictionaries consisting of valid arguments for
    constructing an agent model, excepting the "type" field.
    """

    invalidTimeFractions = (
        NEG_INTS + NEG_FLOATS + [x for x in NON_NEG_FLOATS + NON_NEG_INTS if x > 1]
    )
    badlyTypedTimeFractions = STRINGS

    @staticmethod
    def make_keywords() -> Dict[str, Any]:
        kw = random.choice(
            (ValidElementArgsFactory, InvalidElementArgsFactory)
        ).make_keywords()
        kw["active_time_fraction"] = random.choice(
            InvalidAgentArgsFactory.invalidTimeFractions
            + InvalidAgentArgsFactory.badlyTypedTimeFractions
        )
        return kw


class ValidVehicleArgsFactory(ValidArgsFactory):
    """
    Factory class for constructing dictionaries consisting of valid arguments for
    constructing a vehicle model, excepting the "type" field.
    """

    validMaxFuels = NON_NEG_INTS + NON_NEG_FLOATS
    validMaxCrews = NON_NEG_INTS

    @staticmethod
    def make_keywords() -> Dict[str, Any]:
        kw = ValidCargoCarrierArgsFactory.make_keywords()
        kw["max_crew"] = random.choice(ValidVehicleArgsFactory.validMaxCrews)
        kw["max_fuel"] = random.choice(ValidVehicleArgsFactory.validMaxFuels)
        return kw


class InvalidVehicleArgsFactory(InvalidArgsFactory):
    """
    Factory class for constructing dictionaries consisting of invalid arguments for
    constructing a vehicle model, excepting the "type" field.
    """

    invalidMaxFuels = NEG_INTS + NEG_FLOATS
    badlyTypedMaxFuels = STRINGS
    invalidMaxCrews = NEG_INTS + NEG_FLOATS
    badlyTypedMaxCrews = STRINGS

    @staticmethod
    def make_keywords() -> Dict[str, Any]:
        kw = random.choice(
            (ValidCargoCarrierArgsFactory, InvalidCargoCarrierArgsFactory)
        ).make_keywords()
        rand = random.random()
        if rand < 0.25:
            max_fuel_options = (
                InvalidVehicleArgsFactory.invalidMaxFuels
                + InvalidVehicleArgsFactory.badlyTypedMaxFuels
            )
            max_crew_options = (
                InvalidVehicleArgsFactory.invalidMaxCrews
                + InvalidVehicleArgsFactory.badlyTypedMaxCrews
            )
        elif rand < 0.5:
            max_fuel_options = (
                InvalidVehicleArgsFactory.invalidMaxFuels
                + InvalidVehicleArgsFactory.badlyTypedMaxFuels
            )
            max_crew_options = ValidVehicleArgsFactory.validMaxCrews

        else:
            max_fuel_options = ValidVehicleArgsFactory.validMaxFuels
            max_crew_options = (
                InvalidVehicleArgsFactory.invalidMaxCrews
                + InvalidVehicleArgsFactory.badlyTypedMaxCrews
            )

        kw["max_crew"] = random.choice(max_crew_options)
        kw["max_fuel"] = random.choice(max_fuel_options)
        return kw


class ValidPropulsiveArgsFactory(ValidArgsFactory):
    """
    Factory class for constructing dictionaries consisting of valid arguments for
    constructing a propulsive vehicle model, excepting the "type" field.
    """

    validISPs = NON_NEG_INTS + NON_NEG_FLOATS
    validPropIDs = NON_NEG_INTS + NEG_INTS

    @staticmethod
    def make_keywords() -> Dict[str, Any]:
        kw = ValidVehicleArgsFactory.make_keywords()
        kw["isp"] = random.choice(ValidPropulsiveArgsFactory.validISPs)
        kw["propellant_id"] = random.choice(ValidPropulsiveArgsFactory.validPropIDs)
        return kw


class InvalidPropulsiveArgsFactory(InvalidArgsFactory):
    """
    Factory class for constructing dictionaries consisting of invalid arguments for
    constructing a propulsive vehicle model, excepting the "type" field.
    """

    invalidISPs = NEG_INTS + NEG_FLOATS
    badlyTypedISPs = STRINGS
    invalidPropIDs = NEG_FLOATS + NON_NEG_FLOATS
    badlyTypedPropIDs = STRINGS

    @staticmethod
    def make_keywords() -> Dict[str, Any]:
        kw = random.choice(
            (ValidVehicleArgsFactory, InvalidVehicleArgsFactory)
        ).make_keywords()
        rand = random.random()
        if rand < 0.25:
            isp_options = (
                InvalidPropulsiveArgsFactory.invalidISPs
                + InvalidPropulsiveArgsFactory.badlyTypedISPs
            )
            propellant_id_options = (
                InvalidPropulsiveArgsFactory.invalidPropIDs
                + InvalidPropulsiveArgsFactory.badlyTypedPropIDs
            )
        elif rand < 0.5:
            isp_options = (
                InvalidPropulsiveArgsFactory.invalidISPs
                + InvalidPropulsiveArgsFactory.badlyTypedISPs
            )
            propellant_id_options = ValidPropulsiveArgsFactory.validPropIDs
        else:
            isp_options = ValidPropulsiveArgsFactory.validISPs
            propellant_id_options = (
                InvalidPropulsiveArgsFactory.invalidPropIDs
                + InvalidPropulsiveArgsFactory.badlyTypedPropIDs
            )
        kw["isp"] = random.choice(isp_options)
        kw["propellant_id"] = random.choice(propellant_id_options)
        return kw


class ValidSurfaceArgsFactory(ValidArgsFactory):
    """
    Factory class for constructing dictionaries consisting of valid arguments for
    constructing a surface vehicle model, excepting the "type" field.
    """

    validMaxSpeeds = NON_NEG_INTS + NON_NEG_FLOATS
    validFuelIDs = NON_NEG_INTS + NEG_INTS

    @staticmethod
    def make_keywords() -> Dict[str, Any]:
        kw = ValidVehicleArgsFactory.make_keywords()
        kw["max_speed"] = random.choice(ValidSurfaceArgsFactory.validMaxSpeeds)
        kw["fuel_id"] = random.choice(ValidSurfaceArgsFactory.validFuelIDs)
        return kw


class InvalidSurfaceArgsFactory(InvalidArgsFactory):
    """
    Factory class for constructing dictionaries consisting of invalid arguments for
    constructing a surface vehicle model, excepting the "type" field.
    """

    invalidMaxSpeeds = NEG_INTS + NEG_FLOATS
    badlyTypedMaxSpeeds = STRINGS
    invalidFuelIDs = []
    badlyTypedFuelIDs = STRINGS

    @staticmethod
    def make_keywords() -> Dict[str, Any]:
        kw = random.choice(
            (ValidVehicleArgsFactory, InvalidVehicleArgsFactory)
        ).make_keywords()
        rand = random.random()
        if rand < 0.25:
            max_speed_options = (
                InvalidSurfaceArgsFactory.invalidMaxSpeeds
                + InvalidSurfaceArgsFactory.badlyTypedMaxSpeeds
            )
            fuel_id_options = (
                InvalidSurfaceArgsFactory.invalidFuelIDs
                + InvalidSurfaceArgsFactory.badlyTypedFuelIDs
            )
        elif rand < 0.5:
            max_speed_options = (
                InvalidSurfaceArgsFactory.invalidMaxSpeeds
                + InvalidSurfaceArgsFactory.badlyTypedMaxSpeeds
            )
            fuel_id_options = ValidSurfaceArgsFactory.validFuelIDs
        else:
            max_speed_options = ValidSurfaceArgsFactory.validMaxSpeeds
            fuel_id_options = (
                InvalidSurfaceArgsFactory.invalidFuelIDs
                + InvalidSurfaceArgsFactory.badlyTypedFuelIDs
            )
        kw["max_speed"] = random.choice(max_speed_options)
        kw["fuel_id"] = random.choice(fuel_id_options)
        return kw
