from spacenet.schemas import *

from db_loader import load_db

db = load_db("quick_start_1.xlsx")

##########################################
# NODES
##########################################
def get_node(name):
    return next(filter(lambda o: o.name == name, db.nodes))

##########################################
# EDGES
##########################################
def get_edge(name):
    return next(filter(lambda o: o.name == name, db.edges))

##########################################
# RESOURCES
##########################################
def get_resource(name):
    return next(filter(lambda o: o.name == name, db.resources))

##########################################
# INSTANTIATED ELEMENTS
##########################################
def instantiate_element(cls, template_name, suffix=""):
    return cls(
        template_id=next(filter(lambda o: o.name == template_name, db.elements)).id,
        name="Lunar | " + next(filter(lambda o: o.name == template_name, db.elements)).name + suffix,
    )

ares_i_first_stage_1 = instantiate_element(InstPropulsiveVehicle, "Ares I First Stage")
ares_i_upper_stage_1 = instantiate_element(InstPropulsiveVehicle, "Ares I Upper Stage")
orion_cm_1 = instantiate_element(InstPropulsiveVehicle, "Orion CM")
orion_sm_1 = instantiate_element(InstPropulsiveVehicle, "Orion SM")
orion_las_1 = instantiate_element(InstPropulsiveVehicle, "Orion LAS")
crew_member_1_1 = instantiate_element(InstHumanAgent, "Crew Member", " A")
crew_member_1_2 = instantiate_element(InstHumanAgent, "Crew Member", " B")
crew_member_1_3 = instantiate_element(InstHumanAgent, "Crew Member", " C")
crew_member_1_4 = instantiate_element(InstHumanAgent, "Crew Member", " D")
altair_am_1 = instantiate_element(InstPropulsiveVehicle, "Altair AM")
altair_dm_1 = instantiate_element(InstPropulsiveVehicle, "Altair DM")
ares_v_core_1 = instantiate_element(InstPropulsiveVehicle, "Ares V Core")
ares_v_srbs_1 = instantiate_element(InstPropulsiveVehicle, "Ares V SRBs")
eds_1 = instantiate_element(InstElementCarrier, "EDS")
cargo_1 = instantiate_element(InstElement, "Notional Cargo")
samples_1 = instantiate_element(InstElement, "Lunar Surface Samples")

##########################################
# MISSIONS
##########################################
lunar_sortie = Mission(
    name="Lunar Sortie",
    startDate="2019-07-01T04:00:00.000Z",
    origin=get_node("KSC").id,
    destination=get_node("LSP").id,
    return_origin=get_node("LSP").id,
    return_destination=get_node("PAC").id,
    demand_models=[],
    events=[
        CreateElements(
            name="Lunar | Create Elements",
            missionTime="PT0S",
            priority=1,
            location=get_node("KSC").id,
            container=get_node("KSC").id,
            elements=[
                ares_i_first_stage_1.id,
                ares_i_upper_stage_1.id,
                orion_cm_1.id,
                orion_sm_1.id,
                orion_las_1.id,
            ],
        ),
        CreateElements(
            name="Lunar | Create Elements",
            missionTime="PT0S",
            priority=2,
            location=get_node("KSC").id,
            container=orion_cm_1.id,
            elements=[
                crew_member_1_1.id,
                crew_member_1_2.id,
                crew_member_1_3.id,
                crew_member_1_4.id,
            ],
        ),
        SpaceTransport(
            name="Lunar | Space Transport",
            missionTime="PT0S",
            priority=3,
            location=get_node("KSC").id,
            edge=get_edge("KSC-LEO").id,
            elements=[
                ares_i_first_stage_1.id,
                ares_i_upper_stage_1.id,
                orion_cm_1.id,
                orion_sm_1.id,
                orion_las_1.id,
            ],
            burn_stage_sequence=[
                BurnStageSequence(
                    burn=get_edge("KSC-LEO").burns[0].id,
                    actions=[
                        BurnStageItem(type="Burn", element=ares_i_first_stage_1.id),
                        BurnStageItem(type="Stage", element=ares_i_first_stage_1.id),
                        BurnStageItem(type="Stage", element=orion_las_1.id),
                        BurnStageItem(type="Burn", element=ares_i_upper_stage_1.id),
                        BurnStageItem(type="Stage", element=ares_i_upper_stage_1.id),
                    ],
                )
            ],
        ),
        CreateElements(
            name="Lunar | Create Elements",
            missionTime="P1D",
            priority=1,
            location=get_node("KSC").id,
            container=get_node("KSC").id,
            elements=[
                altair_am_1.id,
                altair_dm_1.id,
                ares_v_core_1.id,
                ares_v_srbs_1.id,
                eds_1.id,
            ],
        ),
        CreateElements(
            name="Lunar | Create Elements",
            missionTime="P1D",
            priority=2,
            location=get_node("KSC").id,
            container=altair_dm_1.id,
            elements=[cargo_1.id,],
        ),
        SpaceTransport(
            name="Lunar | Space Transport",
            missionTime="P1D",
            priority=3,
            location=get_node("KSC").id,
            edge=get_edge("KSC-LEO").id,
            elements=[
                altair_am_1.id,
                altair_dm_1.id,
                ares_v_core_1.id,
                ares_v_srbs_1.id,
                eds_1.id,
            ],
            burn_stage_sequence=[
                BurnStageSequence(
                    burn=get_edge("KSC-LEO").burns[0].id,
                    actions=[
                        BurnStageItem(type="Burn", element=ares_v_srbs_1.id),
                        BurnStageItem(type="Stage", element=ares_v_srbs_1.id),
                        BurnStageItem(type="Burn", element=ares_v_core_1.id),
                        BurnStageItem(type="Stage", element=ares_v_core_1.id),
                        BurnStageItem(type="Burn", element=eds_1.id),
                    ],
                )
            ],
        ),
        SpaceTransport(
            name="Lunar | Space Transport",
            missionTime="P2D",
            priority=1,
            location=get_node("LEO").id,
            edge=get_edge("LEO-LLPO").id,
            elements=[
                altair_am_1.id,
                altair_dm_1.id,
                eds_1.id,
                orion_cm_1.id,
                orion_sm_1.id,
            ],
            burn_stage_sequence=[
                BurnStageSequence(
                    burn=get_edge("LEO-LLPO").burns[0].id,
                    actions=[
                        BurnStageItem(type="Burn", element=eds_1.id),
                        BurnStageItem(type="Stage", element=eds_1.id),
                    ],
                ),
                BurnStageSequence(
                    burn=get_edge("LEO-LLPO").burns[1].id,
                    actions=[BurnStageItem(type="Burn", element=altair_dm_1.id),],
                ),
                BurnStageSequence(
                    burn=get_edge("LEO-LLPO").burns[2].id,
                    actions=[BurnStageItem(type="Burn", element=altair_dm_1.id),],
                ),
                BurnStageSequence(
                    burn=get_edge("LEO-LLPO").burns[3].id,
                    actions=[BurnStageItem(type="Burn", element=altair_dm_1.id),],
                ),
            ],
        ),
        MoveElements(
            name="Lunar | Move Elements",
            missionTime="P6D",
            priority=1,
            location=get_node("LLPO").id,
            container=altair_am_1.id,
            elements=[
                crew_member_1_1.id,
                crew_member_1_2.id,
                crew_member_1_3.id,
                crew_member_1_4.id,
            ],
        ),
        SpaceTransport(
            name="Lunar | Space Transport",
            missionTime="P7D",
            priority=1,
            location=get_node("LLPO").id,
            edge=get_edge("LLPO-LSP").id,
            elements=[altair_am_1.id, altair_dm_1.id,],
            burn_stage_sequence=[
                BurnStageSequence(
                    burn=get_edge("LLPO-LSP").burns[0].id,
                    actions=[BurnStageItem(type="Burn", element=altair_dm_1.id),],
                ),
                BurnStageSequence(
                    burn=get_edge("LLPO-LSP").burns[1].id,
                    actions=[BurnStageItem(type="Burn", element=altair_dm_1.id),],
                ),
            ],
        ),
        CrewedExploration(
            name="Lunar | Crewed Exploration",
            missionTime="P7DT12H",
            priority=1,
            location=get_node("LSP").id,
            vehicle=altair_am_1.id,
            duration="P7D",
            eva_per_week=5.0,
            eva_duration="PT8H",
            element_states=[
                ElementState(element=crew_member_1_1.id, state_index=-1),
                ElementState(element=crew_member_1_2.id, state_index=-1),
            ],
            additional_demands=[],
        ),
        CreateElements(
            name="Lunar | Create Elements",
            missionTime="P14DT12H",
            priority=1,
            location=get_node("LSP").id,
            container=altair_am_1.id,
            elements=[samples_1.id,],
        ),
        SpaceTransport(
            name="Lunar | Space Transport",
            missionTime="P14DT12H",
            priority=2,
            location=get_node("LSP").id,
            edge=get_edge("LSP-LLPO").id,
            elements=[altair_am_1.id],
            burn_stage_sequence=[
                BurnStageSequence(
                    burn=get_edge("LSP-LLPO").burns[0].id,
                    actions=[BurnStageItem(type="Burn", element=altair_am_1.id),],
                ),
                BurnStageSequence(
                    burn=get_edge("LSP-LLPO").burns[1].id,
                    actions=[BurnStageItem(type="Burn", element=altair_am_1.id),],
                ),
            ],
        ),
        MoveElements(
            name="Lunar | Move Elements",
            missionTime="P15D",
            priority=1,
            location=get_node("LLPO").id,
            container=orion_cm_1.id,
            elements=[
                crew_member_1_1.id,
                crew_member_1_2.id,
                crew_member_1_3.id,
                crew_member_1_4.id,
                samples_1.id,
            ],
        ),
        SpaceTransport(
            name="Lunar | Space Transport",
            missionTime="P15D",
            priority=2,
            location=get_node("LLPO").id,
            edge=get_edge("LLPO-PAC").id,
            elements=[orion_cm_1.id, orion_sm_1.id],
            burn_stage_sequence=[
                BurnStageSequence(
                    burn=get_edge("LLPO-PAC").burns[0].id,
                    actions=[BurnStageItem(type="Burn", element=orion_sm_1.id),],
                ),
                BurnStageSequence(
                    burn=get_edge("LLPO-PAC").burns[1].id,
                    actions=[BurnStageItem(type="Burn", element=orion_sm_1.id),],
                ),
                BurnStageSequence(
                    burn=get_edge("LLPO-PAC").burns[2].id,
                    actions=[BurnStageItem(type="Burn", element=orion_sm_1.id),],
                ),
                BurnStageSequence(
                    burn=get_edge("LLPO-PAC").burns[3].id,
                    actions=[BurnStageItem(type="Burn", element=orion_sm_1.id),],
                ),
                BurnStageSequence(
                    burn=get_edge("LLPO-PAC").burns[4].id,
                    actions=[BurnStageItem(type="Burn", element=orion_sm_1.id),],
                ),
                BurnStageSequence(
                    burn=get_edge("LLPO-PAC").burns[5].id,
                    actions=[
                        BurnStageItem(type="Stage", element=orion_sm_1.id),
                        BurnStageItem(type="Burn", element=orion_cm_1.id),
                    ],
                ),
            ],
        ),
    ],
)

##########################################
# SCENARIO
##########################################
scenario = Scenario(
    name="Quick Start Scenario 1",
    description="A sample scenario analyzing the transportation feasibility of a lunar mission.",
    created_by="SpaceNet User",
    start_date="2019-07-02T01:05:16.051Z",
    scenario_type="Lunar",
    network=Network(
        nodes=db.nodes,
        edges=db.edges,
    ),
    mission_list=[lunar_sortie],
    resource_list=db.resources,
    element_templates=db.elements,
    instantiated_elements=[
        altair_am_1,
        altair_dm_1,
        ares_i_first_stage_1,
        ares_i_upper_stage_1,
        ares_v_core_1,
        ares_v_srbs_1,
        crew_member_1_1,
        crew_member_1_2,
        crew_member_1_3,
        crew_member_1_4,
        eds_1,
        samples_1,
        cargo_1,
        orion_cm_1,
        orion_las_1,
        orion_sm_1,
    ],
    demand_models=db.demand_models,
    configuration=Configuration(
        **{
            "timePrecision": 0.05,
            "demandPrecision": 0.01,
            "massPrecision": 0.01,
            "volumePrecision": 1.0e-6,
            "volumeConstrained": False,
            "environmentConstrained": True,
            "itemDiscretization": "None",
            "itemAggregation": 0.0,
            "scavangeSpares": False,
            "detailedEva": True,
            "detailedExploration": True,
            "genericPackingFactorGas": 1.0,
            "genericPackingFactorLiquid": 0.5,
            "genericPackingFactorPressurized": 0.2,
            "genericPackingFactorUnpressurized": 0.6,
            "smallGasTankMass": 10.8,
            "smallGasTankVolume": 0.275,
            "smallGasTankMaxMass": 10.0,
            "smallGasTankMaxVolume": 0.275,
            "largeGasTankMass": 108.0,
            "largeGasTankVolume": 2.75,
            "largeGasTankMaxMass": 100.0,
            "largeGasTankMaxVolume": 2.75,
            "smallLiquidTankMass": 11.4567,
            "smallLiquidTankVolume": 0.0249,
            "smallLiquidTankMaxMass": 24.9333,
            "smallLiquidTankMaxVolume": 0.0249,
            "largeLiquidTankMass": 34.37,
            "largeLiquidTankVolume": 0.0748,
            "largeLiquidTankMaxMass": 74.8,
            "largeLiquidTankMaxVolume": 0.0748,
            "cargoTransferBagMass": 0.83,
            "cargoTransferBagVolume": 0.053,
            "cargoTransferBagMaxMass": 26.8,
            "cargoTransferBagMaxVolume": 0.049,
        }
    ),
)

print(scenario.json(exclude_unset=True, indent=2))
