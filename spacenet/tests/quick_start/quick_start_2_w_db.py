from spacenet.schemas import *
from datetime import datetime, timedelta, timezone

from db_loader import load_db

db = load_db("quick_start_2.xlsx")

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
def instantiate_element(cls, template_name, prefix=None, suffix=None):
    return cls(
        template_id=next(filter(lambda o: o.name == template_name, db.elements)).id,
        name=(prefix + " | " if prefix != None else "")
        + next(filter(lambda o: o.name == template_name, db.elements)).name
        + (" " + suffix if suffix != None else ""),
    )


checkout_lander = instantiate_element(InstElementCarrier, "Crewed Lander", "Autom")
checkout_return = instantiate_element(
    InstElementCarrier, "Crewed Return Capsule", "Autom"
)
crewed_lander_1 = instantiate_element(InstElementCarrier, "Crewed Lander", "7-Day")
crewed_return_1 = instantiate_element(
    InstElementCarrier, "Crewed Return Capsule", "7-Day"
)
crew_1_1 = instantiate_element(InstHumanAgent, "Crew Member", "7-Day", "A")
crew_1_2 = instantiate_element(InstHumanAgent, "Crew Member", "7-Day", "B")
crew_1_3 = instantiate_element(InstHumanAgent, "Crew Member", "7-Day", "C")
crew_1_4 = instantiate_element(InstHumanAgent, "Crew Member", "7-Day", "D")
cargo_lander = instantiate_element(InstElementCarrier, "Cargo Lander", "Habitat")
habitat = instantiate_element(InstElementCarrier, "Crew Habitat", "Habitat")
psu = instantiate_element(InstElement, "Power Supply Unit", "Habitat")
crewed_lander_2 = instantiate_element(InstElementCarrier, "Crewed Lander", "14-Da")
crewed_return_2 = instantiate_element(
    InstElementCarrier, "Crewed Return Capsule", "14-Da"
)
crew_2_1 = instantiate_element(InstHumanAgent, "Crew Member", "14-Da", "A")
crew_2_2 = instantiate_element(InstHumanAgent, "Crew Member", "14-Da", "B")
crew_2_3 = instantiate_element(InstHumanAgent, "Crew Member", "14-Da", "C")
crew_2_4 = instantiate_element(InstHumanAgent, "Crew Member", "14-Da", "D")


##########################################
# DEMAND MODELS
##########################################
consumables_model = CrewConsumablesDemandModel(
    name="Crew Consumables Demand Model",
    reserves_duration=0.0,
    waterRecoveryRate=0.42,
    clothingLifetime=4.0,
    transitDemandsOmitted=True,
)

##########################################
# MISSIONS
##########################################
checkout = Mission(
    name="Automated Check-out Mission",
    start_date=datetime(2019, 7, 1, 4, tzinfo=timezone.utc),
    origin=get_node("KSC").id,
    destination=get_node("LSP").id,
    demand_models=[],
    events=[
        CreateElements(
            name="Autom | Create Elements",
            mission_time=timedelta(0),
            priority=1,
            location=get_node("KSC").id,
            container=get_node("KSC").id,
            elements=[checkout_lander.id, checkout_return.id],
        ),
        FlightTransport(
            name="Autom | Flight Transport",
            mission_time=timedelta(0),
            priority=2,
            location=get_node("KSC").id,
            edge=get_edge("Crewed Delivery").id,
            elements=[checkout_lander.id, checkout_return.id],
        ),
    ],
)
crewed_7_day = Mission(
    name="7-Day Surface Exploration",
    start_date=datetime(2019, 12, 1, 4, tzinfo=timezone.utc),
    origin=get_node("KSC").id,
    destination=get_node("LSP").id,
    return_origin=get_node("LSP").id,
    return_destination=get_node("PAC").id,
    demand_models=[
        InstCrewConsumablesDemandModel(
            name="Crew Consumables Demand Model", template_id=consumables_model.id
        )
    ],
    events=[
        CreateElements(
            name="7-Day | Create Elements",
            mission_time=timedelta(0),
            priority=1,
            location=get_node("KSC").id,
            container=get_node("KSC").id,
            elements=[crewed_lander_1.id, crewed_return_1.id],
        ),
        CreateElements(
            name="7-Day | Create Elements",
            mission_time=timedelta(0),
            priority=2,
            location=get_node("KSC").id,
            container=crewed_lander_1.id,
            elements=[crew_1_1.id, crew_1_2.id, crew_1_3.id, crew_1_4.id,],
        ),
        FlightTransport(
            name="7-Day | Flight Transport",
            mission_time=timedelta(0),
            priority=3,
            location=get_node("KSC").id,
            edge=get_edge("Crewed Delivery").id,
            elements=[crewed_lander_1.id, crewed_return_1.id],
        ),
        CrewedExploration(
            name="7-Day | Crewed Exploration",
            mission_time=timedelta(days=7, hours=12),
            priority=1,
            location=get_node("LSP").id,
            duration=timedelta(days=7),
            eva_duration=timedelta(hours=8),
            eva_per_week=5.0,
            vehicle=crewed_lander_1.id,
            element_states=[
                ElementState(element=crew_1_1.id, state_index=-1),
                ElementState(element=crew_1_2.id, state_index=-1),
            ],
        ),
        MoveElements(
            name="7-Day | Move Elements",
            mission_time=timedelta(days=14, hours=12),
            priority=1,
            location=get_node("LSP").id,
            container=crewed_return_1.id,
            elements=[crew_1_1.id, crew_1_2.id, crew_1_3.id, crew_1_4.id,],
        ),
        FlightTransport(
            name="7-Day | Flight Transport",
            mission_time=timedelta(days=14, hours=12),
            priority=2,
            location=get_node("LSP").id,
            edge=get_edge("Crewed Return").id,
            elements=[crewed_return_1.id],
        ),
        RemoveElements(
            name="7-Day | Remove Elements",
            mission_time=timedelta(days=20),
            priority=1,
            location=get_node("PAC").id,
            elements=[crewed_return_1.id],
        ),
    ],
)
hab_delivery = Mission(
    name="Habitat Delivery",
    start_date=datetime(2020, 3, 1, 4, tzinfo=timezone.utc),
    origin=get_node("KSC").id,
    destination=get_node("LSP").id,
    demand_models=[],
    events=[
        CreateElements(
            name="Habit | Create Elements",
            mission_time=timedelta(0),
            priority=1,
            location=get_node("KSC").id,
            container=get_node("KSC").id,
            elements=[cargo_lander.id],
        ),
        CreateElements(
            name="Habit | Create Elements",
            mission_time=timedelta(0),
            priority=2,
            location=get_node("KSC").id,
            container=cargo_lander.id,
            elements=[habitat.id, psu.id],
        ),
        FlightTransport(
            name="Habit | Flight Transport",
            mission_time=timedelta(0),
            priority=3,
            location=get_node("KSC").id,
            edge=get_edge("Cargo Delivery").id,
            elements=[cargo_lander.id],
        ),
    ],
)
crewed_14_day = Mission(
    name="14-Day Surface Exploration",
    start_date=datetime(2020, 7, 1, 4, tzinfo=timezone.utc),
    origin=get_node("KSC").id,
    destination=get_node("LSP").id,
    return_origin=get_node("LSP").id,
    return_destination=get_node("PAC").id,
    demand_models=[
        InstCrewConsumablesDemandModel(
            name="Crew Consumables Demand Model", template_id=consumables_model.id
        )
    ],
    events=[
        CreateElements(
            name="14-Da | Create Elements",
            mission_time=timedelta(0),
            priority=1,
            location=get_node("KSC").id,
            container=get_node("KSC").id,
            elements=[crewed_lander_2.id, crewed_return_2.id],
        ),
        CreateElements(
            name="14-Da | Create Elements",
            mission_time=timedelta(0),
            priority=2,
            location=get_node("KSC").id,
            container=crewed_lander_2.id,
            elements=[crew_2_1.id, crew_2_2.id, crew_2_3.id, crew_2_4.id,],
        ),
        FlightTransport(
            name="14-Da | Flight Transport",
            mission_time=timedelta(0),
            priority=3,
            location=get_node("KSC").id,
            edge=get_edge("Crewed Delivery").id,
            elements=[crewed_lander_2.id, crewed_return_2.id],
        ),
        MoveElements(
            name="14-Da | Move Elements",
            mission_time=timedelta(days=7, hours=12),
            priority=1,
            location=get_node("LSP").id,
            container=habitat.id,
            elements=[crew_2_1.id, crew_2_2.id, crew_2_3.id, crew_2_4.id,],
        ),
        ReconfigureElements(
            name="14-Da | Reconfigure Group",
            mission_time=timedelta(days=7, hours=12),
            priority=2,
            location=get_node("LSP").id,
            elements=[habitat.id, psu.id],
            state_type="Active",
        ),
        CrewedExploration(
            name="14-Da | Crewed Exploration",
            mission_time=timedelta(days=7, hours=12),
            priority=3,
            location=get_node("LSP").id,
            duration=timedelta(days=14),
            eva_duration=timedelta(hours=8),
            eva_per_week=5.0,
            vehicle=habitat.id,
            element_states=[
                ElementState(element=crew_2_1.id, state_index=-1),
                ElementState(element=crew_2_2.id, state_index=-1),
            ],
        ),
        MoveElements(
            name="14-Da | Move Elements",
            mission_time=timedelta(days=21, hours=12),
            priority=1,
            location=get_node("LSP").id,
            container=crewed_return_2.id,
            elements=[crew_2_1.id, crew_2_2.id, crew_2_3.id, crew_2_4.id,],
        ),
        ReconfigureElements(
            name="14-Da | Reconfigure Group",
            mission_time=timedelta(days=21, hours=12),
            priority=2,
            location=get_node("LSP").id,
            elements=[habitat.id, psu.id],
            state_type="Dormant",
        ),
        FlightTransport(
            name="14-Da | Flight Transport",
            mission_time=timedelta(days=21, hours=12),
            priority=3,
            location=get_node("LSP").id,
            edge=get_edge("Crewed Return").id,
            elements=[crewed_return_2.id],
        ),
        RemoveElements(
            name="14-Da | Remove Elements",
            mission_time=timedelta(days=27),
            priority=1,
            location=get_node("PAC").id,
            elements=[crewed_return_2.id],
        ),
    ],
)

##########################################
# SCENARIO
##########################################
scenario = Scenario(
    name="Quick Start Scenario 2",
    description="A sample scenario analyzing the feasibility of a lunar outpost.",
    created_by="SpaceNet User",
    start_date=datetime(2019, 7, 1, 4, tzinfo=timezone.utc),
    scenario_type="Lunar",
    network=Network(nodes=db.nodes, edges=db.edges,),
    mission_list=[checkout, crewed_7_day, hab_delivery, crewed_14_day],
    resource_list=db.resources,
    element_templates=db.elements,
    instantiated_elements=[
        checkout_lander,
        checkout_return,
        crewed_lander_1,
        crewed_return_1,
        crew_1_1,
        crew_1_2,
        crew_1_3,
        crew_1_4,
        cargo_lander,
        habitat,
        psu,
        crewed_lander_2,
        crewed_return_2,
        crew_2_1,
        crew_2_2,
        crew_2_3,
        crew_2_4,
    ],
    demand_models=[consumables_model] + db.demand_models,
    configuration=Configuration(environmentConstrained=True),
)

with open("completed_quick_start_2_w_db.json", "w") as f:
    f.write(scenario.json(exclude_none=True, indent=2, by_alias=True))
