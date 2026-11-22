"""
Validates the reference Artemis campaign (``artemis_add_campaign.py``)
against published NASA and other data.

Usage: ``python artemis/validation.py`` prints a Markdown table of results.
"""

import math
import sys
from pathlib import Path
from typing import List, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent))

# pylint: disable=wrong-import-position
from artemis_add_campaign import (  # noqa: E402
    CampaignBuilder,
    CampaignParameters,
    build_scenario,
)

from spacenet import schemas as s  # noqa: E402
from spacenet.simulation import FullSimulator  # noqa: E402
from spacenet.simulation.analysis import CostAnalysis, ISRUAnalysis  # noqa: E402
from spacenet.simulation.events import G0  # noqa: E402
from spacenet.validation import (  # noqa: E402
    CheckKind,
    Reference,
    ValidationResult,
    compare,
    max_payload,
    number,
    report_markdown,
)

SLS_FACT_SHEET = (
    "NASA SLS Block 1B fact sheet (Dec. 2025)",
    "https://www.nasa.gov/wp-content/uploads/2026/02/"
    "sls-5644-sls-block-1b-fact-sheet-dec2025-508.pdf",
)
ESM_PROPULSION = (
    "NASA NTRS 20180004488 (ESM propulsion subsystem)",
    "https://ntrs.nasa.gov/api/citations/20180004488/downloads/20180004488.pdf",
)
NRHO_PAPER = (
    "NASA, NRHO: The Artemis Orbit (Architecture Workshop, 2023)",
    "https://www.nasa.gov/wp-content/uploads/2023/10/nrho-artemis-orbit.pdf",
)
ADD = (
    "NASA Moon to Mars Architecture Definition Document, Rev. C (2025)",
    "https://ntrs.nasa.gov/citations/20250010956",
)
LOGISTICS = (
    "NASA, Logistics Beyond LEO (ASCEND 2023)",
    "https://ntrs.nasa.gov/citations/20230013896",
)
FSP = (
    "NASA Fission Surface Power (IAC 2024)",
    "https://ntrs.nasa.gov/citations/20240011694",
)
OIG = (
    "NASA OIG IG-22-003 (Artemis missions, 2022)",
    "https://oig.nasa.gov/docs/IG-22-003.pdf",
)
PILOT_PLANT = (
    "NASA NTRS 20205008294 (Linne et al., Lunar Water Pilot Plant, ASCEND 2020)",
    "https://ntrs.nasa.gov/citations/20205008294",
)

#: Enthalpy of formation (kJ/mol) of liquid water (NIST Chemistry WebBook).
WATER_FORMATION_ENTHALPY = 285.83
#: Standard atomic weights (g/mol) of hydrogen and oxygen (IUPAC).
HYDROGEN, OXYGEN = 1.008, 15.999

REFERENCES = {
    reference.key: reference
    for reference in [
        Reference(
            "sls_block_1_tli",
            "SLS Block 1 payload to TLI",
            (27_000.0, None),
            "kg",
            *SLS_FACT_SHEET,
            note="'more than 27 t' to the Moon (Orion and payloads)",
        ),
        Reference(
            "sls_block_1b_tli",
            "SLS Block 1B crew payload to TLI",
            38_000.0,
            "kg",
            *SLS_FACT_SHEET,
            note="approximately 38 t including Orion and a 10 t co-manifested payload",
        ),
        Reference(
            "esm_propellant",
            "Orion ESM usable propellant",
            8_602.0,
            "kg",
            *ESM_PROPULSION,
        ),
        Reference(
            "orion_nrho_delta_v",
            "Orion NRHO insertion and departure delta-v",
            1_000.0,
            "m/s",
            *NRHO_PAPER,
            note="NRHO LOI + TEI, as built",
        ),
        Reference(
            "orion_capability",
            "Orion delta-v capability (no payload)",
            (1_000.0, None),
            "m/s",
            *NRHO_PAPER,
            note="must cover NRHO LOI + TEI (1,000 m/s)",
        ),
        Reference("nrho_llo", "NRHO to LLO delta-v", 750.0, "m/s", *NRHO_PAPER),
        Reference("descent", "LLO to surface delta-v", 2_050.0, "m/s", *NRHO_PAPER),
        Reference("ascent", "Surface to LLO delta-v", 1_860.0, "m/s", *NRHO_PAPER),
        Reference("llo_nrho", "LLO to NRHO delta-v", 750.0, "m/s", *NRHO_PAPER),
        Reference(
            "hls_tankers",
            "Tanker flights per HLS landing",
            (8.0, 14.0),
            "flights",
            "GAO B-419783 (2021): 14 tankers; SpaceX statements: ~8 to 10",
            "https://www.gao.gov/assets/870/864236.pdf",
            note="published estimates vary with tanker capacity and boiloff",
        ),
        Reference(
            "crew_cislunar",
            "Crew per mission to cislunar space",
            (None, 4.0),
            "crew",
            *ADD,
            note="LD-06-L: up to four crew members",
        ),
        Reference(
            "surface_stay",
            "Initial crewed surface stay",
            6.0,
            "days",
            *ADD,
            note="LD-07-L: initial missions of approximately 6 Earth days",
        ),
        Reference(
            "water_rate",
            "Crew water (drink, rehydration, hygiene, flush)",
            3.99,
            "kg/crew-day",
            *LOGISTICS,
        ),
        Reference("food_rate", "Crew packaged food", 2.36, "kg/crew-day", *LOGISTICS),
        Reference(
            "oxygen_rate", "Crew metabolic oxygen", 0.89, "kg/crew-day", *LOGISTICS
        ),
        Reference(
            "site_illumination",
            "Connecting ridge illumination",
            (0.0, 0.90),
            "fraction",
            "LROC, Traversing the Shackleton-de Gerlache Ridge",
            "https://www.lroc.asu.edu/images/1247",
            note="portions illuminated up to 90% of the time",
        ),
        Reference("fsp_power", "Fission Surface Power output", 40.0, "kWe", *FSP),
        Reference(
            "fsp_mass", "Fission Surface Power mass", (None, 6_000.0), "kg", *FSP
        ),
        Reference(
            "ltv_crew", "LTV crew capacity", 2.0, "crew", *ADD, note="two suited crew"
        ),
        Reference(
            "ltv_walk_back",
            "Suited walk-back distance",
            10.0,
            "km",
            "NASA NTRS 20250011301 (suited 10 km walkback study)",
            "https://ntrs.nasa.gov/citations/20250011301",
        ),
        Reference(
            "pressurized_rover_crew", "Pressurized rover crew", 2.0, "crew", *ADD
        ),
        Reference(
            "pressurized_rover_duration",
            "Pressurized rover mission duration",
            28.0,
            "days",
            *ADD,
        ),
        Reference(
            "sls_orion_launch_cost",
            "SLS/Orion production and operations cost per launch",
            4_100.0,
            "$M",
            *OIG,
            note="SLS $2.2B, Orion $1.0B, ESM $0.3B, ground systems $568M per year",
        ),
        Reference(
            "hls_artemis_iii_cost",
            "SpaceX HLS contract (development and Artemis III)",
            2_890.0,
            "$M",
            "NASA, Artemis III HLS award (2021)",
            "https://www.nasa.gov/news-release/as-artemis-moves-forward-nasa-picks-"
            "spacex-to-land-next-americans-on-moon/",
        ),
        Reference(
            "hls_artemis_v_cost",
            "Blue Origin HLS contract (Artemis V)",
            3_400.0,
            "$M",
            "NASA, second Artemis lunar lander award (2023)",
            "https://www.nasa.gov/news-release/nasa-selects-blue-origin-as-second-"
            "artemis-lunar-lander-provider/",
            note="the campaign models every lander as Starship-class",
        ),
        Reference(
            "ppe_cost",
            "Power and Propulsion Element contract",
            375.0,
            "$M",
            "NASA, PPE award (2019)",
            "https://www.nasa.gov/news-release/nasa-awards-artemis-contract-for-"
            "lunar-gateway-power-propulsion",
        ),
        Reference(
            "halo_cost",
            "HALO contract",
            935.0,
            "$M",
            "NASA, HALO contract (2021)",
            "https://www.nasa.gov/news-release/nasa-northrop-grumman-finalize-moon-"
            "outpost-living-quarters-contract",
        ),
        Reference(
            "gateway_launch_cost",
            "Falcon Heavy launch of PPE and HALO",
            331.8,
            "$M",
            "NASA, Gateway launch award (2021)",
            "https://www.nasa.gov/press-release/nasa-awards-contract-to-launch-"
            "initial-elements-for-lunar-outpost",
        ),
        Reference(
            "gateway_life",
            "Gateway design life",
            (15.0, None),
            "years",
            "NASA, About Gateway",
            "https://www.nasa.gov/reference/gateway-about/",
            note="minimum 15-year lifespan",
        ),
        Reference(
            "fsp_life", "Fission Surface Power design life", (10.0, None), "years", *FSP
        ),
        Reference(
            "gateway_logistics",
            "Logistics deliveries per crewed Gateway mission",
            (1.0, None),
            "deliveries",
            *ADD,
            note="at least one logistics delivery for each Gateway mission of 30 days",
        ),
        Reference(
            "dragon_xl_cargo",
            "Dragon XL cargo to Gateway",
            (5_000.0, None),
            "kg",
            "NASA Gateway Logistics Services award (Spaceflight Now, 2020)",
            "https://www.spaceflightnow.com/2020/03/27/nasa-picks-spacex-to-deliver-"
            "cargo-to-gateway-station-in-lunar-orbit",
            note="more than 5 t of pressurized and unpressurized cargo",
        ),
        Reference(
            "dragon_xl_berthing",
            "Dragon XL berthing at Gateway",
            (6.0, 12.0),
            "months",
            "NASA Gateway Logistics Services award (Spaceflight Now, 2020)",
            "https://www.spaceflightnow.com/2020/03/27/nasa-picks-spacex-to-deliver-"
            "cargo-to-gateway-station-in-lunar-orbit",
        ),
        Reference(
            "cargo_transfer",
            "Low-energy cargo transfer to NRHO",
            120.0,
            "days",
            *NRHO_PAPER,
        ),
        Reference(
            "isru_production",
            "ISRU pilot plant oxygen production",
            1_000.0,
            "kg/yr",
            *PILOT_PLANT,
            note="from 1,125 kg of water extracted from icy regolith",
        ),
        Reference(
            "isru_mass",
            "ISRU pilot plant mass",
            325.0 + 840.0,
            "kg",
            *PILOT_PLANT,
            note="PSR plant (325 kg) and ridge plant (840 kg)",
        ),
        Reference(
            "isru_pilot_energy",
            "ISRU pilot plant energy per kg of oxygen",
            (None, round((2.4 + 4.3) * 225 * 24 / 1_000.0, 1)),
            "kWh/kg",
            *PILOT_PLANT,
            note="upper bound: PSR (2.4 kW) and ridge (4.3 kW) plant power "
            "for 225 days of operation per year",
        ),
        Reference(
            "isru_o2_h2_ratio",
            "Water electrolysis oxygen-to-hydrogen mass ratio",
            round(2 * OXYGEN / (4 * HYDROGEN), 3),
            "kg/kg",
            "IUPAC standard atomic weights (stoichiometry)",
            "https://iupac.qmul.ac.uk/AtWt/",
        ),
        Reference(
            "isru_minimum_energy",
            "Minimum energy of water electrolysis",
            (round(2 * WATER_FORMATION_ENTHALPY / (2 * OXYGEN) / 3.6, 2), None),
            "kWh/kg O2",
            "NIST Chemistry WebBook (water, enthalpy of formation)",
            "https://webbook.nist.gov/cgi/cbook.cgi?ID=C7732185",
            note="higher heating value of 285.83 kJ/mol",
        ),
        Reference(
            "sls_cadence",
            "Interval between crewed SLS launches",
            365.0,
            "days",
            *ADD,
            note="annual cadence of crewed missions",
        ),
    ]
}


def _template(scenario: s.Scenario, name: str):
    return next(t for t in scenario.element_templates if t.name == name)


def _edge(scenario: s.Scenario, name: str):
    return next(e for e in scenario.network.edges if e.name == name)


def _delta_v(edge, burns: Optional[slice] = None) -> float:
    return sum(b.delta_v for b in edge.burns[burns or slice(None)])


def validate(params: Optional[CampaignParameters] = None) -> List[ValidationResult]:
    """
    Validates the reference Artemis campaign.

    Args:
        params (:obj:`CampaignParameters`): The campaign parameters.

    Returns:
        [:obj:`ValidationResult`]: The results.
    """
    # pylint: disable=too-many-locals
    params = params or CampaignParameters()
    scenario = build_scenario(params)
    ref = REFERENCES
    results = []

    def add(key, model, kind=CheckKind.INPUT, tolerance=0.0, note=""):
        results.append(compare(ref[key], model, kind, tolerance, note))

    # launch vehicles (simulated with the stage models)
    block_1 = max_payload(
        lambda m: CampaignBuilder(params).launch_capability(False, m), 80_000
    )
    block_1b = max_payload(
        lambda m: CampaignBuilder(params).launch_capability(True, m), 80_000
    )
    add(
        "sls_block_1_tli",
        block_1,
        CheckKind.VALIDATED,
        0.10,
        "simulated: SRBs, core, and iCPS through the 9,500 m/s ascent and TLI",
    )
    add(
        "sls_block_1b_tli",
        block_1b,
        CheckKind.CALIBRATED,
        0.01,
        "the equivalent Block 1B ascent delta-v is calibrated to this value",
    )

    # Orion
    sm = _template(scenario, "Orion SM")
    cm = _template(scenario, "Orion CM")
    system = sm.propulsion_systems[0]
    propellant = system.fuel_tank.max_amount
    add("esm_propellant", propellant)
    dry = cm.mass + sm.mass
    add(
        "orion_capability",
        system.isp * G0 * math.log((dry + propellant) / dry),
        CheckKind.VALIDATED,
        note="rocket equation with the CM and ESM masses",
    )
    outbound = _edge(scenario, "LEO-NRHO")
    inbound = _edge(scenario, "NRHO-PAC")
    add(
        "orion_nrho_delta_v",
        _delta_v(outbound, slice(1, None)) + _delta_v(inbound),
        CheckKind.INPUT,
        0.05,
        "Orion burns after TLI, including trajectory corrections",
    )

    # lunar transfers
    add("nrho_llo", _delta_v(_edge(scenario, "NRHO-LLO")))
    add("descent", _delta_v(_edge(scenario, "LLO-LSP")))
    add("ascent", _delta_v(_edge(scenario, "LSP-LLO")))
    add("llo_nrho", _delta_v(_edge(scenario, "LLO-NRHO")))

    # propellant aggregation
    add(
        "hls_tankers",
        params.tankers(),
        CheckKind.VALIDATED,
        note="sized for boiloff and transfer losses (tanker campaign sizing)",
    )

    # missions
    crew_ids = {
        i.id for i in scenario.instantiated_elements if isinstance(i, s.InstHumanAgent)
    }
    add(
        "crew_cislunar",
        max(
            sum(
                1
                for e in m.events
                if isinstance(e, s.CreateElements)
                for i in e.elements
                if i in crew_ids
            )
            for m in scenario.mission_list
        ),
        note="largest crew created in a mission",
    )
    add("surface_stay", params.surface_days, note="surface exploration duration")

    # crew consumables
    model = next(d for d in scenario.demand_models if d.type == "Crew Consumables")
    add("water_rate", model.water_rate * (1 - model.water_recovery_rate))
    add(
        "food_rate",
        model.ambient_food_rate + model.rf_food_rate + model.food_support_rate,
    )
    add("oxygen_rate", model.oxygen_rate)

    # surface
    site = next(n for n in scenario.network.nodes if n.name == "LSP")
    add("site_illumination", site.illumination, CheckKind.VALIDATED)
    fsp = _template(scenario, "FSP")
    add("fsp_power", max(st.power_generation or 0 for st in fsp.states))
    add("fsp_mass", fsp.mass)
    ltv = _template(scenario, "LTV")
    add("ltv_crew", ltv.max_crew)
    add("ltv_walk_back", ltv.walk_back_distance)
    rover = _template(scenario, "Pressurized Rover")
    add("pressurized_rover_crew", rover.max_crew)
    add("pressurized_rover_duration", rover.max_crewed_duration / 24)

    # cost (simulated) and design lives
    simulator = FullSimulator(scenario)
    simulator.simulate()
    costs = CostAnalysis.create(simulator, scenario.start_date)
    add(
        "sls_orion_launch_cost",
        costs.by_mission["Artemis II"],
        tolerance=0.02,
        note="simulated cost of Artemis II (SLS, Orion, and ground systems)",
    )
    add("hls_artemis_iii_cost", costs.by_mission["Artemis III Propellant Aggregation"])
    add("hls_artemis_v_cost", costs.by_mission["Artemis V Propellant Aggregation"])
    by_item = {i.item: i.amount for i in costs.items}
    add("ppe_cost", by_item["Gateway | PPE"])
    add("halo_cost", by_item["Gateway | HALO"])
    add("gateway_launch_cost", by_item["KSC-NRHO (Falcon Heavy + SEP)"])
    add("gateway_life", _template(scenario, "HALO").design_life)
    add("fsp_life", fsp.design_life)
    add("sls_cadence", _edge(scenario, "KSC-LEO (SLS)").min_departure_interval)

    # Gateway logistics: deliveries berthed at Gateway during each crewed
    # Gateway mission (simulated)
    berthed = []
    for mission in ("Artemis IV", "Artemis V"):
        sim_mission = next(m for m in simulator.state.missions if m.name == mission)
        arrival = sim_mission.start_time + 6  # Orion arrives in NRHO
        count = 0
        for snapshot in simulator.network_history:
            if snapshot.time >= arrival:
                count = sum(
                    1
                    for element in snapshot.get_elements(
                        next(n.id for n in scenario.network.nodes if n.name == "NRHO")
                    )
                    if element.name.endswith("Dragon XL")
                )
                break
        berthed.append(count)
    add(
        "gateway_logistics",
        min(berthed),
        CheckKind.VALIDATED,
        note="Dragon XL berthed at Gateway on arrival of the crew (simulated)",
    )
    dragon = _template(scenario, "Dragon XL")
    add("dragon_xl_cargo", dragon.max_cargo_mass)
    disposal = next(
        e
        for m in scenario.mission_list
        if m.name == "Gateway Logistics 1"
        for e in m.events
        if e.name.endswith("Disposal")
    )
    transfer = _edge(scenario, "KSC-NRHO (Falcon Heavy, Logistics)")
    berth_days = (disposal.mission_time - transfer.duration).total_seconds() / 86400
    add("dragon_xl_berthing", berth_days / 30.44, tolerance=0.01)
    add("cargo_transfer", transfer.duration.total_seconds() / 86400)

    # ISRU pilot plant (simulated on fission surface power)
    if params.isru_pilot_plant:
        (plant,) = ISRUAnalysis.create(simulator).processes
        oxygen = plant.total_outputs["LOX"]
        add(
            "isru_production",
            oxygen / plant.duration * 365,
            CheckKind.CALIBRATED,
            0.01,
            f"simulated: {number(oxygen)} kg in {number(plant.duration)} days, "
            "not limited by power or storage",
        )
        add("isru_mass", _template(scenario, "ISRU Pilot Plant").mass)
        add(
            "isru_pilot_energy",
            plant.specific_energy,
            CheckKind.CALIBRATED,
            0.01,
            "simulated energy consumed per kg of oxygen",
        )
        add(
            "isru_o2_h2_ratio",
            oxygen / plant.total_outputs["LH2"],
            CheckKind.VALIDATED,
            0.01,
            "simulated: the published 1,000 / 125 kg split is within 1% of "
            "stoichiometric",
        )
        add(
            "isru_minimum_energy",
            plant.specific_energy,
            CheckKind.VALIDATED,
            note="simulated energy per kg of oxygen exceeds the minimum",
        )
    return results


def compare_default_consumables() -> List[ValidationResult]:
    """
    Compares the default rates of the crew consumables demand model (from the
    reference implementation) with NASA planning values.
    """
    model = s.CrewConsumablesDemandModel(name="Default")
    ref = REFERENCES
    return [
        compare(ref["water_rate"], model.water_rate, CheckKind.VALIDATED, 0.10),
        compare(
            ref["food_rate"],
            model.ambient_food_rate + model.rf_food_rate + model.food_support_rate,
            CheckKind.VALIDATED,
            0.10,
        ),
        compare(ref["oxygen_rate"], model.oxygen_rate, CheckKind.VALIDATED, 0.10),
    ]


if __name__ == "__main__":
    print("## Reference Artemis campaign\n")
    print(report_markdown(validate()))
    print("\n## Default crew consumables rates\n")
    print(report_markdown(compare_default_consumables()))
