from abc import ABC
from enum import Enum

from pydantic import BaseModel, Field, conint
from uuid import UUID, uuid4


class ClassOfSupply(int, Enum):
    """
    An enumeration of the ten main classes of supply, and the sub-classes of supply.
    """

    CoS0 = 0
    CoS1 = 1
    CoS2 = 2
    CoS3 = 3
    CoS4 = 4
    CoS5 = 5
    CoS6 = 6
    CoS7 = 7
    CoS8 = 8
    CoS9 = 9
    CoS10 = 10
    CoS101 = 101
    CoS102 = 102
    CoS103 = 103
    CoS104 = 104
    CoS105 = 105
    CoS106 = 106
    CoS201 = 201
    CoS202 = 202
    CoS203 = 203
    CoS204 = 204
    CoS205 = 205
    CoS206 = 206
    CoS301 = 301
    CoS302 = 302
    CoS303 = 303
    CoS304 = 304
    CoS305 = 305
    CoS306 = 306
    CoS401 = 401
    CoS402 = 402
    CoS403 = 403
    CoS404 = 404
    CoS405 = 405
    CoS501 = 501
    CoS502 = 502
    CoS601 = 601
    CoS602 = 602
    CoS603 = 603
    CoS701 = 701
    CoS702 = 702
    CoS703 = 703
    CoS801 = 801
    CoS802 = 802
    CoS803 = 803
    CoS804 = 804
    CoS805 = 805
    CoS806 = 806
    CoS901 = 901
    CoS902 = 902
    CoS4011 = 4011
    CoS4012 = 4012
    CoS8041 = 8041
    CoS8042 = 8042
    CoS9021 = 9021
    CoS9022 = 9022
    CoS9023 = 9023
    CoS9024 = 9024

    @property
    def name(self) -> str:
        return COS_TO_NAME[self]


COS_TO_NAME = {
    ClassOfSupply.CoS0: "None",
    ClassOfSupply.CoS1: "Propellants and Fuels",
    ClassOfSupply.CoS2: "Crew Provisions",
    ClassOfSupply.CoS3: "Crew Operations",
    ClassOfSupply.CoS4: "Maintenance and Upkeep",
    ClassOfSupply.CoS5: "Stowage and Restraint",
    ClassOfSupply.CoS6: "Exploration and Research",
    ClassOfSupply.CoS7: "Waste and Disposal",
    ClassOfSupply.CoS8: "Habitation and Infrastructure",
    ClassOfSupply.CoS9: "Transportation and Carriers",
    ClassOfSupply.CoS10: "Miscellaneous",
    ClassOfSupply.CoS101: "Cryogens",
    ClassOfSupply.CoS102: "Hypergols",
    ClassOfSupply.CoS103: "Nuclear Fuel",
    ClassOfSupply.CoS104: "Petroleum Fuels",
    ClassOfSupply.CoS105: "Other Fuels",
    ClassOfSupply.CoS106: "Green Propellant",
    ClassOfSupply.CoS201: "Water and Support Equipment",
    ClassOfSupply.CoS202: "Food and Support Equipment",
    ClassOfSupply.CoS203: "Gases",
    ClassOfSupply.CoS204: "Hygiene Items",
    ClassOfSupply.CoS205: "Clothing",
    ClassOfSupply.CoS206: "Personal Items",
    ClassOfSupply.CoS301: "Office Equipment and Supplies",
    ClassOfSupply.CoS302: "EVA Equipment and Consumables",
    ClassOfSupply.CoS303: "Health Equipment and Consumables",
    ClassOfSupply.CoS304: "Safety Equipment",
    ClassOfSupply.CoS305: "Communications Equipment",
    ClassOfSupply.CoS306: "Computers and Support Equipment",
    ClassOfSupply.CoS401: "Spares and Repair Parts",
    ClassOfSupply.CoS402: "Maintenance Tools",
    ClassOfSupply.CoS403: "Lubricants and Bulk Chemicals",
    ClassOfSupply.CoS404: "Batteries",
    ClassOfSupply.CoS405: "Cleaning Equipment and Consumables",
    ClassOfSupply.CoS501: "Cargo Containers and Restraints",
    ClassOfSupply.CoS502: "Inventory Management Equipment",
    ClassOfSupply.CoS601: "Science Payloads and Instruments",
    ClassOfSupply.CoS602: "Field Equipment",
    ClassOfSupply.CoS603: "Samples",
    ClassOfSupply.CoS701: "Waste",
    ClassOfSupply.CoS702: "Waste Management Equipment",
    ClassOfSupply.CoS703: "Failed Pairs",
    ClassOfSupply.CoS801: "Habitation Facilities",
    ClassOfSupply.CoS802: "Surface Mobility Systems",
    ClassOfSupply.CoS803: "Power Systems",
    ClassOfSupply.CoS804: "Robotic Systems",
    ClassOfSupply.CoS805: "Resource Utilization Systems",
    ClassOfSupply.CoS806: "Orbiting Service Systems",
    ClassOfSupply.CoS901: "Carriers, Non-propulsive Elements",
    ClassOfSupply.CoS902: "Propulsive Elements",
    ClassOfSupply.CoS4011: "Spares",
    ClassOfSupply.CoS4012: "Repair Parts",
    ClassOfSupply.CoS8041: "Science Robotics",
    ClassOfSupply.CoS8042: "Construction/Maintenance Robotics",
    ClassOfSupply.CoS9021: "Launch Vehicles",
    ClassOfSupply.CoS9022: "Upper Stages/In-Space Propulsion Systems",
    ClassOfSupply.CoS9023: "Descent Stages",
    ClassOfSupply.CoS9024: "Ascent Stages",
}


class Environment(str, Enum):
    """
    An enumeration of the environments an element can be carried in or carry elements in.
    """

    Pressurized = "Pressurized"
    Unpressurized = "Unpressurized"


class ElementKind(str, Enum):
    """
    An enumeration of all the types of Element.
    """

    Element = "Element"
    ResourceContainer = "ResourceContainer"
    ElementCarrier = "ElementCarrier"
    HumanAgent = "HumanAgent"
    RoboticAgent = "RoboticAgent"
    Vehicle = "Vehicle"
    Propulsive = "Propulsive"
    Surface = "Surface"


class DomainModel(BaseModel):
    """
    A base class which generates a unique ID for each instantiation of a schema.

    Uniqueness comes from random number generation, so collisions are possible, but very
    unlikely.
    """

    id_: UUID = Field(default_factory=uuid4, title="ID", const=True)


def typeFieldWithDefault(default: ElementKind) -> Field:
    """
    Construct a field with description "the element's type", which must be the default value,
    provided by the default parameter.

    :param default: the desired default parameter
    :return: the constructed field
    """
    return Field(default=default, description="the element's type", const=True)


class Element(DomainModel):
    """
    A generic element.
    """

    name: str = Field(..., title="Name", description="name of the element")
    description: str = Field(
        ..., title="Description", description="short description of the element"
    )
    classOfSupply: ClassOfSupply = Field(
        ..., title="Class of Supply", description="class of supply number"
    )
    type: ElementKind = typeFieldWithDefault(ElementKind.Element)
    environment: Environment = Field(
        ..., title="Environment", description="the element's environment"
    )
    accommodationMass: float = Field(
        ...,
        ge=0,
        title="Accommodation Mass",
        description="the amount of additional COS5 "
        "required to pack the element inside a"
        " carrier.",
    )
    mass: float = Field(..., ge=0, title="Mass", description="mass in kg")
    volume: float = Field(..., ge=0, title="Volume", description="volume in m^3")


class CargoCarrier(Element, ABC):
    """
    Abstract base class representing a carrier of some sort of cargo, elements or resources.
    """

    maxCargoMass: float = Field(
        ..., ge=0, title="Max Cargo Mass", description="cargo capacity constraint (kg)"
    )
    maxCargoVolume: float = Field(
        ...,
        ge=0,
        title="Maximum Cargo Volume",
        description="cargo capacity constraint (m^3)",
    )


class ResourceContainer(CargoCarrier):
    """
    An element representing a container for resources.
    """

    type: ElementKind = typeFieldWithDefault(ElementKind.ResourceContainer)


class ElementCarrier(CargoCarrier):
    """
    An element which can carry other elements.
    """

    type: ElementKind = typeFieldWithDefault(ElementKind.ElementCarrier)
    cargoEnvironment: Environment = Field(
        ...,
        title="Cargo Environment",
        description="the cargo's environment — if "
        "unpressurized, "
        "cannot add pressurized elements as "
        "cargo",
    )


class Agent(Element, ABC):
    """
    An abstract base class representing a generic Agent element.
    """

    activeTimeFraction: float = Field(
        ...,
        title="Active Time Fraction",
        description="the fraction of the day that an agent is active (available)",
        ge=0,
    )


class HumanAgent(Agent):
    """
    An element representing a human agent, like a crew member.
    """

    type: ElementKind = typeFieldWithDefault(ElementKind.HumanAgent)


class RoboticAgent(Agent):
    """
    An element representing a robotic agent.
    """

    type: ElementKind = typeFieldWithDefault(ElementKind.RoboticAgent)


class Vehicle(Element, ABC):
    """
    An abstract base class representing a generic Vehicle, surface or propulsive.
    """

    type: ElementKind = typeFieldWithDefault(ElementKind.Vehicle)
    maxCrew: conint(strict=True, ge=0) = Field(
        ..., title="Maximum Crew Count", description="crew capacity constraint"
    )


class PropulsiveVehicle(Vehicle, CargoCarrier):
    """
    An element representing a vehicle with its own propulsion via OMS.
    """

    type: ElementKind = typeFieldWithDefault(ElementKind.Propulsive)
    omsISP: float = Field(
        ..., ge=0, title="OMS ISP", description="OMS specific impulse (s)"
    )
    maxOMS: float = Field(
        ..., ge=0, title="Maximum OMS Fuel", description="maximum OMS fuel (units)"
    )
    # omsID: ResourceID


class SurfaceVehicle(Vehicle, CargoCarrier):
    """
    An element representing a surface vehicle.
    """

    type: ElementKind = typeFieldWithDefault(ElementKind.Surface)
    maxSpeed: float = Field(
        ..., ge=0, title="Maximum Speed", description="maximum speed (kph)"
    )
    maxFuel: float = Field(
        ..., ge=0, title="Maximum Fuel", description="maximum fuel (units)"
    )
    # fuelID: ResourceID
