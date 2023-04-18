"""Defines object schemas for class of supply."""

from enum import IntEnum

import enum_tools.documentation

enum_tools.documentation.INTERACTIVE = True


@enum_tools.documentation.document_enum
class ClassOfSupply(IntEnum):
    """
    Enumeration of the ten top-level classes of supply and sub-classes of supply.
    """

    COS_0 = 0  # doc: None
    COS_1 = 1  # doc: Propellants and Fuels
    COS_2 = 2  # doc: Crew Provisions
    COS_3 = 3  # doc: Crew Operations
    COS_4 = 4  # doc: Maintenance and Upkeep
    COS_5 = 5  # doc: Stowage and Restraint
    COS_6 = 6  # doc: Exploration and Research
    COS_7 = 7  # doc: Waste and Disposal
    COS_8 = 8  # doc: Habitation and Infrastructure
    COS_9 = 9  # doc: Transportation and Carriers
    COS_10 = 10  # doc: Miscellaneous
    COS_101 = 101  # doc: Cryogens
    COS_102 = 102  # doc: Hypergols
    COS_103 = 103  # doc: Nuclear Fuel
    COS_104 = 104  # doc: Petroleum Fuels
    COS_105 = 105  # doc: Other Fuels
    COS_106 = 106  # doc: Green Propellant
    COS_201 = 201  # doc: Water and Support Equipment
    COS_202 = 202  # doc: Food and Support Equipment
    COS_203 = 203  # doc: Gases
    COS_204 = 204  # doc: Hygiene Items
    COS_205 = 205  # doc: Clothing
    COS_206 = 206  # doc: Personal Items
    COS_301 = 301  # doc: Office Equipemnt and Supplies
    COS_302 = 302  # doc: EVA Equipment and Consumables
    COS_303 = 303  # doc: Health Equipment and Consumables
    COS_304 = 304  # doc: Safety Equipment
    COS_305 = 305  # doc: Communications Equipment
    COS_306 = 306  # doc: Computers and Support Equipment
    COS_401 = 401  # doc: Spares and Repair Parts
    COS_402 = 402  # doc: Maintenance Tools
    COS_403 = 403  # doc: Lubricants and Bulk Chemicals
    COS_404 = 404  # doc: Batteries
    COS_405 = 405  # doc: Cleaning Equipment and Consumables
    COS_501 = 501  # doc: Cargo Containers and Restraints
    COS_502 = 502  # doc: Inventory Management Equipment
    COS_601 = 601  # doc: Science Payloads and Instruments
    COS_602 = 602  # doc: Field Equipment
    COS_603 = 603  # doc: Samples
    COS_701 = 701  # doc: Waste
    COS_702 = 702  # doc: Waste Management Equipment
    COS_703 = 703  # doc: Failed Parts
    COS_801 = 801  # doc: Habitation Facilities
    COS_802 = 802  # doc: Surface Mobility Systems
    COS_803 = 803  # doc: Power Systems
    COS_804 = 804  # doc: Robotic Systems
    COS_805 = 805  # doc: Resource Utilization Systems
    COS_806 = 806  # doc: Orbiting Service Systems
    COS_901 = 901  # doc: Carriers, Non-propulsive Elements
    COS_902 = 902  # doc: Propulsive Elements
    COS_4011 = 4011  # doc: Spares
    COS_4012 = 4012  # doc: Repair Parts
    COS_8041 = 8041  # doc: Science Robotics
    COS_8042 = 8042  # doc: Construction/Maintenance Robotics
    COS_9021 = 9021  # doc: Launch Vehicles
    COS_9022 = 9022  # doc: Upper Stages/In-Space Propulsion Systems
    COS_9023 = 9023  # doc: Descent Stages
    COS_9024 = 9024  # doc: Ascent Stages

    def get_name(self) -> str:
        """
        Gets the name of this class of supply.
        """
        return COS_TO_NAME[self]


COS_TO_NAME = {
    ClassOfSupply.COS_0: "None",
    ClassOfSupply.COS_1: "Propellants and Fuels",
    ClassOfSupply.COS_2: "Crew Provisions",
    ClassOfSupply.COS_3: "Crew Operations",
    ClassOfSupply.COS_4: "Maintenance and Upkeep",
    ClassOfSupply.COS_5: "Stowage and Restraint",
    ClassOfSupply.COS_6: "Exploration and Research",
    ClassOfSupply.COS_7: "Waste and Disposal",
    ClassOfSupply.COS_8: "Habitation and Infrastructure",
    ClassOfSupply.COS_9: "Transportation and Carriers",
    ClassOfSupply.COS_10: "Miscellaneous",
    ClassOfSupply.COS_101: "Cryogens",
    ClassOfSupply.COS_102: "Hypergols",
    ClassOfSupply.COS_103: "Nuclear Fuel",
    ClassOfSupply.COS_104: "Petroleum Fuels",
    ClassOfSupply.COS_105: "Other Fuels",
    ClassOfSupply.COS_106: "Green Propellant",
    ClassOfSupply.COS_201: "Water and Support Equipment",
    ClassOfSupply.COS_202: "Food and Support Equipment",
    ClassOfSupply.COS_203: "Gases",
    ClassOfSupply.COS_204: "Hygiene Items",
    ClassOfSupply.COS_205: "Clothing",
    ClassOfSupply.COS_206: "Personal Items",
    ClassOfSupply.COS_301: "Office Equipment and Supplies",
    ClassOfSupply.COS_302: "EVA Equipment and Consumables",
    ClassOfSupply.COS_303: "Health Equipment and Consumables",
    ClassOfSupply.COS_304: "Safety Equipment",
    ClassOfSupply.COS_305: "Communications Equipment",
    ClassOfSupply.COS_306: "Computers and Support Equipment",
    ClassOfSupply.COS_401: "Spares and Repair Parts",
    ClassOfSupply.COS_402: "Maintenance Tools",
    ClassOfSupply.COS_403: "Lubricants and Bulk Chemicals",
    ClassOfSupply.COS_404: "Batteries",
    ClassOfSupply.COS_405: "Cleaning Equipment and Consumables",
    ClassOfSupply.COS_501: "Cargo Containers and Restraints",
    ClassOfSupply.COS_502: "Inventory Management Equipment",
    ClassOfSupply.COS_601: "Science Payloads and Instruments",
    ClassOfSupply.COS_602: "Field Equipment",
    ClassOfSupply.COS_603: "Samples",
    ClassOfSupply.COS_701: "Waste",
    ClassOfSupply.COS_702: "Waste Management Equipment",
    ClassOfSupply.COS_703: "Failed Parts",
    ClassOfSupply.COS_801: "Habitation Facilities",
    ClassOfSupply.COS_802: "Surface Mobility Systems",
    ClassOfSupply.COS_803: "Power Systems",
    ClassOfSupply.COS_804: "Robotic Systems",
    ClassOfSupply.COS_805: "Resource Utilization Systems",
    ClassOfSupply.COS_806: "Orbiting Service Systems",
    ClassOfSupply.COS_901: "Carriers, Non-propulsive Elements",
    ClassOfSupply.COS_902: "Propulsive Elements",
    ClassOfSupply.COS_4011: "Spares",
    ClassOfSupply.COS_4012: "Repair Parts",
    ClassOfSupply.COS_8041: "Science Robotics",
    ClassOfSupply.COS_8042: "Construction/Maintenance Robotics",
    ClassOfSupply.COS_9021: "Launch Vehicles",
    ClassOfSupply.COS_9022: "Upper Stages/In-Space Propulsion Systems",
    ClassOfSupply.COS_9023: "Descent Stages",
    ClassOfSupply.COS_9024: "Ascent Stages",
}
