import random
import unittest
from abc import ABC, abstractmethod
from typing import Any

from pydantic import ValidationError

from spacenet.schemas.element import Element, ResourceContainer, ElementCarrier, \
    HumanAgent, RoboticAgent, PropulsiveVehicle, SurfaceVehicle, Environment, ElementKind

NUM_ATTEMPTS = 50
STRINGS = ["foo", "bar", "baz"]
NON_NEG_INTS = list(range(10))
NEG_INTS = [-1 * (n + 1) for n in NON_NEG_INTS]
NON_NEG_FLOATS = list(i / 2 for i in range(10))
NEG_FLOATS = list(-1 * i for i in range(1, 10))
FLOATS_IN_UNIT_INTERVAL = [i / 9 for i in range(10)]


def getInvalidTypes(myType: ElementKind) -> list[ElementKind]:
    return [kind for kind in ElementKind if kind != myType]


class ValidElementArgsFactory:
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
    def makeKeywords() -> dict[str, Any]:
        """
        Make valid keyword arguments for constructing an element model.

        :return: the resulting keyword argument dictionary
        """
        kw = {
            "name": random.choice(ValidElementArgsFactory.validNames),
            "description": random.choice(ValidElementArgsFactory.validDescs),
            "classOfSupply": random.choice(ValidElementArgsFactory.validCoS),
            "environment": random.choice(ValidElementArgsFactory.validEnvironments),
            "accommodationMass": random.choice(ValidElementArgsFactory.validAccMasses),
            "mass": random.choice(ValidElementArgsFactory.validMasses),
            "volume": random.choice(ValidElementArgsFactory.validVolumes)
        }
        return kw


class InvalidElementArgsFactory:
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
    def makeKeywords() -> dict[str, Any]:
        """
        Make invalid or badly-typed keyword arguments for constructing an element model.

        :return: the resulting keyword argument dictionary
        """
        invalidSelected = 0
        attrs = ["Names", "Descs", "CoS", "Environments",
                 "AccMasses", "Masses", "Volumes"]
        fieldNames = ["name", "description", "classOfSupply", "environment",
                      "accommodationMass", "mass", "volume"]
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
            options = InvalidElementArgsFactory.getOptions(attr)[1:]  # exclude first valid
            option = random.choice(options)
            attrValue = random.choice(option)
            kw[fieldName] = attrValue
        return kw

    @staticmethod
    def getOptions(attr: str) -> list:
        options = [getattr(ValidElementArgsFactory, f"valid{attr}"),
                   getattr(InvalidElementArgsFactory, f"badlyTyped{attr}"),
                   getattr(InvalidElementArgsFactory, f"invalid{attr}")]
        return [opt for opt in options if len(opt) > 0]


class BaseTester(unittest.TestCase):
    # Should be set by subclasses
    validTypes = None
    invalidTypes = None
    validFactory = None
    invalidFactory = None
    nonEnumAttrs = ["name", "description", "accommodationMass", "mass", "volume"]
    enumAttrs = ["classOfSupply", "environment"]

    def assertMatches(self, kw: dict, element: Element):
        for nonEnumAttr in self.nonEnumAttrs:
            self.assertEqual(kw[nonEnumAttr], getattr(element, nonEnumAttr),
                             msg=f"Expected element.{nonEnumAttr} = {kw[nonEnumAttr]},"
                                 f"but was {getattr(element, nonEnumAttr)}")
        for enumAttr in self.enumAttrs:
            self.assertEqual(kw[enumAttr], getattr(element, enumAttr).value,
                             msg=f"Expected element.{enumAttr}.value = {kw[enumAttr]},"
                                 f"but was {getattr(element, enumAttr).value}")
        self.assertEqual(self.validTypes[0], element.type,
                         msg=f"Expected element.type to be {self.validTypes[0]}")

    def _testAllValid(self, elementType):
        factory = self.validFactory()
        for _ in range(NUM_ATTEMPTS):
            for type_ in self.validTypes:
                kw = factory.makeKeywords()
                if type_:
                    kw |= {"type": type_}
                element = elementType(**kw)
                self.assertMatches(kw, element)

    def _testInvalidValues(self, elementType):
        factory = self.invalidFactory()
        for _ in range(NUM_ATTEMPTS):
            kw = factory.makeKeywords()
            with self.assertRaises(ValidationError, msg=f"{kw} should have raised an error"):
                elementType(**kw)

    def _testInvalidType(self, elementType):
        factory = self.validFactory()
        kw = factory.makeKeywords()
        for type_ in self.invalidTypes:
            kw |= {"type": type_}
            with self.assertRaises(ValidationError, msg=f"{kw} should have raised an error"):
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


class ValidCargoCarrierArgsFactory:
    """
    Factory class for constructing dictionaries consisting of valid arguments for
    constructing a resource container or element carrier model, excepting the "type" field.
    """
    validMaxCargoMass = NON_NEG_FLOATS
    validMaxCargoVolume = NON_NEG_FLOATS

    @staticmethod
    def makeKeywords() -> dict[str, Any]:
        kw = ValidElementArgsFactory.makeKeywords()
        kw["maxCargoMass"] = random.choice(ValidCargoCarrierArgsFactory.validMaxCargoMass)
        kw["maxCargoVolume"] = random.choice(ValidCargoCarrierArgsFactory.validMaxCargoVolume)
        return kw


class InvalidCargoCarrierArgsFactory:
    """
    Factory class for constructing dictionaries consisting of invalid arguments for
    constructing a resource container or element carrier model, excepting the "type" field.
    """
    invalidMaxCargoMass = NEG_INTS + NEG_FLOATS
    badlyTypedMaxCargoMass = STRINGS
    invalidMaxCargoVolume = NEG_INTS + NEG_FLOATS
    badlyTypedMaxCargoVolume = STRINGS

    @staticmethod
    def makeKeywords() -> dict[str, Any]:
        kw = ValidCargoCarrierArgsFactory.makeKeywords()
        rand = random.random()
        if random.random() < 0.25:
            kw["maxCargoMass"] = random.choice(
                InvalidCargoCarrierArgsFactory.invalidMaxCargoMass +
                InvalidCargoCarrierArgsFactory.badlyTypedMaxCargoMass)
            kw["maxCargoVolume"] = random.choice(
                InvalidCargoCarrierArgsFactory.invalidMaxCargoVolume +
                InvalidCargoCarrierArgsFactory.badlyTypedMaxCargoVolume)
        elif rand < 0.5:
            kw["maxCargoMass"] = random.choice(
                InvalidCargoCarrierArgsFactory.invalidMaxCargoMass +
                InvalidCargoCarrierArgsFactory.badlyTypedMaxCargoMass)
        else:
            kw["maxCargoVolume"] = random.choice(
                InvalidCargoCarrierArgsFactory.invalidMaxCargoVolume +
                InvalidCargoCarrierArgsFactory.badlyTypedMaxCargoVolume)
        return kw


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


class ValidElementCarrierArgsFactory:
    """
    Factory class for constructing dictionaries consisting of valid arguments for
    constructing a element carrier model, excepting the "type" field.
    """

    @staticmethod
    def makeKeywords() -> dict[str, Any]:
        kw = ValidCargoCarrierArgsFactory.makeKeywords()
        kw["cargoEnvironment"] = random.choice([variant.value for variant in Environment])
        return kw


class InvalidElementCarrierArgsFactory:
    """
    Factory class for constructing dictionaries consisting of invalid arguments for
    constructing an element carrier model, excepting the "type" field.
    """
    invalidCargoEnvironments = ["Foo", "Bar", "Baz"]
    badlyTypedCargoEnvironments = list(range(10))

    @staticmethod
    def makeKeywords() -> dict[str, Any]:
        kw = random.choice(
            (ValidCargoCarrierArgsFactory, InvalidCargoCarrierArgsFactory)).makeKeywords()
        kw["cargoEnvironment"] = random.choice(
            InvalidElementCarrierArgsFactory.invalidCargoEnvironments +
            InvalidElementCarrierArgsFactory.badlyTypedCargoEnvironments)
        return kw


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


class ValidAgentArgsFactory:
    """
    Factory class for constructing dictionaries consisting of valid arguments for
    constructing an agent model, excepting the "type" field.
    """

    @staticmethod
    def makeKeywords() -> dict[str, Any]:
        kw = ValidElementArgsFactory.makeKeywords()
        kw["activeTimeFraction"] = random.choice(NON_NEG_FLOATS)
        return kw


class InvalidAgentArgsFactory:
    """
        Factory class for constructing dictionaries consisting of valid arguments for
        constructing an agent model, excepting the "type" field.
        """

    @staticmethod
    def makeKeywords() -> dict[str, Any]:
        kw = random.choice((ValidElementArgsFactory, InvalidElementArgsFactory)).makeKeywords()
        kw["activeTimeFraction"] = random.choice(NEG_INTS + NEG_FLOATS + STRINGS)
        return kw


class AgentTester(BaseTester):
    validFactory = ValidAgentArgsFactory
    invalidFactory = InvalidAgentArgsFactory
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
