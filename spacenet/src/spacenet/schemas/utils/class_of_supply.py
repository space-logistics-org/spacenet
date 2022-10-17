"""Defines object schemas for class of supply."""

from enum import Enum


class ClassOfSupply(int, Enum):
    """
    Enumeration of the ten top-level classes of supply and sub-classes of supply.
    """

    COS_0 = 0
    COS_1 = 1
    COS_2 = 2
    COS_3 = 3
    COS_4 = 4
    COS_5 = 5
    COS_6 = 6
    COS_7 = 7
    COS_8 = 8
    COS_9 = 9
    COS_10 = 10
    COS_101 = 101
    COS_102 = 102
    COS_103 = 103
    COS_104 = 104
    COS_105 = 105
    COS_106 = 106
    COS_201 = 201
    COS_202 = 202
    COS_203 = 203
    COS_204 = 204
    COS_205 = 205
    COS_206 = 206
    COS_301 = 301
    COS_302 = 302
    COS_303 = 303
    COS_304 = 304
    COS_305 = 305
    COS_306 = 306
    COS_401 = 401
    COS_402 = 402
    COS_403 = 403
    COS_404 = 404
    COS_405 = 405
    COS_501 = 501
    COS_502 = 502
    COS_601 = 601
    COS_602 = 602
    COS_603 = 603
    COS_701 = 701
    COS_702 = 702
    COS_703 = 703
    COS_801 = 801
    COS_802 = 802
    COS_803 = 803
    COS_804 = 804
    COS_805 = 805
    COS_806 = 806
    COS_901 = 901
    COS_902 = 902
    COS_4011 = 4011
    COS_4012 = 4012
    COS_8041 = 8041
    COS_8042 = 8042
    COS_9021 = 9021
    COS_9022 = 9022
    COS_9023 = 9023
    COS_9024 = 9024

    @property
    def name(self) -> str:
        """
        :return: the name of this class of supply
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
    ClassOfSupply.COS_703: "Failed Pairs",
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
