from datetime import datetime, timedelta, timezone

from spacenet.io import load_db
from spacenet.schemas import *

with open("quick_start_1.xlsx", "rb") as db_file:
    db = load_db(db_file)

##########################################
# INSTANTIATED ELEMENTS
##########################################

ares_i_first_stage_1 = db.instantiate_element(
    InstPropulsiveVehicle, "Ares I First Stage", "Lunar"
)
ares_i_upper_stage_1 = db.instantiate_element(
    InstPropulsiveVehicle, "Ares I Upper Stage", "Lunar"
)
orion_cm_1 = db.instantiate_element(InstPropulsiveVehicle, "Orion CM", "Lunar")
orion_sm_1 = db.instantiate_element(InstPropulsiveVehicle, "Orion SM", "Lunar")
orion_las_1 = db.instantiate_element(InstElementCarrier, "Orion LAS", "Lunar")
crew_member_1_1 = db.instantiate_element(InstHumanAgent, "Crew Member", "Lunar", " A")
crew_member_1_2 = db.instantiate_element(InstHumanAgent, "Crew Member", "Lunar", " B")
crew_member_1_3 = db.instantiate_element(InstHumanAgent, "Crew Member", "Lunar", " C")
crew_member_1_4 = db.instantiate_element(InstHumanAgent, "Crew Member", "Lunar", " D")
altair_am_1 = db.instantiate_element(InstPropulsiveVehicle, "Altair AM", "Lunar")
altair_dm_1 = db.instantiate_element(InstPropulsiveVehicle, "Altair DM", "Lunar")
ares_v_core_1 = db.instantiate_element(InstPropulsiveVehicle, "Ares V Core", "Lunar")
ares_v_srbs_1 = db.instantiate_element(InstPropulsiveVehicle, "Ares V SRBs", "Lunar")
eds_1 = db.instantiate_element(InstPropulsiveVehicle, "EDS", "Lunar")
cargo_1 = db.instantiate_element(InstElement, "Notional Cargo", "Lunar")
samples_1 = db.instantiate_element(InstElement, "Lunar Surface Samples", "Lunar")

##########################################
# MISSIONS
##########################################
lunar_sortie = Mission(
    name="Lunar Sortie",
    startDate=datetime(2019, 7, 1, 4, tzinfo=timezone.utc),
    origin=db.get_node("KSC").id,
    destination=db.get_node("LSP").id,
    return_origin=db.get_node("LSP").id,
    return_destination=db.get_node("PAC").id,
    demand_models=[],
    events=[
        CreateElements(
            name="Lunar | Create Elements",
            mission_time=timedelta(0),
            priority=1,
            location=db.get_node("KSC").id,
            container=db.get_node("KSC").id,
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
            mission_time=timedelta(0),
            priority=2,
            location=db.get_node("KSC").id,
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
            mission_time=timedelta(0),
            priority=3,
            location=db.get_node("KSC").id,
            edge=db.get_edge("KSC-LEO").id,
            elements=[
                ares_i_first_stage_1.id,
                ares_i_upper_stage_1.id,
                orion_cm_1.id,
                orion_sm_1.id,
                orion_las_1.id,
            ],
            burn_stage_sequence=[
                BurnStageSequence(
                    burn=db.get_edge("KSC-LEO").burns[0].id,
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
            mission_time=timedelta(days=1),
            priority=1,
            location=db.get_node("KSC").id,
            container=db.get_node("KSC").id,
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
            mission_time=timedelta(days=1),
            priority=2,
            location=db.get_node("KSC").id,
            container=altair_dm_1.id,
            elements=[
                cargo_1.id,
            ],
        ),
        SpaceTransport(
            name="Lunar | Space Transport",
            mission_time=timedelta(days=1),
            priority=3,
            location=db.get_node("KSC").id,
            edge=db.get_edge("KSC-LEO").id,
            elements=[
                altair_am_1.id,
                altair_dm_1.id,
                ares_v_core_1.id,
                ares_v_srbs_1.id,
                eds_1.id,
            ],
            burn_stage_sequence=[
                BurnStageSequence(
                    burn=db.get_edge("KSC-LEO").burns[0].id,
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
            mission_time=timedelta(days=2),
            priority=1,
            location=db.get_node("LEO").id,
            edge=db.get_edge("LEO-LLPO").id,
            elements=[
                altair_am_1.id,
                altair_dm_1.id,
                eds_1.id,
                orion_cm_1.id,
                orion_sm_1.id,
            ],
            burn_stage_sequence=[
                BurnStageSequence(
                    burn=db.get_edge("LEO-LLPO").burns[0].id,
                    actions=[
                        BurnStageItem(type="Burn", element=eds_1.id),
                        BurnStageItem(type="Stage", element=eds_1.id),
                    ],
                ),
                BurnStageSequence(
                    burn=db.get_edge("LEO-LLPO").burns[1].id,
                    actions=[
                        BurnStageItem(type="Burn", element=altair_dm_1.id),
                    ],
                ),
                BurnStageSequence(
                    burn=db.get_edge("LEO-LLPO").burns[2].id,
                    actions=[
                        BurnStageItem(type="Burn", element=altair_dm_1.id),
                    ],
                ),
                BurnStageSequence(
                    burn=db.get_edge("LEO-LLPO").burns[3].id,
                    actions=[
                        BurnStageItem(type="Burn", element=altair_dm_1.id),
                    ],
                ),
            ],
        ),
        MoveElements(
            name="Lunar | Move Elements",
            mission_time=timedelta(days=6),
            priority=1,
            location=db.get_node("LLPO").id,
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
            mission_time=timedelta(days=7),
            priority=1,
            location=db.get_node("LLPO").id,
            edge=db.get_edge("LLPO-LSP").id,
            elements=[
                altair_am_1.id,
                altair_dm_1.id,
            ],
            burn_stage_sequence=[
                BurnStageSequence(
                    burn=db.get_edge("LLPO-LSP").burns[0].id,
                    actions=[
                        BurnStageItem(type="Burn", element=altair_dm_1.id),
                    ],
                ),
                BurnStageSequence(
                    burn=db.get_edge("LLPO-LSP").burns[1].id,
                    actions=[
                        BurnStageItem(type="Burn", element=altair_dm_1.id),
                    ],
                ),
            ],
        ),
        CrewedExploration(
            name="Lunar | Crewed Exploration",
            mission_time=timedelta(days=7, hours=12),
            priority=1,
            location=db.get_node("LSP").id,
            vehicle=altair_am_1.id,
            duration=timedelta(days=7),
            eva_per_week=5.0,
            eva_duration=timedelta(hours=8),
            element_states=[
                ElementState(element=crew_member_1_1.id, state_index=-1),
                ElementState(element=crew_member_1_2.id, state_index=-1),
            ],
            additional_demands=[],
        ),
        CreateElements(
            name="Lunar | Create Elements",
            mission_time=timedelta(days=14, hours=12),
            priority=1,
            location=db.get_node("LSP").id,
            container=altair_am_1.id,
            elements=[
                samples_1.id,
            ],
        ),
        SpaceTransport(
            name="Lunar | Space Transport",
            mission_time=timedelta(days=14, hours=12),
            priority=2,
            location=db.get_node("LSP").id,
            edge=db.get_edge("LSP-LLPO").id,
            elements=[altair_am_1.id],
            burn_stage_sequence=[
                BurnStageSequence(
                    burn=db.get_edge("LSP-LLPO").burns[0].id,
                    actions=[
                        BurnStageItem(type="Burn", element=altair_am_1.id),
                    ],
                ),
                BurnStageSequence(
                    burn=db.get_edge("LSP-LLPO").burns[1].id,
                    actions=[
                        BurnStageItem(type="Burn", element=altair_am_1.id),
                    ],
                ),
            ],
        ),
        MoveElements(
            name="Lunar | Move Elements",
            mission_time=timedelta(days=15),
            priority=1,
            location=db.get_node("LLPO").id,
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
            mission_time=timedelta(days=15),
            priority=2,
            location=db.get_node("LLPO").id,
            edge=db.get_edge("LLPO-PAC").id,
            elements=[orion_cm_1.id, orion_sm_1.id],
            burn_stage_sequence=[
                BurnStageSequence(
                    burn=db.get_edge("LLPO-PAC").burns[0].id,
                    actions=[
                        BurnStageItem(type="Burn", element=orion_sm_1.id),
                    ],
                ),
                BurnStageSequence(
                    burn=db.get_edge("LLPO-PAC").burns[1].id,
                    actions=[
                        BurnStageItem(type="Burn", element=orion_sm_1.id),
                    ],
                ),
                BurnStageSequence(
                    burn=db.get_edge("LLPO-PAC").burns[2].id,
                    actions=[
                        BurnStageItem(type="Burn", element=orion_sm_1.id),
                    ],
                ),
                BurnStageSequence(
                    burn=db.get_edge("LLPO-PAC").burns[3].id,
                    actions=[
                        BurnStageItem(type="Burn", element=orion_sm_1.id),
                    ],
                ),
                BurnStageSequence(
                    burn=db.get_edge("LLPO-PAC").burns[4].id,
                    actions=[
                        BurnStageItem(type="Burn", element=orion_sm_1.id),
                    ],
                ),
                BurnStageSequence(
                    burn=db.get_edge("LLPO-PAC").burns[5].id,
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
    start_date=datetime(2019, 7, 1, 4, tzinfo=timezone.utc),
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
    configuration=Configuration(environmentConstrained=True),
)

with open("completed_quick_start_1_w_db.json", "w", encoding="utf-8") as f:
    f.write(scenario.json(exclude_none=True, indent=2, by_alias=True))
