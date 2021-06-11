"""
This module contains tests for the element model and schema. The tests are organized as
follows:

<<<<<<< HEAD
Each type of element, T, has its own tester class Test{T}. These tester classes are what's
actually run by the unittest framework, while they're backed by supporting factory classes
and non-instantiated tester superclasses which handle configuration.
=======
Each type of element, T, has its own tester class Test{T}.
These tester classes are what's actually run by the unittest framework, while
they're backed by supporting factory classes and non-instantiated tester superclasses which
handle configuration.
>>>>>>> a14263327e51c6b639d2ebd658e5b12615f88296

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
tested in the testAllValid cases alone. Then, equivalence partitioning likely tests fewer
combinations of values. If some particular problematic combination of inputs causes issues,
adding a more manual test for that specific combination is still feasible.

Reproducing a failure is possible because the seed is deterministically generated: the tests
failing once should be repeatable each time, as the same sequence of values is always produced.

The BaseTester class handles most of the testing logic, while factories handle their respective
keyword argument generation logic. Changing schema attributes constitutes removing them from
a tester class (or its superclass)'s attributes, and making the factory no longer assign the
value in the dictionary.
"""
<<<<<<< HEAD
import copy
import random
import unittest
from abc import ABC, abstractmethod
from typing import Any, Dict, List

from pydantic import BaseModel, Field, ValidationError, conint

from spacenet.schemas.element import (
    Element,
    ElementCarrier,
    ElementKind,
    Environment,
    HumanAgent,
    PropulsiveVehicle,
    ResourceContainer,
    RoboticAgent,
    SurfaceVehicle,
    patchModel,
=======
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
>>>>>>> a14263327e51c6b639d2ebd658e5b12615f88296
)

NUM_ATTEMPTS = 500
SEED = "spacenet"
STRINGS = ["foo", "bar", "baz"]
NON_NEG_INTS = list(range(10))
NEG_INTS = [-1 * (n + 1) for n in NON_NEG_INTS]
NON_NEG_FLOATS = [i / 2 for i in range(10)]
NEG_FLOATS = [float(-1 * i) for i in range(1, 10)]
FLOATS_IN_UNIT_INTERVAL = [i / 9 for i in range(10)]


<<<<<<< HEAD
def getInvalidTypes(myType: ElementKind) -> List[ElementKind]:
=======
def getInvalidTypes(myType: ElementKind) -> Tuple[ElementKind, ...]:
>>>>>>> a14263327e51c6b639d2ebd658e5b12615f88296
    """
    Get a list of all invalid type discriminants, given that the only valid type discriminant
    is the provided "myType".

    :param myType: the valid type discriminant
    :return:  all invalid type discriminants
    """
<<<<<<< HEAD
    return [kind for kind in ElementKind if kind != myType]
=======
    return tuple(kind for kind in ElementKind if kind != myType)


def withID(kw: Dict) -> Dict:
    return {**kw, "id_": uuid.uuid4()}
>>>>>>> a14263327e51c6b639d2ebd658e5b12615f88296


class I_ValidArgsFactory(ABC):
    """
    Interface defining behavior of a keyword argument factory which provides valid keyword
    arguments.
    """

    @staticmethod
    @abstractmethod
    def makeKeywords() -> Dict[str, Any]:
        """
        Make valid keyword arguments for constructing an element model.

        :return: the resulting keyword argument dictionary
        """
        pass


class I_InvalidArgsFactory(ABC):
    """
    Interface defining behavior of a keyword argument factory which provides invalid keyword
    arguments.
    """

    @staticmethod
    @abstractmethod
    def makeKeywords() -> Dict[str, Any]:
        """
        Make invalid keyword arguments for constructing an element model.

        :return: the resulting keyword argument dictionary
        """
        pass


class ValidElementArgsFactory(I_ValidArgsFactory):
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
    def makeKeywords() -> Dict[str, Any]:
        kw = {
            "name": random.choice(ValidElementArgsFactory.validNames),
            "description": random.choice(ValidElementArgsFactory.validDescs),
<<<<<<< HEAD
            "classOfSupply": random.choice(ValidElementArgsFactory.validCoS),
            "environment": random.choice(ValidElementArgsFactory.validEnvironments),
            "accommodationMass": random.choice(ValidElementArgsFactory.validAccMasses),
=======
            "class_of_supply": random.choice(ValidElementArgsFactory.validCoS),
            "environment": random.choice(ValidElementArgsFactory.validEnvironments),
            "accommodation_mass": random.choice(ValidElementArgsFactory.validAccMasses),
>>>>>>> a14263327e51c6b639d2ebd658e5b12615f88296
            "mass": random.choice(ValidElementArgsFactory.validMasses),
            "volume": random.choice(ValidElementArgsFactory.validVolumes),
        }
        return kw


class InvalidElementArgsFactory(I_InvalidArgsFactory):
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
    def makeKeywords() -> Dict[str, Any]:
        """
        Make invalid or badly-typed keyword arguments for constructing an element model.

        :return: the resulting keyword argument dictionary

        This implementation first randomly checks if an attribute should be given an invalid
        value, and if said process assigns no invalid values, selects exactly 1 attribute to
        have an invalid value.
        """
        invalidSelected = 0
        attrs = [
            "Names",
            "Descs",
            "CoS",
            "Environments",
            "AccMasses",
            "Masses",
            "Volumes",
        ]
        fieldNames = [
            "name",
            "description",
<<<<<<< HEAD
            "classOfSupply",
            "environment",
            "accommodationMass",
=======
            "class_of_supply",
            "environment",
            "accommodation_mass",
>>>>>>> a14263327e51c6b639d2ebd658e5b12615f88296
            "mass",
            "volume",
        ]
        kw = {}
        for attr, fieldName in zip(attrs, fieldNames):
            options = InvalidElementArgsFactory.getOptions(attr)
            ix = random.randrange(len(options))
            if ix != 0:
                invalidSelected += 1
            option = options[ix]
            attrValue = random.choice(option)
            kw[fieldName] = attrValue
        if invalidSelected == 0:
            badAttrIx = random.randrange(2, len(attrs))  # exclude name and description
            attr, fieldName = attrs[badAttrIx], fieldNames[badAttrIx]
            options = InvalidElementArgsFactory.getOptions(attr)[
                1:
            ]  # exclude first valid
            option = random.choice(options)
            attrValue = random.choice(option)
            kw[fieldName] = attrValue
        return kw

    @staticmethod
    def getOptions(attr: str) -> list:
        options = [
            getattr(ValidElementArgsFactory, f"valid{attr}"),
            getattr(InvalidElementArgsFactory, f"badlyTyped{attr}"),
            getattr(InvalidElementArgsFactory, f"invalid{attr}"),
        ]
        return [opt for opt in options if len(opt) > 0]


<<<<<<< HEAD
class BaseTester(unittest.TestCase):
    """
    The base testing class. This class handles verifying that a model has values matching
    the keyword arguments which instantiated it, as well as that the model fails to validate
    when invalid values or an invalid type discriminant is provided.
    """

    # Should be set by subclasses
    validTypes = None  # a list of one ElementKind and None
    invalidTypes = (
        None  # a list of ElementKinds which don't match the expected discriminant
    )
    validFactory = None  # factory to use for successfully constructing models
    invalidFactory = None  # factory to use for unsuccessfully constructing models
    nonEnumAttrs = ["name", "description", "accommodationMass", "mass", "volume"]
    # the attribute names which are not enumerations
    enumAttrs = ["classOfSupply", "environment"]

    # the attribute names which are enumerations

    def setUp(self) -> None:
        random.seed(SEED)

=======
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

>>>>>>> a14263327e51c6b639d2ebd658e5b12615f88296
    def assertMatches(self, kw: dict, element: Element) -> None:
        """
        Verify that the fields of the provided Element match the corresponding values in the
        provided keyword argument dictionary which created it.

        :param kw: keyword argument dictionary which created element
        :param element: the element to check the fields of

        This implementation uses getattr for using non-literal values when accessing attributes
        to avoid code duplication.
        """
        for nonEnumAttr in self.nonEnumAttrs:
<<<<<<< HEAD
            self.assertEqual(
                kw[nonEnumAttr],
                getattr(element, nonEnumAttr),
                msg=f"Expected element.{nonEnumAttr} = {kw[nonEnumAttr]},"
                f"but was {getattr(element, nonEnumAttr)}",
            )
        for enumAttr in self.enumAttrs:
            self.assertEqual(
                kw[enumAttr],
                getattr(element, enumAttr).value,
                msg=f"Expected element.{enumAttr}.value = {kw[enumAttr]},"
                f"but was {getattr(element, enumAttr).value}",
            )
        self.assertEqual(
            self.validTypes[0],
            element.type,
            msg=f"Expected element.type to be {self.validTypes[0]}",
        )

    def _testAllValid(self, elementType) -> None:
        """
        Verify that, when all fields are valid, no error is raised when constructing a model
        from keyword arguments, and that all fields match what is expected.

        :param elementType: the type of the model to construct
        """
        factory = self.validFactory()
        for _ in range(NUM_ATTEMPTS):
            for type_ in self.validTypes:
                kw = factory.makeKeywords()
                if type_:
                    kw["type"] = type_
                element = elementType(**kw)
                self.assertMatches(kw, element)

    def _testInvalidValues(self, elementType) -> None:
        """
        Verify that, when at least one field takes on an invalid value, an error is raised when
        constructing a model from keyword arguments.

        :param elementType: the type of the model to attempt to construct
=======
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

    def testAllValid(self) -> None:
        """
        Verify that, when all fields are valid, no error is raised when constructing a model
        from keyword arguments, and that all fields match what is expected.
        """
        factory = self.validFactory()
        for _ in range(NUM_ATTEMPTS):
            kw = factory.makeKeywords()
            kw["type"] = self.validType
            element = self.elementType(**kw)
            self.assertMatches(kw, element)

    def testMissingFields(self):
        factory = self.validFactory()
        for _ in range(NUM_ATTEMPTS):
            kw = factory.makeKeywords()
            kw["type"] = self.validType
            missingField, _ = kw.popitem()
            with self.assertRaises(
                ValidationError, msg=f"provided keywords are missing {missingField}"
            ):
                self.elementType(**kw)

    def testInvalidValues(self) -> None:
        """
        Verify that, when at least one field takes on an invalid value, an error is raised when
        constructing a model from keyword arguments.
>>>>>>> a14263327e51c6b639d2ebd658e5b12615f88296
        """
        factory = self.invalidFactory()
        for _ in range(NUM_ATTEMPTS):
            kw = factory.makeKeywords()
<<<<<<< HEAD
            with self.assertRaises(
                ValidationError, msg=f"{kw} should have raised an error"
            ):
                elementType(**kw)

    def _testInvalidType(self, elementType) -> None:
        """
        Verify that, when the type discriminant of an element does not match what it's expected
        to, validation fails.

        :param elementType: the type of the model to attempt to construct
=======
            kw["type"] = self.validType
            with self.assertRaises(
                ValidationError, msg=f"{kw} should have raised an error"
            ):
                self.elementType(**kw)

    def testInvalidType(self) -> None:
        """
        Verify that, when the type discriminant of an element does not match what it's expected
        to, validation fails.
>>>>>>> a14263327e51c6b639d2ebd658e5b12615f88296
        """
        factory = self.validFactory()
        kw = factory.makeKeywords()
        for type_ in self.invalidTypes:
            kw["type"] = type_
            with self.assertRaises(
<<<<<<< HEAD
                ValidationError, msg=f"{kw} should have raised an error"
            ):
                elementType(**kw)


class TestElement(BaseTester):
    validTypes = [ElementKind.Element, None]
    invalidTypes = getInvalidTypes(myType=ElementKind.Element)
    validFactory = ValidElementArgsFactory
    invalidFactory = InvalidElementArgsFactory

    def testAllValid(self):
        self._testAllValid(Element)

    def testInvalidValues(self):
        self._testInvalidValues(Element)

    def testInvalidType(self):
        self._testInvalidType(Element)
=======
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
    invalidTypes = getInvalidTypes(myType=validType)
    validFactory = ValidElementArgsFactory
    invalidFactory = InvalidElementArgsFactory
    elementType = Element
>>>>>>> a14263327e51c6b639d2ebd658e5b12615f88296


class ValidCargoCarrierArgsFactory(I_ValidArgsFactory):
    """
    Factory class for constructing dictionaries consisting of valid arguments for
    constructing a resource container or element carrier model, excepting the "type" field.
    """

<<<<<<< HEAD
    validMaxCargoMass = NON_NEG_FLOATS
    validMaxCargoVolume = NON_NEG_FLOATS
=======
    validMaxCargoMass = NON_NEG_FLOATS + [None]
    validMaxCargoVolume = NON_NEG_FLOATS + [None]
>>>>>>> a14263327e51c6b639d2ebd658e5b12615f88296

    @staticmethod
    def makeKeywords() -> Dict[str, Any]:
        kw = ValidElementArgsFactory.makeKeywords()
<<<<<<< HEAD
        kw["maxCargoMass"] = random.choice(
            ValidCargoCarrierArgsFactory.validMaxCargoMass
        )
        kw["maxCargoVolume"] = random.choice(
=======
        kw["max_cargo_mass"] = random.choice(
            ValidCargoCarrierArgsFactory.validMaxCargoMass
        )
        kw["max_cargo_volume"] = random.choice(
>>>>>>> a14263327e51c6b639d2ebd658e5b12615f88296
            ValidCargoCarrierArgsFactory.validMaxCargoVolume
        )
        return kw


class InvalidCargoCarrierArgsFactory(I_InvalidArgsFactory):
    """
    Factory class for constructing dictionaries consisting of invalid arguments for
    constructing a resource container or element carrier model, excepting the "type" field.
    """

    invalidMaxCargoMass = NEG_INTS + NEG_FLOATS
    badlyTypedMaxCargoMass = STRINGS
    invalidMaxCargoVolume = NEG_INTS + NEG_FLOATS
    badlyTypedMaxCargoVolume = STRINGS

    @staticmethod
    def makeKeywords() -> Dict[str, Any]:
        kw = ValidCargoCarrierArgsFactory.makeKeywords()
        rand = random.random()
        if rand < 0.25:
<<<<<<< HEAD
            kw["maxCargoMass"] = random.choice(
                InvalidCargoCarrierArgsFactory.invalidMaxCargoMass
                + InvalidCargoCarrierArgsFactory.badlyTypedMaxCargoMass
            )
            kw["maxCargoVolume"] = random.choice(
=======
            kw["max_cargo_mass"] = random.choice(
                InvalidCargoCarrierArgsFactory.invalidMaxCargoMass
                + InvalidCargoCarrierArgsFactory.badlyTypedMaxCargoMass
            )
            kw["max_cargo_volume"] = random.choice(
>>>>>>> a14263327e51c6b639d2ebd658e5b12615f88296
                InvalidCargoCarrierArgsFactory.invalidMaxCargoVolume
                + InvalidCargoCarrierArgsFactory.badlyTypedMaxCargoVolume
            )
        elif rand < 0.5:
<<<<<<< HEAD
            kw["maxCargoMass"] = random.choice(
=======
            kw["max_cargo_mass"] = random.choice(
>>>>>>> a14263327e51c6b639d2ebd658e5b12615f88296
                InvalidCargoCarrierArgsFactory.invalidMaxCargoMass
                + InvalidCargoCarrierArgsFactory.badlyTypedMaxCargoMass
            )
        else:
<<<<<<< HEAD
            kw["maxCargoVolume"] = random.choice(
=======
            kw["max_cargo_volume"] = random.choice(
>>>>>>> a14263327e51c6b639d2ebd658e5b12615f88296
                InvalidCargoCarrierArgsFactory.invalidMaxCargoVolume
                + InvalidCargoCarrierArgsFactory.badlyTypedMaxCargoVolume
            )
        return kw


<<<<<<< HEAD
class TestResourceContainer(BaseTester):
    validTypes = [ElementKind.ResourceContainer, None]
    invalidTypes = getInvalidTypes(myType=ElementKind.ResourceContainer)
    validFactory = ValidCargoCarrierArgsFactory
    invalidFactory = InvalidCargoCarrierArgsFactory
    nonEnumAttrs = BaseTester.nonEnumAttrs + ["maxCargoMass", "maxCargoVolume"]

    def testAllValid(self):
        self._testAllValid(ResourceContainer)

    def testInvalidValues(self):
        self._testInvalidValues(ResourceContainer)

    def testInvalidType(self):
        self._testInvalidType(ResourceContainer)
=======
class TestResourceContainer(SeededTester, BaseTester):
    validType = ElementKind.ResourceContainer
    invalidTypes = getInvalidTypes(myType=validType)
    validFactory = ValidCargoCarrierArgsFactory
    invalidFactory = InvalidCargoCarrierArgsFactory
    nonEnumAttrs = BaseTester.nonEnumAttrs + ["max_cargo_mass", "max_cargo_volume"]
    elementType = ResourceContainer
>>>>>>> a14263327e51c6b639d2ebd658e5b12615f88296


class ValidElementCarrierArgsFactory(I_ValidArgsFactory):
    """
    Factory class for constructing dictionaries consisting of valid arguments for
    constructing a element carrier model, excepting the "type" field.
    """

    @staticmethod
    def makeKeywords() -> Dict[str, Any]:
        kw = ValidCargoCarrierArgsFactory.makeKeywords()
<<<<<<< HEAD
        kw["cargoEnvironment"] = random.choice(
=======
        kw["cargo_environment"] = random.choice(
>>>>>>> a14263327e51c6b639d2ebd658e5b12615f88296
            [variant.value for variant in Environment]
        )
        return kw


class InvalidElementCarrierArgsFactory(I_InvalidArgsFactory):
    """
    Factory class for constructing dictionaries consisting of invalid arguments for
    constructing an element carrier model, excepting the "type" field.
    """

    invalidCargoEnvironments = ["Foo", "Bar", "Baz"]
    badlyTypedCargoEnvironments = list(range(10))

    @staticmethod
    def makeKeywords() -> Dict[str, Any]:
        kw = random.choice(
            (ValidCargoCarrierArgsFactory, InvalidCargoCarrierArgsFactory)
        ).makeKeywords()
<<<<<<< HEAD
        kw["cargoEnvironment"] = random.choice(
=======
        kw["cargo_environment"] = random.choice(
>>>>>>> a14263327e51c6b639d2ebd658e5b12615f88296
            InvalidElementCarrierArgsFactory.invalidCargoEnvironments
            + InvalidElementCarrierArgsFactory.badlyTypedCargoEnvironments
        )
        return kw


<<<<<<< HEAD
class TestElementCarrier(BaseTester):
    validTypes = [ElementKind.ElementCarrier, None]
    invalidTypes = getInvalidTypes(myType=ElementKind.ElementCarrier)
    validFactory = ValidElementCarrierArgsFactory
    invalidFactory = InvalidCargoCarrierArgsFactory
    nonEnumAttrs = TestResourceContainer.nonEnumAttrs
    enumAttrs = BaseTester.enumAttrs + ["cargoEnvironment"]

    def testAllValid(self):
        self._testAllValid(ElementCarrier)

    def testInvalidValues(self):
        self._testInvalidValues(ElementCarrier)

    def testInvalidType(self):
        self._testInvalidType(ElementCarrier)
=======
class TestElementCarrier(SeededTester, BaseTester):
    validType = ElementKind.ElementCarrier
    invalidTypes = getInvalidTypes(myType=validType)
    validFactory = ValidElementCarrierArgsFactory
    invalidFactory = InvalidCargoCarrierArgsFactory
    nonEnumAttrs = TestResourceContainer.nonEnumAttrs
    enumAttrs = BaseTester.enumAttrs + ["cargo_environment"]
    elementType = ElementCarrier
>>>>>>> a14263327e51c6b639d2ebd658e5b12615f88296


class ValidAgentArgsFactory(I_ValidArgsFactory):
    """
    Factory class for constructing dictionaries consisting of valid arguments for
    constructing an agent model, excepting the "type" field.
    """

<<<<<<< HEAD
    @staticmethod
    def makeKeywords() -> Dict[str, Any]:
        kw = ValidElementArgsFactory.makeKeywords()
        kw["activeTimeFraction"] = random.choice(NON_NEG_FLOATS)
=======
    validTImeFractions = FLOATS_IN_UNIT_INTERVAL

    @staticmethod
    def makeKeywords() -> Dict[str, Any]:
        kw = ValidElementArgsFactory.makeKeywords()
        kw["active_time_fraction"] = random.choice(
            ValidAgentArgsFactory.validTImeFractions
        )
>>>>>>> a14263327e51c6b639d2ebd658e5b12615f88296
        return kw


class InvalidAgentArgsFactory(I_InvalidArgsFactory):
    """
    Factory class for constructing dictionaries consisting of valid arguments for
    constructing an agent model, excepting the "type" field.
    """

<<<<<<< HEAD
=======
    invalidTimeFractions = (
        NEG_INTS + NEG_FLOATS + [x for x in NON_NEG_FLOATS + NON_NEG_INTS if x > 1]
    )
    badlyTypedTimeFractions = STRINGS

>>>>>>> a14263327e51c6b639d2ebd658e5b12615f88296
    @staticmethod
    def makeKeywords() -> Dict[str, Any]:
        kw = random.choice(
            (ValidElementArgsFactory, InvalidElementArgsFactory)
        ).makeKeywords()
<<<<<<< HEAD
        kw["activeTimeFraction"] = random.choice(NEG_INTS + NEG_FLOATS + STRINGS)
=======
        kw["active_time_fraction"] = random.choice(
            InvalidAgentArgsFactory.invalidTimeFractions
            + InvalidAgentArgsFactory.badlyTypedTimeFractions
        )
>>>>>>> a14263327e51c6b639d2ebd658e5b12615f88296
        return kw


class AgentTester(BaseTester):
    validFactory = ValidAgentArgsFactory
    invalidFactory = InvalidAgentArgsFactory
<<<<<<< HEAD
    nonEnumAttrs = BaseTester.nonEnumAttrs + ["activeTimeFraction"]


class TestHumanAgent(AgentTester):
    validTypes = [ElementKind.HumanAgent, None]
    invalidTypes = getInvalidTypes(myType=ElementKind.HumanAgent)

    def testAllValid(self):
        self._testAllValid(HumanAgent)

    def testInvalidValues(self):
        self._testInvalidValues(HumanAgent)

    def testInvalidType(self):
        self._testInvalidType(HumanAgent)


class TestRoboticAgent(AgentTester):
    validTypes = [ElementKind.RoboticAgent, None]
    invalidTypes = getInvalidTypes(myType=ElementKind.RoboticAgent)

    def testAllValid(self):
        self._testAllValid(RoboticAgent)

    def testInvalidValues(self):
        self._testInvalidValues(RoboticAgent)

    def testInvalidType(self):
        self._testInvalidType(RoboticAgent)
=======
    nonEnumAttrs = BaseTester.nonEnumAttrs + ["active_time_fraction"]


class TestHumanAgent(SeededTester, AgentTester):
    validType = ElementKind.HumanAgent
    invalidTypes = getInvalidTypes(myType=validType)
    elementType = HumanAgent


class TestRoboticAgent(SeededTester, AgentTester):
    validType = ElementKind.RoboticAgent
    invalidTypes = getInvalidTypes(myType=validType)
    elementType = RoboticAgent
>>>>>>> a14263327e51c6b639d2ebd658e5b12615f88296


class ValidVehicleArgsFactory(I_ValidArgsFactory):
    """
    Factory class for constructing dictionaries consisting of valid arguments for
    constructing a vehicle model, excepting the "type" field.
    """

<<<<<<< HEAD
    @staticmethod
    def makeKeywords() -> Dict[str, Any]:
        kw = ValidCargoCarrierArgsFactory.makeKeywords()
        kw["maxCrew"] = random.choice(NON_NEG_INTS)
=======
    validMaxFuels = NON_NEG_INTS + NON_NEG_FLOATS
    validMaxCrews = NON_NEG_INTS

    @staticmethod
    def makeKeywords() -> Dict[str, Any]:
        kw = ValidCargoCarrierArgsFactory.makeKeywords()
        kw["max_crew"] = random.choice(ValidVehicleArgsFactory.validMaxCrews)
        kw["max_fuel"] = random.choice(ValidVehicleArgsFactory.validMaxFuels)
>>>>>>> a14263327e51c6b639d2ebd658e5b12615f88296
        return kw


class InvalidVehicleArgsFactory(I_InvalidArgsFactory):
    """
    Factory class for constructing dictionaries consisting of invalid arguments for
    constructing a vehicle model, excepting the "type" field.
    """

<<<<<<< HEAD
=======
    invalidMaxFuels = NEG_INTS + NEG_FLOATS
    badlyTypedMaxFuels = STRINGS
    invalidMaxCrews = NEG_INTS + NEG_FLOATS
    badlyTypedMaxCrews = STRINGS

>>>>>>> a14263327e51c6b639d2ebd658e5b12615f88296
    @staticmethod
    def makeKeywords() -> Dict[str, Any]:
        kw = random.choice(
            (ValidCargoCarrierArgsFactory, InvalidCargoCarrierArgsFactory)
        ).makeKeywords()
<<<<<<< HEAD
        kw["maxCrew"] = random.choice(NEG_INTS + NEG_FLOATS + STRINGS)
=======
        rand = random.random()
        if rand < 0.25:
            maxFuelOptions = (
                InvalidVehicleArgsFactory.invalidMaxFuels
                + InvalidVehicleArgsFactory.badlyTypedMaxFuels
            )
            maxCrewOptions = (
                InvalidVehicleArgsFactory.invalidMaxCrews
                + InvalidVehicleArgsFactory.badlyTypedMaxCrews
            )
        elif rand < 0.5:
            maxFuelOptions = (
                InvalidVehicleArgsFactory.invalidMaxFuels
                + InvalidVehicleArgsFactory.badlyTypedMaxFuels
            )
            maxCrewOptions = ValidVehicleArgsFactory.validMaxCrews

        else:
            maxFuelOptions = ValidVehicleArgsFactory.validMaxFuels
            maxCrewOptions = (
                InvalidVehicleArgsFactory.invalidMaxCrews
                + InvalidVehicleArgsFactory.badlyTypedMaxCrews
            )

        kw["max_crew"] = random.choice(maxCrewOptions)
        kw["max_fuel"] = random.choice(maxFuelOptions)
>>>>>>> a14263327e51c6b639d2ebd658e5b12615f88296
        return kw


class VehicleTester(BaseTester):
<<<<<<< HEAD
    nonEnumAttrs = BaseTester.nonEnumAttrs + ["maxCrew"]
=======
    nonEnumAttrs = BaseTester.nonEnumAttrs + ["max_crew"]
>>>>>>> a14263327e51c6b639d2ebd658e5b12615f88296


class ValidPropulsiveArgsFactory(I_ValidArgsFactory):
    """
    Factory class for constructing dictionaries consisting of valid arguments for
    constructing a propulsive vehicle model, excepting the "type" field.
    """

<<<<<<< HEAD
    @staticmethod
    def makeKeywords() -> Dict[str, Any]:
        kw = ValidVehicleArgsFactory.makeKeywords()
        kw["omsISP"] = random.choice(NON_NEG_INTS + NON_NEG_FLOATS)
        kw["maxOMS"] = random.choice(NON_NEG_INTS + NON_NEG_FLOATS)
=======
    validISPs = NON_NEG_INTS + NON_NEG_FLOATS
    validPropIDs = NON_NEG_INTS + NEG_INTS

    @staticmethod
    def makeKeywords() -> Dict[str, Any]:
        kw = ValidVehicleArgsFactory.makeKeywords()
        kw["isp"] = random.choice(ValidPropulsiveArgsFactory.validISPs)
        kw["propellant_id"] = random.choice(ValidPropulsiveArgsFactory.validPropIDs)
>>>>>>> a14263327e51c6b639d2ebd658e5b12615f88296
        return kw


class InvalidPropulsiveArgsFactory(I_InvalidArgsFactory):
    """
    Factory class for constructing dictionaries consisting of invalid arguments for
    constructing a propulsive vehicle model, excepting the "type" field.
    """

<<<<<<< HEAD
=======
    invalidISPs = NEG_INTS + NEG_FLOATS
    badlyTypedISPs = STRINGS
    invalidPropIDs = NEG_FLOATS + NON_NEG_FLOATS
    badlyTypedPropIDs = STRINGS

>>>>>>> a14263327e51c6b639d2ebd658e5b12615f88296
    @staticmethod
    def makeKeywords() -> Dict[str, Any]:
        kw = random.choice(
            (ValidVehicleArgsFactory, InvalidVehicleArgsFactory)
        ).makeKeywords()
        rand = random.random()
        if rand < 0.25:
<<<<<<< HEAD
            kw["omsISP"] = random.choice(NEG_INTS + NEG_FLOATS + STRINGS)
            kw["maxOMS"] = random.choice(NEG_INTS + NEG_FLOATS + STRINGS)
        elif rand < 0.5:
            kw["omsISP"] = random.choice(NEG_INTS + NEG_FLOATS + STRINGS)
        else:
            kw["maxOMS"] = random.choice(NEG_INTS + NEG_FLOATS + STRINGS)
        return kw


class TestPropulsiveVehicle(VehicleTester):
    validTypes = [ElementKind.Propulsive, None]
    invalidTypes = getInvalidTypes(myType=ElementKind.Propulsive)
    validFactory = ValidPropulsiveArgsFactory
    invalidFactory = InvalidPropulsiveArgsFactory
    nonEnumAttrs = VehicleTester.nonEnumAttrs + ["maxOMS", "omsISP"]

    def testAllValid(self):
        self._testAllValid(PropulsiveVehicle)

    def testInvalidValues(self):
        self._testInvalidValues(PropulsiveVehicle)

    def testInvalidType(self):
        self._testInvalidType(PropulsiveVehicle)
=======
            ispOptions = (
                InvalidPropulsiveArgsFactory.invalidISPs
                + InvalidPropulsiveArgsFactory.badlyTypedISPs
            )
            propellantIDOptions = (
                InvalidPropulsiveArgsFactory.invalidPropIDs
                + InvalidPropulsiveArgsFactory.badlyTypedPropIDs
            )
        elif rand < 0.5:
            ispOptions = (
                InvalidPropulsiveArgsFactory.invalidISPs
                + InvalidPropulsiveArgsFactory.badlyTypedISPs
            )
            propellantIDOptions = ValidPropulsiveArgsFactory.validPropIDs
        else:
            ispOptions = ValidPropulsiveArgsFactory.validISPs
            propellantIDOptions = (
                InvalidPropulsiveArgsFactory.invalidPropIDs
                + InvalidPropulsiveArgsFactory.badlyTypedPropIDs
            )
        kw["isp"] = random.choice(ispOptions)
        kw["propellant_id"] = random.choice(propellantIDOptions)
        return kw


class TestPropulsiveVehicle(SeededTester, VehicleTester):
    validType = ElementKind.Propulsive
    invalidTypes = getInvalidTypes(myType=validType)
    validFactory = ValidPropulsiveArgsFactory
    invalidFactory = InvalidPropulsiveArgsFactory
    nonEnumAttrs = VehicleTester.nonEnumAttrs + ["max_fuel", "isp"]
    elementType = PropulsiveVehicle
>>>>>>> a14263327e51c6b639d2ebd658e5b12615f88296


class ValidSurfaceArgsFactory(I_ValidArgsFactory):
    """
    Factory class for constructing dictionaries consisting of valid arguments for
    constructing a surface vehicle model, excepting the "type" field.
    """

<<<<<<< HEAD
    @staticmethod
    def makeKeywords() -> Dict[str, Any]:
        kw = ValidVehicleArgsFactory.makeKeywords()
        kw["maxSpeed"] = random.choice(NON_NEG_INTS + NON_NEG_FLOATS)
        kw["maxFuel"] = random.choice(NON_NEG_INTS + NON_NEG_FLOATS)
=======
    validMaxSpeeds = NON_NEG_INTS + NON_NEG_FLOATS
    validFuelIDs = NON_NEG_INTS + NEG_INTS

    @staticmethod
    def makeKeywords() -> Dict[str, Any]:
        kw = ValidVehicleArgsFactory.makeKeywords()
        kw["max_speed"] = random.choice(ValidSurfaceArgsFactory.validMaxSpeeds)
        kw["fuel_id"] = random.choice(ValidSurfaceArgsFactory.validFuelIDs)
>>>>>>> a14263327e51c6b639d2ebd658e5b12615f88296
        return kw


class InvalidSurfaceArgsFactory(I_InvalidArgsFactory):
    """
    Factory class for constructing dictionaries consisting of invalid arguments for
    constructing a surface vehicle model, excepting the "type" field.
    """

<<<<<<< HEAD
=======
    invalidMaxSpeeds = NEG_INTS + NEG_FLOATS
    badlyTypedMaxSpeeds = STRINGS
    invalidFuelIDs = []
    badlyTypedFuelIDs = STRINGS

>>>>>>> a14263327e51c6b639d2ebd658e5b12615f88296
    @staticmethod
    def makeKeywords() -> Dict[str, Any]:
        kw = random.choice(
            (ValidVehicleArgsFactory, InvalidVehicleArgsFactory)
        ).makeKeywords()
        rand = random.random()
        if rand < 0.25:
<<<<<<< HEAD
            kw["maxSpeed"] = random.choice(NEG_INTS + NEG_FLOATS + STRINGS)
            kw["maxFuel"] = random.choice(NEG_INTS + NEG_FLOATS + STRINGS)
        elif rand < 0.5:
            kw["maxSpeed"] = random.choice(NEG_INTS + NEG_FLOATS + STRINGS)
        else:
            kw["maxFuel"] = random.choice(NEG_INTS + NEG_FLOATS + STRINGS)
        return kw


class TestSurfaceVehicle(VehicleTester):
    validTypes = [ElementKind.Surface, None]
    invalidTypes = getInvalidTypes(myType=ElementKind.Surface)
    validFactory = ValidSurfaceArgsFactory
    invalidFactory = InvalidSurfaceArgsFactory
    nonEnumAttrs = VehicleTester.nonEnumAttrs + ["maxFuel", "maxSpeed"]

    def testAllValid(self):
        self._testAllValid(SurfaceVehicle)

    def testInvalidValues(self):
        self._testInvalidValues(SurfaceVehicle)

    def testInvalidType(self):
        self._testInvalidType(SurfaceVehicle)


class TestPatchModel(unittest.TestCase):
    """
    Tests for the patchModel function.
    Partitions:
    Number of required fields:
        0
        > 0
    Number of removed fields:
        0
        > 0
    """

    class Model(BaseModel):
        a: int
        b: float = Field(description="test")
        c: conint(ge=0)

    def testNoRequiredNoRemoved(self):
        Patched = patchModel(TestPatchModel.Model)
        for fieldName, field in TestPatchModel.Model.__fields__.items():
            expField = copy.deepcopy(field)
            expField.required = False
            expField.default = None
            actualField = Patched.__fields__[fieldName]
            # using repr b/c __eq__ isn't implemented for Field
            self.assertEqual(repr(expField), repr(actualField))

    def testSomeRequired(self):
        required = {"a"}
        Patched = patchModel(TestPatchModel.Model, required_fields=required)
        for fieldName, field in TestPatchModel.Model.__fields__.items():
            if fieldName in required:
                expField = field
            else:
                expField = copy.deepcopy(field)
                expField.required = False
                expField.default = None
            actualField = Patched.__fields__[fieldName]
            self.assertEqual(repr(expField), repr(actualField))

    def testSomeRemoved(self):
        removed = {"c"}
        Patched = patchModel(TestPatchModel.Model, removed_fields=removed)
        self.assertTrue(Patched.__fields__.keys().isdisjoint(removed))
        self.assertEqual(
            set(TestPatchModel.Model.__fields__.keys()) - removed,
            set(Patched.__fields__.keys()),
        )
=======
            maxSpeedOptions = (
                InvalidSurfaceArgsFactory.invalidMaxSpeeds
                + InvalidSurfaceArgsFactory.badlyTypedMaxSpeeds
            )
            fuelIDOptions = (
                InvalidSurfaceArgsFactory.invalidFuelIDs
                + InvalidSurfaceArgsFactory.badlyTypedFuelIDs
            )
        elif rand < 0.5:
            maxSpeedOptions = (
                InvalidSurfaceArgsFactory.invalidMaxSpeeds
                + InvalidSurfaceArgsFactory.badlyTypedMaxSpeeds
            )
            fuelIDOptions = ValidSurfaceArgsFactory.validFuelIDs
        else:
            maxSpeedOptions = ValidSurfaceArgsFactory.validMaxSpeeds
            fuelIDOptions = (
                InvalidSurfaceArgsFactory.invalidFuelIDs
                + InvalidSurfaceArgsFactory.badlyTypedFuelIDs
            )
        kw["max_speed"] = random.choice(maxSpeedOptions)
        kw["fuel_id"] = random.choice(fuelIDOptions)
        return kw


class TestSurfaceVehicle(SeededTester, VehicleTester):
    validType = ElementKind.Surface
    invalidTypes = getInvalidTypes(myType=validType)
    validFactory = ValidSurfaceArgsFactory
    invalidFactory = InvalidSurfaceArgsFactory
    nonEnumAttrs = VehicleTester.nonEnumAttrs + ["max_fuel", "max_speed"]
    elementType = SurfaceVehicle
>>>>>>> a14263327e51c6b639d2ebd658e5b12615f88296
