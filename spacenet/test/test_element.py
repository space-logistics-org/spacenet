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
from typing import Tuple, Type

import pytest
from pydantic import ValidationError

from spacenet.schemas.element import *
from spacenet.schemas.element import ElementKind
from .element_factories import *

pytestmark = [pytest.mark.unit, pytest.mark.element, pytest.mark.schema]
NUM_ATTEMPTS = 500
SEED = "spacenet"


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
                self.elementType.parse_obj(kw)

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
                self.elementType.parse_obj(kw)

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
                self.elementType.parse_obj(kw)


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


class TestResourceContainer(SeededTester, BaseTester):
    validType = ElementKind.ResourceContainer
    invalidTypes = get_invalid_types(my_type=validType)
    validFactory = ValidCargoCarrierArgsFactory
    invalidFactory = InvalidCargoCarrierArgsFactory
    nonEnumAttrs = BaseTester.nonEnumAttrs + ["max_cargo_mass", "max_cargo_volume"]
    elementType = ResourceContainer


class TestElementCarrier(SeededTester, BaseTester):
    validType = ElementKind.ElementCarrier
    invalidTypes = get_invalid_types(my_type=validType)
    validFactory = ValidElementCarrierArgsFactory
    invalidFactory = InvalidCargoCarrierArgsFactory
    nonEnumAttrs = TestResourceContainer.nonEnumAttrs
    enumAttrs = BaseTester.enumAttrs + ["cargo_environment"]
    elementType = ElementCarrier


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


class VehicleTester(BaseTester):
    nonEnumAttrs = BaseTester.nonEnumAttrs + ["max_crew"]


class TestPropulsiveVehicle(SeededTester, VehicleTester):
    validType = ElementKind.Propulsive
    invalidTypes = get_invalid_types(my_type=validType)
    validFactory = ValidPropulsiveArgsFactory
    invalidFactory = InvalidPropulsiveArgsFactory
    nonEnumAttrs = VehicleTester.nonEnumAttrs + ["max_fuel", "isp"]
    elementType = PropulsiveVehicle


class TestSurfaceVehicle(SeededTester, VehicleTester):
    validType = ElementKind.Surface
    invalidTypes = get_invalid_types(my_type=validType)
    validFactory = ValidSurfaceArgsFactory
    invalidFactory = InvalidSurfaceArgsFactory
    nonEnumAttrs = VehicleTester.nonEnumAttrs + ["max_fuel", "max_speed"]
    elementType = SurfaceVehicle
