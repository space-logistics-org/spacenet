"""Module for handling datetime-related data structures."""
from datetime import datetime, timedelta, timezone

from spacenet import schemas

##########################################
# NODES
##########################################
ksc = schemas.SurfaceNode(
    name="KSC",
    description="Kennedy Space Center",
    body1="Earth",
    latitude=28.6,
    longitude=-80.6,
)
pac = schemas.SurfaceNode(
    name="PAC",
    description="Pacific Ocean Splash-down",
    body1="Earth",
    latitude=35.0,
    longitude=-117.9,
)
leo = schemas.OrbitalNode(
    name="LEO",
    description="Low Earth Orbit",
    body1="Earth",
    inclination=28.5,
    periapsis=296.0,
    apoapsis=296.0,
)
nro = schemas.LagrangeNode(
    name="NRO",
    description="Near Rectilinear Halo Orbit",
    body1="Earth",
    body2="Moon",
    lp_number=2,
)
llo = schemas.OrbitalNode(
    name="LLO",
    description="Low Lunar Orbit",
    body1="Moon",
    inclination=90.0,
    periapsis=100.0,
    apoapsis=100.0,
)
lsp = schemas.SurfaceNode(
    name="LSP",
    description="Lunar South Pole",
    body1="Moon",
    latitude=-89.9,
    longitude=-180.0,
)

##########################################
# EDGES
##########################################
ksc_leo = schemas.SpaceEdge(
    name="KSC-LEO",
    description="Earth Ascent",
    origin=ksc.id,
    destination=leo.id,
    duration=timedelta(hours=6),
    burns=[schemas.Burn(time=timedelta(0), delta_v=9500.0)],
)
leo_nro = schemas.SpaceEdge(
    name="LEO-NRO",
    description="Trans-Lunar Injection",
    origin=leo.id,
    destination=nro.id,
    duration=timedelta(days=7),
    burns=[
        schemas.Burn(time=timedelta(0), delta_v=3124.0),
        schemas.Burn(time=timedelta(days=0.3), delta_v=30.0),
        schemas.Burn(time=timedelta(days=3.1), delta_v=242.0),
        schemas.Burn(time=timedelta(days=4.4), delta_v=1.0),
        schemas.Burn(time=timedelta(days=6.4), delta_v=126.0),
    ],
)
nro_llo = schemas.SpaceEdge(
    name="NRO-LLO",
    description="Transfer to Low Lunar Orbit",
    origin=nro.id,
    destination=llo.id,
    duration=timedelta(days=0.5),
    burns=[
        schemas.Burn(time=timedelta(0), delta_v=126.4),
        schemas.Burn(time=timedelta(days=0.5), delta_v=648.6),
    ],
)
llo_lsp = schemas.SpaceEdge(
    name="LLO-LSP",
    description="Lunar Descent",
    origin=llo.id,
    destination=lsp.id,
    duration=timedelta(days=0.2),
    burns=[
        schemas.Burn(time=timedelta(0), delta_v=19.4),
        schemas.Burn(time=timedelta(days=0.2), delta_v=1692.5),
    ],
)
lsp_llo = schemas.SpaceEdge(
    name="LSP-LLO",
    description="Lunar Ascent",
    origin=lsp.id,
    destination=llo.id,
    duration=timedelta(days=0.2),
    burns=[
        schemas.Burn(time=timedelta(0), delta_v=1692.4),
        schemas.Burn(time=timedelta(days=0.2), delta_v=19.4),
    ],
)
llo_nro = schemas.SpaceEdge(
    name="LLO-NRO",
    description="Transfer to Near Rectilinear Halo Orbit",
    origin=llo.id,
    destination=nro.id,
    duration=timedelta(days=0.5),
    burns=[
        schemas.Burn(time=timedelta(0), delta_v=649.2),
        schemas.Burn(time=timedelta(days=0.5), delta_v=125.1),
    ],
)
nro_pac = schemas.SpaceEdge(
    name="NRO-PAC",
    description="Trans-Earth Injection",
    origin=nro.id,
    destination=pac.id,
    duration=timedelta(days=6.4),
    burns=[
        schemas.Burn(time=timedelta(0), delta_v=147.0),
        schemas.Burn(time=timedelta(days=1.6), delta_v=2.0),
        schemas.Burn(time=timedelta(days=2.8), delta_v=263.0),
    ],
)

##########################################
# RESOURCES
##########################################
pban_solid = schemas.ContinuousResource(
    name="PBAN Solid",
    description="Solid rocket fuel",
    classOfSupply=105,
    environment="Unpressurized",
    units="kg",
    unitMass=1.0,
    unitVolume=1/955,
    packingFactor=0.0,
)
lox_lh2 = schemas.ContinuousResource(
    name="LOX/LH2",
    description="Liquid oxygen/liquid hydrogen cryogenic fuel",
    classOfSupply=101,
    environment="Unpressurized",
    units="kg",
    unitMass=1.0,
    unitVolume=1/59231,
    packingFactor=0.0,
)
mmh_n2o4 = schemas.ContinuousResource(
    name="MMH/N2O4",
    description="Hypergolic fuel",
    classOfSupply=102,
    environment="Unpressurized",
    units="kg",
    unitMass=1.0,
    unitVolume=1/1200,
    packingFactor=0.0,
)
lox_lch4 = schemas.ContinuousResource(
    name="LOX/LCH4",
    description="Liquid oxygen/liquid methane",
    classOfSupply=101,
    environment="Unpressurized",
    units="kg",
    unitMass=1.0,
    unitVolume=1/424,
    packingFactor=0.0,
)

##########################################
# DEMAND MODELS
##########################################
# none to report

##########################################
# ELEMENT TEMPLATES
##########################################
sls_srbs = schemas.PropulsiveVehicle(
    name="SLS SRBs",
    description="SLS Solid Rocket Boosters (2)",
    mass=195000.0,
    volume=0.0,
    class_of_supply=9021,
    environment="Unpressurized",
    accommodation_mass=0.0,
    cargo_environment="Unpressurized",
    max_cargo_mass=0.0,
    max_cargo_volume=0.0,
    max_crew=0,
    max_fuel=1256000.0,
    fuel=schemas.ResourceAmount(resource=pban_solid.id, amount=1256000.0),
    isp=269.0,
    states=[],
    parts=[],
)
sls_core = schemas.PropulsiveVehicle(
    name="SLS Core",
    description="SLS Core Stage",
    mass=88275.0,
    volume=0.0,
    class_of_supply=9021,
    environment="Unpressurized",
    accommodation_mass=0.0,
    cargo_environment="Unpressurized",
    max_cargo_mass=0.0,
    max_cargo_volume=0.0,
    max_crew=0,
    max_fuel=987000.0,
    fuel=schemas.ResourceAmount(resource=lox_lh2.id, amount=987000.0),
    isp=414.0,
    states=[],
    parts=[],
)
sls_icps = schemas.PropulsiveVehicle(
    name="iCPS",
    description="SLS Interim Cryogenic Propulsion Stage",
    mass=3490.0,
    volume=0.0,
    class_of_supply=9022,
    environment="Unpressurized",
    accommodation_mass=0.0,
    cargo_environment="Unpressurized",
    max_cargo_mass=0.0,
    max_cargo_volume=0.0,
    max_crew=0,
    max_fuel=28576.0,
    fuel=schemas.ResourceAmount(resource=lox_lh2.id, amount=28576.0),
    isp=465.0,
    states=[],
    parts=[],
)
sls_sa = schemas.Element(
    name="SLS SA",
    description="SLS Spacecraft Adapter",
    mass=1900.0,
    volume=0.0,
    class_of_supply=5,
    environment="Unpressurized",
    accommodation_mass=0.0,
    states=[],
    parts=[],
)
orion_sm = schemas.PropulsiveVehicle(
    name="Orion SM",
    description="Orion Service Module",
    mass=6185.0,
    volume=0.0,
    class_of_supply=9022,
    environment="Unpressurized",
    accommodation_mass=0.0,
    cargo_environment="Unpressurized",
    max_cargo_mass=0.0,
    max_cargo_volume=0.0,
    max_crew=4,
    max_fuel=9276.0,
    fuel=schemas.ResourceAmount(resource=mmh_n2o4.id, amount=9276.0),
    isp=316.0,
    states=[],
    parts=[],
)
orion_cm = schemas.ElementCarrier(
    name="Orion CM",
    description="Orion Crew Module",
    mass=9300.0,
    volume=0.0,
    class_of_supply=9022,
    environment="Unpressurized",
    accommodation_mass=0.0,
    cargo_environment="Unpressurized",
    max_cargo_mass=1100.0,
    max_cargo_volume=0.0,
    max_crew=4,
    states=[],
    parts=[],
)
sls_las = schemas.ElementCarrier(
    name="SLS LAS",
    description="SLS Launch Abort System",
    mass=7250.0,
    volume=0.0,
    class_of_supply=9021,
    environment="Unpressurized",
    accommodation_mass=0.0,
    cargo_environment="Unpressurized",
    max_cargo_mass=0.0,
    max_cargo_volume=0.0,
    max_crew=0,
    states=[],
    parts=[],
)
crew_member = schemas.HumanAgent(
    name="Crew Member",
    description="Crew Member",
    mass=100.0,
    volume=0.0,
    class_of_supply=0,
    environment="Unpressurized",
    accommodation_mass=0.0,
    active_time_fraction=0.66,
    states=[],
    parts=[],
)
samples = schemas.Element(
    name="Lunar Surface Samples",
    description="Lunar Surface Samples",
    mass=100.0,
    volume=0.0,
    class_of_supply=6,
    environment="Unpressurized",
    accommodation_mass=0.0,
    states=[],
    parts=[],
)
cargo = schemas.Element(
    name="Notional Cargo",
    description="Notional Cargo",
    mass=500.0,
    volume=0.0,
    class_of_supply=6,
    environment="Unpressurized",
    accommodation_mass=0.0,
    states=[],
    parts=[],
)
hls = schemas.PropulsiveVehicle(
    name="HLS",
    description="Human Landing System",
    mass=8149.0,
    volume=0.0,
    class_of_supply=902,
    environment="Unpressurized",
    accommodation_mass=0.0,
    cargo_environment="Unpressurized",
    max_cargo_mass=900.0,
    max_cargo_volume=0.0,
    max_crew=2,
    max_fuel=32285.0,
    fuel=schemas.ResourceAmount(resource=lox_lch4.id, amount=32285.0),
    isp=363.0,
    states=[],
    parts=[],
)

##########################################
# INSTANTIATED ELEMENTS
##########################################
sls_srbs_1 = schemas.InstPropulsiveVehicle(
    template_id=sls_srbs.id, name="Lunar | " + sls_srbs.name
)
sls_core_1 = schemas.InstPropulsiveVehicle(
    template_id=sls_core.id, name="Lunar | " + sls_core.name
)
sls_icps_1 = schemas.InstPropulsiveVehicle(
    template_id=sls_icps.id, name="Lunar | " + sls_icps.name
)
sls_sa_1 = schemas.InstElement(
    template_id=sls_sa.id, name="Lunar | " + sls_sa.name
)
orion_sm_1 = schemas.InstPropulsiveVehicle(
    template_id=orion_sm.id, name="Lunar | " + orion_sm.name
)
orion_cm_1 = schemas.InstElementCarrier(
    template_id=orion_cm.id, name="Lunar | " + orion_cm.name
)
sls_las_1 = schemas.InstElementCarrier(
    template_id=sls_las.id, name="Lunar | " + sls_las.name
)
crew_member_1_1 = schemas.InstHumanAgent(
    template_id=crew_member.id, name="Lunar | " + crew_member.name + " A"
)
crew_member_1_2 = schemas.InstHumanAgent(
    template_id=crew_member.id, name="Lunar | " + crew_member.name + " B"
)
crew_member_1_3 = schemas.InstHumanAgent(
    template_id=crew_member.id, name="Lunar | " + crew_member.name + " C"
)
crew_member_1_4 = schemas.InstHumanAgent(
    template_id=crew_member.id, name="Lunar | " + crew_member.name + " D"
)
cargo_1 = schemas.InstElement(template_id=cargo.id, name="Lunar | " + cargo.name)
samples_1 = schemas.InstElement(template_id=samples.id, name="Lunar | " + samples.name)
hls_1 = schemas.InstPropulsiveVehicle(template_id=hls.id, name="Lunar | " + hls.name)

##########################################
# MISSIONS
##########################################
lunar_sortie = schemas.Mission(
    name="Lunar Sortie",
    start_date=datetime(2025, 7, 4, tzinfo=timezone.utc),
    origin=ksc.id,
    destination=lsp.id,
    return_origin=lsp.id,
    return_destination=pac.id,
    demand_models=[],
    events=[
        schemas.CreateElements(
            name="Lunar | Pre-position Landing System",
            mission_time=timedelta(0),
            priority=1,
            location=nro.id,
            container=nro.id,
            elements=[
                hls_1.id
            ],
        ),
        schemas.CreateElements(
            name="Lunar | Create Launch Stack",
            mission_time=timedelta(0),
            priority=2,
            location=ksc.id,
            container=ksc.id,
            elements=[
                sls_srbs_1.id,
                sls_core_1.id,
                sls_sa_1.id,
                sls_icps_1.id,
                orion_cm_1.id,
                orion_sm_1.id,
                sls_las_1.id,
            ],
        ),
        schemas.CreateElements(
            name="Lunar | Create Crew Members",
            mission_time=timedelta(0),
            priority=3,
            location=ksc.id,
            container=orion_cm_1.id,
            elements=[
                crew_member_1_1.id,
                crew_member_1_2.id,
                crew_member_1_3.id,
                crew_member_1_4.id,
            ],
        ),
        schemas.SpaceTransport(
            name="Lunar | Earth Ascent Transport",
            mission_time=timedelta(0),
            priority=4,
            location=ksc.id,
            edge=ksc_leo.id,
            elements=[
                sls_srbs_1.id,
                sls_core_1.id,
                sls_sa_1.id,
                sls_icps_1.id,
                orion_cm_1.id,
                orion_sm_1.id,
                sls_las_1.id,
            ],
            burn_stage_sequence=[
                schemas.BurnStageSequence(
                    burn=ksc_leo.burns[0].id,
                    actions=[
                        schemas.BurnStageItem(type="Burn", element=sls_srbs_1.id),
                        schemas.BurnStageItem(type="Stage", element=sls_srbs_1.id),
                        schemas.BurnStageItem(type="Stage", element=sls_las_1.id),
                        schemas.BurnStageItem(type="Burn", element=sls_core_1.id),
                        schemas.BurnStageItem(type="Stage", element=sls_core_1.id),
                        schemas.BurnStageItem(type="Stage", element=sls_sa_1.id),
                    ],
                )
            ],
        ),
        schemas.SpaceTransport(
            name="Lunar | Trans-Lunar Injection Transport",
            mission_time=timedelta(days=1),
            priority=1,
            location=leo.id,
            edge=leo_nro.id,
            elements=[
                sls_icps_1.id,
                orion_cm_1.id,
                orion_sm_1.id,
            ],
            burn_stage_sequence=[
                schemas.BurnStageSequence(
                    burn=leo_nro.burns[0].id,
                    actions=[
                        schemas.BurnStageItem(type="Burn", element=sls_icps_1.id),
                        schemas.BurnStageItem(type="Stage", element=sls_icps_1.id),
                    ],
                ),
                schemas.BurnStageSequence(
                    burn=leo_nro.burns[1].id,
                    actions=[schemas.BurnStageItem(type="Burn", element=orion_sm_1.id),],
                ),
                schemas.BurnStageSequence(
                    burn=leo_nro.burns[2].id,
                    actions=[schemas.BurnStageItem(type="Burn", element=orion_sm_1.id),],
                ),
                schemas.BurnStageSequence(
                    burn=leo_nro.burns[3].id,
                    actions=[schemas.BurnStageItem(type="Burn", element=orion_sm_1.id),],
                ),
                schemas.BurnStageSequence(
                    burn=leo_nro.burns[4].id,
                    actions=[schemas.BurnStageItem(type="Burn", element=orion_sm_1.id),],
                ),
            ],
        ),
        schemas.MoveElements(
            name="Lunar | Rendezvous, Crew Transfer",
            mission_time=timedelta(days=8),
            priority=1,
            location=nro.id,
            container=hls_1.id,
            elements=[
                crew_member_1_1.id,
                crew_member_1_2.id,
            ],
        ),
        schemas.SpaceTransport(
            name="Lunar | Transfer to Low Lunar Orbit",
            mission_time=timedelta(days=9),
            priority=1,
            location=nro.id,
            edge=nro_llo.id,
            elements=[hls_1.id],
            burn_stage_sequence=[
                schemas.BurnStageSequence(
                    burn=nro_llo.burns[0].id,
                    actions=[schemas.BurnStageItem(type="Burn", element=hls_1.id),],
                ),
                schemas.BurnStageSequence(
                    burn=nro_llo.burns[1].id,
                    actions=[schemas.BurnStageItem(type="Burn", element=hls_1.id),],
                ),
            ],
        ),
        schemas.SpaceTransport(
            name="Lunar | Lunar Descent",
            mission_time=timedelta(days=10),
            priority=1,
            location=llo.id,
            edge=llo_lsp.id,
            elements=[hls_1.id],
            burn_stage_sequence=[
                schemas.BurnStageSequence(
                    burn=llo_lsp.burns[0].id,
                    actions=[schemas.BurnStageItem(type="Burn", element=hls_1.id),],
                ),
                schemas.BurnStageSequence(
                    burn=llo_lsp.burns[1].id,
                    actions=[schemas.BurnStageItem(type="Burn", element=hls_1.id),],
                ),
            ],
        ),
        schemas.CrewedExploration(
            name="Lunar | Crewed Exploration",
            mission_time=timedelta(days=11),
            priority=1,
            location=lsp.id,
            vehicle=hls_1.id,
            duration=timedelta(days=7),
            eva_per_week=5.0,
            eva_duration=timedelta(hours=8),
            element_states=[
                schemas.ElementState(element=crew_member_1_1.id, state_index=-1),
                schemas.ElementState(element=crew_member_1_2.id, state_index=-1),
            ],
            additional_demands=[],
        ),
        schemas.CreateElements(
            name="Lunar | Create Samples",
            mission_time=timedelta(days=18),
            priority=1,
            location=lsp.id,
            container=hls_1.id,
            elements=[samples_1.id,],
        ),
        schemas.SpaceTransport(
            name="Lunar | Lunar Ascent",
            mission_time=timedelta(days=18),
            priority=2,
            location=lsp.id,
            edge=lsp_llo.id,
            elements=[hls_1.id],
            burn_stage_sequence=[
                schemas.BurnStageSequence(
                    burn=lsp_llo.burns[0].id,
                    actions=[schemas.BurnStageItem(type="Burn", element=hls_1.id),],
                ),
                schemas.BurnStageSequence(
                    burn=lsp_llo.burns[1].id,
                    actions=[schemas.BurnStageItem(type="Burn", element=hls_1.id),],
                ),
            ],
        ),
        schemas.SpaceTransport(
            name="Lunar | Transfer to Halo Orbit",
            mission_time=timedelta(days=19),
            priority=2,
            location=llo.id,
            edge=llo_nro.id,
            elements=[hls_1.id],
            burn_stage_sequence=[
                schemas.BurnStageSequence(
                    burn=llo_nro.burns[0].id,
                    actions=[schemas.BurnStageItem(type="Burn", element=hls_1.id),],
                ),
                schemas.BurnStageSequence(
                    burn=llo_nro.burns[1].id,
                    actions=[schemas.BurnStageItem(type="Burn", element=hls_1.id),],
                ),
            ],
        ),
        schemas.MoveElements(
            name="Lunar | Rendezvous, Transfer Crew and Samples",
            mission_time=timedelta(days=20),
            priority=1,
            location=nro.id,
            container=orion_cm_1.id,
            elements=[
                crew_member_1_1.id,
                crew_member_1_2.id,
                samples_1.id,
            ],
        ),
        schemas.SpaceTransport(
            name="Lunar | Trans-Earth Injection",
            mission_time=timedelta(days=21),
            priority=2,
            location=nro.id,
            edge=nro_pac.id,
            elements=[orion_cm_1.id, orion_sm_1.id],
            burn_stage_sequence=[
                schemas.BurnStageSequence(
                    burn=nro_pac.burns[0].id,
                    actions=[schemas.BurnStageItem(type="Burn", element=orion_sm_1.id),],
                ),
                schemas.BurnStageSequence(
                    burn=nro_pac.burns[1].id,
                    actions=[schemas.BurnStageItem(type="Burn", element=orion_sm_1.id),],
                ),
                schemas.BurnStageSequence(
                    burn=nro_pac.burns[2].id,
                    actions=[
                        schemas.BurnStageItem(type="Burn", element=orion_sm_1.id),
                        schemas.BurnStageItem(type="Stage", element=orion_sm_1.id),
                    ],
                ),
            ],
        ),
    ],
)

##########################################
# SCENARIO
##########################################
scenario = schemas.Scenario(
    name="Quick Start Scenario 3",
    description="A sample scenario analyzing the transportation feasibility of a lunar mission.",
    created_by="SpaceNet User",
    start_date=datetime(2025, 7, 4, tzinfo=timezone.utc),
    scenario_type="Lunar",
    network=schemas.Network(
        nodes=[ksc, pac, leo, nro, llo, lsp],
        edges=[ksc_leo, leo_nro, nro_llo, llo_lsp, lsp_llo, llo_nro, nro_pac],
    ),
    mission_list=[lunar_sortie],
    resource_list=[pban_solid, lox_lh2, lox_lch4, mmh_n2o4],
    element_templates=[
        sls_core,
        sls_srbs,
        sls_icps,
        sls_sa,
        orion_sm,
        orion_cm,
        sls_las,
        crew_member,
        samples,
        cargo,
        hls,
    ],
    instantiated_elements=[
        sls_core_1,
        sls_srbs_1,
        sls_icps_1,
        sls_sa_1,
        orion_sm_1,
        orion_cm_1,
        sls_las_1,
        crew_member_1_1,
        crew_member_1_2,
        crew_member_1_3,
        crew_member_1_4,
        samples_1,
        cargo_1,
        hls_1,
    ],
    demand_models=[],
    configuration=schemas.Configuration(environmentConstrained=True),
)

with open("completed_quick_start_3_wo_db.json", "w", encoding="utf-8") as f:
    f.write(scenario.json(exclude_none=True, indent=2, by_alias=True))
