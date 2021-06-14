"""
This module contains tests for the element model and schema. The tests are organized as
follows:

Each type of element, T, has its own tester class Test{T}.
These tester classes are what's actually run by the unittest framework, while
they're backed by supporting factory classes and non-instantiated tester superclasses which
handle configuration.

For each T, a factory class is used to generate valid and invalid keyword arguments to the
constructor of that type. Each tester class verifies that a) when all fields are valid,
no error results and all fields match as assigned, b) when a field is invalid, an error
is always raised, and c) if a vehicle's type discriminant disagrees with its Python type,
an error is always raised.

The factories generate their inputs to keyword arguments by pseudo-random selection from a
fairly small dataset: over the NUM_ATTEMPTS times a test occurs, the probability that a given
value for any one field is not exercised is quite small (and increasing NUM_ATTEMPTS
improves this).

An alternative approach would be a Cartesian product over all inputs, but
there are too many inputs for this to be feasible, This approach also likely provides
equivalent or better coverage than equivalence partitioning: it's very likely that no
combination of values is repeated across the many iterations of a test, and again, it's
unlikely that any one value is untested. This means that about 7 * NUM_SAMPLES combinations are
tested in the test_all_valid cases alone. Then, equivalence partitioning likely tests fewer
combinations of values. If some particular problematic combination of inputs causes issues,
adding a more manual test for that specific combination is still feasible.

Reproducing a failure is possible because the seed is deterministically generated: the tests
failing once should be repeatable each time, as the same sequence of values is always produced.

The BaseTester class handles most of the testing logic, while factories handle their respective
keyword argument generation logic. Changing schema attributes constitutes removing them from
a tester class (or its superclass)'s attributes, and making the factory no longer assign the
value in the dictionary.
"""
import random
import unittest
import uuid
from abc import ABC, abstractmethod
from typing import Any, Dict, Tuple, Type

from pydantic import ValidationError

from spacenet.schemas.element import *
from spacenet.schemas.element import (
    ElementKind,
    Environment,
)

NUM_ATTEMPTS = 500
SEED = "spacenet"
STRINGS = ["foo", "bar", "baz"]
NON_NEG_INTS = list(range(10))
NEG_INTS = [-1 * (n + 1) for n in NON_NEG_INTS]
NON_NEG_FLOATS = [i / 2 for i in range(10)]
NEG_FLOATS = [float(-1 * i) for i in range(1, 10)]
FLOATS_IN_UNIT_INTERVAL = [i / 9 for i in range(10)]


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
    return {**kw, "id_": uuid.uuid4()}


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


class BaseTester:
    """
    The base testing class. This class handles verifying that a model has values matching
    the keyword arguments which instantiated it, as well as that the model fails to validate
    when invalid values or an invalid type discriminant is provided. This is a mixin, so any
    uses will also have to inherit from unittest.TestCase at some point.
    """

    # Should be set by subclasses
    validType: ElementKind
    invalidTypes: Tuple[ElementKind, ...]
    validFactory = None  # factory to use for successfully constructing models
    invalidFactory = None  # factory to use for unsuccessfully constructing models
    nonEnumAttrs = ["name", "description", "accommodation_mass", "mass", "volume"]
    # the attribute names which are not enumerations
    enumAttrs = ["class_of_supply", "environment"]
    elementType: Type[Element]

    # the attribute names which are enumerations

    def assert_matches(self, kw: dict, element: Element) -> None:
        """
        Verify that the fields of the provided Element match the corresponding values in the
        provided keyword argument dictionary which created it.

        :param kw: keyword argument dictionary which created element
        :param element: the element to check the fields of

        This implementation uses getattr for using non-literal values when accessing attributes
        to avoid code duplication.
        """
        for nonEnumAttr in self.nonEnumAttrs:
            if nonEnumAttr in kw:
                self.assertEqual(
                    kw[nonEnumAttr],
                    getattr(element, nonEnumAttr),
                    msg=f"Expected element.{nonEnumAttr} = {kw[nonEnumAttr]},"
                    f"but was {getattr(element, nonEnumAttr)}",
                )
        for enumAttr in self.enumAttrs:
            if str(enumAttr) in kw:
                self.assertEqual(
                    kw[enumAttr],
                    getattr(element, enumAttr).value,
                    msg=f"Expected element.{enumAttr}.value = {kw[enumAttr]},"
                    f"but was {getattr(element, enumAttr).value}",
                )
        self.assertEqual(
            self.validType,
            element.type,
            msg=f"Expected element.type to be {self.validType}",
        )

    def test_all_valid(self) -> None:
        """
        Verify that, when all fields are valid, no error is raised when constructing a model
        from keyword arguments, and that all fields match what is expected.
        """
        factory = self.validFactory()
        for _ in range(NUM_ATTEMPTS):
            kw = factory.make_keywords()
            kw["type"] = self.validType
            element = self.elementType(**kw)
            self.assert_matches(kw, element)

    def test_missing_fields(self):
        factory = self.validFactory()
        for _ in range(NUM_ATTEMPTS):
            kw = factory.make_keywords()
            kw["type"] = self.validType
            missing_field, _ = kw.popitem()
            with self.assertRaises(
                ValidationError, msg=f"provided keywords are missing {missing_field}"
            ):
                self.elementType(**kw)

    def test_invalid_values(self) -> None:
        """
        Verify that, when at least one field takes on an invalid value, an error is raised when
        constructing a model from keyword arguments.
        """
        factory = self.invalidFactory()
        for _ in range(NUM_ATTEMPTS):
            kw = factory.make_keywords()
            kw["type"] = self.validType
            with self.assertRaises(
                ValidationError, msg=f"{kw} should have raised an error"
            ):
                self.elementType(**kw)

    def test_invalid_type(self) -> None:
        """
        Verify that, when the type discriminant of an element does not match what it's expected
        to, validation fails.
        """
        factory = self.validFactory()
        kw = factory.make_keywords()
        for type_ in self.invalidTypes:
            kw["type"] = type_
            with self.assertRaises(
                ValidationError,
                msg=f"{kw} should have raised an error for wrong discriminant",
            ):
                self.elementType(**kw)


class SeededTester(unittest.TestCase):
    """
    Base testing class which, on setup, resets its random seed to a constant.
    """

    def setUp(self) -> None:
        random.seed(SEED)


class TestElement(SeededTester, BaseTester):
    validType = ElementKind.Element
    invalidTypes = get_invalid_types(my_type=validType)
    validFactory = ValidElementArgsFactory
    invalidFactory = InvalidElementArgsFactory
    elementType = Element


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


class TestResourceContainer(SeededTester, BaseTester):
    validType = ElementKind.ResourceContainer
    invalidTypes = get_invalid_types(my_type=validType)
    validFactory = ValidCargoCarrierArgsFactory
    invalidFactory = InvalidCargoCarrierArgsFactory
    nonEnumAttrs = BaseTester.nonEnumAttrs + ["max_cargo_mass", "max_cargo_volume"]
    elementType = ResourceContainer


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


class TestElementCarrier(SeededTester, BaseTester):
    validType = ElementKind.ElementCarrier
    invalidTypes = get_invalid_types(my_type=validType)
    validFactory = ValidElementCarrierArgsFactory
    invalidFactory = InvalidCargoCarrierArgsFactory
    nonEnumAttrs = TestResourceContainer.nonEnumAttrs
    enumAttrs = BaseTester.enumAttrs + ["cargo_environment"]
    elementType = ElementCarrier


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


class AgentTester(BaseTester):
    validFactory = ValidAgentArgsFactory
    invalidFactory = InvalidAgentArgsFactory
    nonEnumAttrs = BaseTester.nonEnumAttrs + ["active_time_fraction"]


class TestHumanAgent(SeededTester, AgentTester):
    validType = ElementKind.HumanAgent
    invalidTypes = get_invalid_types(my_type=validType)
    elementType = HumanAgent


class TestRoboticAgent(SeededTester, AgentTester):
    validType = ElementKind.RoboticAgent
    invalidTypes = get_invalid_types(my_type=validType)
    elementType = RoboticAgent


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


class VehicleTester(BaseTester):
    nonEnumAttrs = BaseTester.nonEnumAttrs + ["max_crew"]


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


class TestPropulsiveVehicle(SeededTester, VehicleTester):
    validType = ElementKind.Propulsive
    invalidTypes = get_invalid_types(my_type=validType)
    validFactory = ValidPropulsiveArgsFactory
    invalidFactory = InvalidPropulsiveArgsFactory
    nonEnumAttrs = VehicleTester.nonEnumAttrs + ["max_fuel", "isp"]
    elementType = PropulsiveVehicle


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


class TestSurfaceVehicle(SeededTester, VehicleTester):
    validType = ElementKind.Surface
    invalidTypes = get_invalid_types(my_type=validType)
    validFactory = ValidSurfaceArgsFactory
    invalidFactory = InvalidSurfaceArgsFactory
    nonEnumAttrs = VehicleTester.nonEnumAttrs + ["max_fuel", "max_speed"]
    elementType = SurfaceVehicle
