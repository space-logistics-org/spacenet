from spacenet.schemas import *

##########################################
# NODES
##########################################
ksc = SurfaceNode(
    name="KSC",
    description="Kennedy Space Center",
    body1="Earth",
    latitude=28.6,
    longitude=-80.6,
)
pac = SurfaceNode(
    name="PAC",
    description="Pacific Ocean Splash-down",
    body1="Earth",
    latitude=35.0,
    longitude=-117.9,
)
leo = OrbitalNode(
    name="LEO",
    description="Low Earth Orbit",
    body1="Earth",
    inclination=28.5,
    periapsis=296.0,
    apoapsis=296.0,
)
llpo = OrbitalNode(
    name="LLPO",
    description="Low Lunar Polar Orbit",
    body1="Moon",
    inclination=90.0,
    periapsis=100.0,
    apoapsis=100.0,
)
lsp = SurfaceNode(
    name="LSP",
    description="Lunar South Pole",
    body1="Moon",
    latitude=-89.9,
    longitude=-180.0,
)

##########################################
# EDGES
##########################################
ksc_leo = SpaceEdge(
    name="KSC-LEO",
    description="Earth Ascent",
    origin=ksc.id,
    destination=leo.id,
    duration="PT6H",
    burns=[Burn(time="PT0S", delta_v=9500.0)],
)
leo_llpo = SpaceEdge(
    name="LEO-LLPO",
    description="Lunar Orbit Injection",
    origin=leo.id,
    destination=llpo.id,
    duration="P4D",
    burns=[
        Burn(time="PT0S", delta_v=3150.0),
        Burn(time="PT12H", delta_v=2.0),
        Burn(time="P2DT12H", delta_v=2.0),
        Burn(time="P4D", delta_v=950.0),
    ],
)
llpo_lsp = SpaceEdge(
    name="LLPO-LSP",
    description="Lunar Descent",
    origin=llpo.id,
    destination=lsp.id,
    duration="PT12H",
    burns=[Burn(time="PT0S", delta_v=2030.0), Burn(time="PT6H", delta_v=11.0),],
)
lsp_llpo = SpaceEdge(
    name="LSP-LLPO",
    description="Lunar Ascent",
    origin=lsp.id,
    destination=llpo.id,
    duration="PT12H",
    burns=[Burn(time="PT0S", delta_v=1875.0), Burn(time="PT6H", delta_v=31.0),],
)
llpo_pac = SpaceEdge(
    name="LLPO-PAC",
    description="Trans-Earth Injection",
    origin=llpo.id,
    destination=pac.id,
    duration="P4D",
    burns=[
        Burn(time="PT0S", delta_v=612.3),
        Burn(time="PT12H", delta_v=276.5),
        Burn(time="P1D", delta_v=333.6),
        Burn(time="P1DT12H", delta_v=3.2),
        Burn(time="P3D", delta_v=3.2),
        Burn(time="P4D", delta_v=5.0),
    ],
)

##########################################
# RESOURCES
##########################################
pban_solid = ContinuousResource(
    name="PBAN Solid",
    description="Solid rocket fuel",
    classOfSupply=105,
    environment="Unpressurized",
    units="kg",
    unitMass=1.0,
    unitVolume=0.0,
    packingFactor=0.0,
)
lh2_lox = ContinuousResource(
    name="LH2/LOX",
    description="Liquid oxygen/liquid hydrogen cryogenic fuel",
    classOfSupply=101,
    environment="Unpressurized",
    units="kg",
    unitMass=1.0,
    unitVolume=0.0,
    packingFactor=0.0,
)
mmh_n2o4 = ContinuousResource(
    name="MMH/N2O4",
    description="Hypergolic fuel",
    classOfSupply=102,
    environment="Unpressurized",
    units="kg",
    unitMass=1.0,
    unitVolume=0.0,
    packingFactor=0.0,
)

##########################################
# DEMAND MODELS
##########################################
# none to report

##########################################
# ELEMENT TEMPLATES
##########################################
altair_am = PropulsiveVehicle(
    name="Altair AM",
    description="Altair Ascent Module",
    mass=3000.0,
    volume=0.0,
    class_of_supply=9024,
    environment="Unpressurized",
    accommodation_mass=0.0,
    cargo_environment="Unpressurized",
    max_cargo_mass=100.0,
    max_cargo_volume=0.0,
    max_crew=4,
    max_fuel=3000.0,
    fuel=ResourceAmount(resource=mmh_n2o4.id, amount=3000.0),
    isp=320.0,
    states=[],
    parts=[],
)
altair_dm = PropulsiveVehicle(
    name="Altair DM",
    description="Altair Descent Module",
    mass=12000.0,
    volume=0.0,
    class_of_supply=9023,
    environment="Unpressurized",
    accommodation_mass=0.0,
    cargo_environment="Unpressurized",
    max_cargo_mass=500.0,
    max_cargo_volume=0.0,
    max_crew=0,
    max_fuel=24900.0,
    fuel=ResourceAmount(resource=lh2_lox.id, amount=24900.0),
    isp=448.0,
    states=[],
    parts=[],
)
ares_i_first_stage = PropulsiveVehicle(
    name="Ares I First Stage",
    description="Ares I Launch Vehicle, First Propulsive Stage",
    mass=105000.0,
    volume=0.0,
    class_of_supply=9021,
    environment="Unpressurized",
    accommodation_mass=0.0,
    cargo_environment="Unpressurized",
    max_cargo_mass=0.0,
    max_cargo_volume=0.0,
    max_crew=0,
    max_fuel=620000.0,
    fuel=ResourceAmount(resource=pban_solid.id, amount=620000.0),
    isp=267.0,
    states=[],
    parts=[],
)
ares_i_upper_stage = PropulsiveVehicle(
    name="Ares I Upper Stage",
    description="Ares I Launch Vehicle, Second Propulsive Stage",
    mass=12000.0,
    volume=0.0,
    class_of_supply=9021,
    environment="Unpressurized",
    accommodation_mass=0.0,
    cargo_environment="Unpressurized",
    max_cargo_mass=0.0,
    max_cargo_volume=0.0,
    max_crew=0,
    max_fuel=125000.0,
    fuel=ResourceAmount(resource=pban_solid.id, amount=125000.0),
    isp=448.0,
    states=[],
    parts=[],
)
ares_v_core = PropulsiveVehicle(
    name="Ares V Core",
    description="Ares V Launch Vehicle, Core Engine",
    mass=175000.0,
    volume=0.0,
    class_of_supply=9021,
    environment="Unpressurized",
    accommodation_mass=0.0,
    cargo_environment="Unpressurized",
    max_cargo_mass=0.0,
    max_cargo_volume=0.0,
    max_crew=0,
    max_fuel=1587000.0,
    fuel=ResourceAmount(resource=lh2_lox.id, amount=1587000.0),
    isp=414.0,
    states=[],
    parts=[],
)
ares_v_srbs = PropulsiveVehicle(
    name="Ares V SRBs",
    description="Ares V Launch Vehicle, Solid Rocket Boosters",
    mass=210000.0,
    volume=0.0,
    class_of_supply=9021,
    environment="Unpressurized",
    accommodation_mass=0.0,
    cargo_environment="Unpressurized",
    max_cargo_mass=0.0,
    max_cargo_volume=0.0,
    max_crew=0,
    max_fuel=1375000.0,
    fuel=ResourceAmount(resource=pban_solid.id, amount=1375000.0),
    isp=270.0,
    states=[],
    parts=[],
)
crew_member = HumanAgent(
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
eds = PropulsiveVehicle(
    name="EDS",
    description="Earth Departure System",
    mass=26000.0,
    volume=0.0,
    class_of_supply=9022,
    environment="Unpressurized",
    accommodation_mass=0.0,
    cargo_environment="Unpressurized",
    max_cargo_mass=0.0,
    max_cargo_volume=0.0,
    max_crew=0,
    max_fuel=253000.0,
    fuel=ResourceAmount(resource=lh2_lox.id, amount=253000.0),
    isp=448.0,
    states=[],
    parts=[],
)
samples = Element(
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
cargo = Element(
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
orion_cm = PropulsiveVehicle(
    name="Orion CM",
    description="Orion Crew Module",
    mass=8000.0,
    volume=0.0,
    class_of_supply=9022,
    environment="Unpressurized",
    accommodation_mass=0.0,
    cargo_environment="Unpressurized",
    max_cargo_mass=100.0,
    max_cargo_volume=0.0,
    max_crew=4,
    max_fuel=175.0,
    fuel=ResourceAmount(resource=mmh_n2o4.id, amount=175.0),
    isp=301.0,
    states=[],
    parts=[],
)
orion_las = ElementCarrier(
    name="Orion LAS",
    description="Orion Launch Abort System",
    mass=6000.0,
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
orion_sm = PropulsiveVehicle(
    name="Orion SM",
    description="Orion Service Module",
    mass=3000.0,
    volume=0.0,
    class_of_supply=9022,
    environment="Unpressurized",
    accommodation_mass=0.0,
    cargo_environment="Unpressurized",
    max_cargo_mass=0.0,
    max_cargo_volume=0.0,
    max_crew=4,
    max_fuel=10000.0,
    fuel=ResourceAmount(resource=mmh_n2o4.id, amount=10000.0),
    isp=301.0,
    states=[],
    parts=[],
)

##########################################
# INSTANTIATED ELEMENTS
##########################################
ares_i_first_stage_1 = InstPropulsiveVehicle(
    template_id=ares_i_first_stage.id, name="Lunar | " + ares_i_first_stage.name
)
ares_i_upper_stage_1 = InstPropulsiveVehicle(
    template_id=ares_i_upper_stage.id, name="Lunar | " + ares_i_upper_stage.name
)
orion_cm_1 = InstPropulsiveVehicle(
    template_id=orion_cm.id, name="Lunar | " + orion_cm.name
)
orion_sm_1 = InstPropulsiveVehicle(
    template_id=orion_sm.id, name="Lunar | " + orion_sm.name
)
orion_las_1 = InstElementCarrier(
    template_id=orion_las.id, name="Lunar | " + orion_las.name
)
crew_member_1_1 = InstHumanAgent(
    template_id=crew_member.id, name="Lunar | " + crew_member.name + " A"
)
crew_member_1_2 = InstHumanAgent(
    template_id=crew_member.id, name="Lunar | " + crew_member.name + " B"
)
crew_member_1_3 = InstHumanAgent(
    template_id=crew_member.id, name="Lunar | " + crew_member.name + " C"
)
crew_member_1_4 = InstHumanAgent(
    template_id=crew_member.id, name="Lunar | " + crew_member.name + " D"
)
altair_am_1 = InstPropulsiveVehicle(
    template_id=altair_am.id, name="Lunar | " + altair_am.name
)
altair_dm_1 = InstPropulsiveVehicle(
    template_id=altair_dm.id, name="Lunar | " + altair_dm.name
)
ares_v_core_1 = InstPropulsiveVehicle(
    template_id=ares_v_core.id, name="Lunar | " + ares_v_core.name
)
ares_v_srbs_1 = InstPropulsiveVehicle(
    template_id=ares_v_srbs.id, name="Lunar | " + ares_v_srbs.name
)
eds_1 = InstPropulsiveVehicle(template_id=eds.id, name="Lunar | " + eds.name)
cargo_1 = InstElement(template_id=cargo.id, name="Lunar | " + cargo.name)
samples_1 = InstElement(template_id=samples.id, name="Lunar | " + samples.name)

##########################################
# MISSIONS
##########################################
lunar_sortie = Mission(
    name="Lunar Sortie",
    startDate="2019-07-01T04:00:00.000Z",
    origin=ksc.id,
    destination=lsp.id,
    return_origin=lsp.id,
    return_destination=pac.id,
    demand_models=[],
    events=[
        CreateElements(
            name="Lunar | Create Elements",
            missionTime="PT0S",
            priority=1,
            location=ksc.id,
            container=ksc.id,
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
            location=ksc.id,
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
            location=ksc.id,
            edge=ksc_leo.id,
            elements=[
                ares_i_first_stage_1.id,
                ares_i_upper_stage_1.id,
                orion_cm_1.id,
                orion_sm_1.id,
                orion_las_1.id,
            ],
            burn_stage_sequence=[
                BurnStageSequence(
                    burn=ksc_leo.burns[0].id,
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
            location=ksc.id,
            container=ksc.id,
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
            location=ksc.id,
            container=altair_dm_1.id,
            elements=[cargo_1.id,],
        ),
        SpaceTransport(
            name="Lunar | Space Transport",
            missionTime="P1D",
            priority=3,
            location=ksc.id,
            edge=ksc_leo.id,
            elements=[
                altair_am_1.id,
                altair_dm_1.id,
                ares_v_core_1.id,
                ares_v_srbs_1.id,
                eds_1.id,
            ],
            burn_stage_sequence=[
                BurnStageSequence(
                    burn=ksc_leo.burns[0].id,
                    actions=[
                        BurnStageItem(type="Burn", element=ares_v_srbs_1.id),
                        BurnStageItem(type="Stage", element=ares_v_srbs_1.id),
                        BurnStageItem(type="Burn", element=ares_v_srbs_1.id),
                        BurnStageItem(type="Stage", element=ares_v_srbs_1.id),
                        BurnStageItem(type="Burn", element=eds_1.id),
                    ],
                )
            ],
        ),
        SpaceTransport(
            name="Lunar | Space Transport",
            missionTime="P2D",
            priority=1,
            location=leo.id,
            edge=leo_llpo.id,
            elements=[
                altair_am_1.id,
                altair_dm_1.id,
                eds_1.id,
                orion_cm_1.id,
                orion_sm_1.id,
            ],
            burn_stage_sequence=[
                BurnStageSequence(
                    burn=leo_llpo.burns[0].id,
                    actions=[
                        BurnStageItem(type="Burn", element=eds_1.id),
                        BurnStageItem(type="Stage", element=eds_1.id),
                    ],
                ),
                BurnStageSequence(
                    burn=leo_llpo.burns[1].id,
                    actions=[BurnStageItem(type="Burn", element=altair_dm_1.id),],
                ),
                BurnStageSequence(
                    burn=leo_llpo.burns[2].id,
                    actions=[BurnStageItem(type="Burn", element=altair_dm_1.id),],
                ),
                BurnStageSequence(
                    burn=leo_llpo.burns[3].id,
                    actions=[BurnStageItem(type="Burn", element=altair_dm_1.id),],
                ),
            ],
        ),
        MoveElements(
            name="Lunar | Move Elements",
            missionTime="P6D",
            priority=1,
            location=llpo.id,
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
            location=llpo.id,
            edge=llpo_lsp.id,
            elements=[altair_am_1.id, altair_dm_1.id,],
            burn_stage_sequence=[
                BurnStageSequence(
                    burn=llpo_lsp.burns[0].id,
                    actions=[BurnStageItem(type="Burn", element=altair_dm_1.id),],
                ),
                BurnStageSequence(
                    burn=llpo_lsp.burns[1].id,
                    actions=[BurnStageItem(type="Burn", element=altair_dm_1.id),],
                ),
            ],
        ),
        CrewedExploration(
            name="Lunar | Crewed Exploration",
            missionTime="P7DT12H",
            priority=1,
            location=lsp.id,
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
            location=lsp.id,
            container=altair_am_1.id,
            elements=[samples_1.id,],
        ),
        SpaceTransport(
            name="Lunar | Space Transport",
            missionTime="P14DT12H",
            priority=2,
            location=lsp.id,
            edge=lsp_llpo.id,
            elements=[altair_am_1.id],
            burn_stage_sequence=[
                BurnStageSequence(
                    burn=lsp_llpo.burns[0].id,
                    actions=[BurnStageItem(type="Burn", element=altair_am_1.id),],
                ),
                BurnStageSequence(
                    burn=lsp_llpo.burns[1].id,
                    actions=[BurnStageItem(type="Burn", element=altair_am_1.id),],
                ),
            ],
        ),
        MoveElements(
            name="Lunar | Move Elements",
            missionTime="P15D",
            priority=1,
            location=llpo.id,
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
            location=llpo.id,
            edge=llpo_pac.id,
            elements=[orion_cm_1.id, orion_sm_1.id],
            burn_stage_sequence=[
                BurnStageSequence(
                    burn=llpo_pac.burns[0].id,
                    actions=[BurnStageItem(type="Burn", element=orion_sm_1.id),],
                ),
                BurnStageSequence(
                    burn=llpo_pac.burns[1].id,
                    actions=[BurnStageItem(type="Burn", element=orion_sm_1.id),],
                ),
                BurnStageSequence(
                    burn=llpo_pac.burns[2].id,
                    actions=[BurnStageItem(type="Burn", element=orion_sm_1.id),],
                ),
                BurnStageSequence(
                    burn=llpo_pac.burns[3].id,
                    actions=[BurnStageItem(type="Burn", element=orion_sm_1.id),],
                ),
                BurnStageSequence(
                    burn=llpo_pac.burns[4].id,
                    actions=[BurnStageItem(type="Burn", element=orion_sm_1.id),],
                ),
                BurnStageSequence(
                    burn=llpo_pac.burns[5].id,
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
        nodes=[ksc, pac, leo, llpo, lsp],
        edges=[ksc_leo, leo_llpo, llpo_lsp, lsp_llpo, llpo_pac],
    ),
    mission_list=[lunar_sortie],
    resource_list=[pban_solid, lh2_lox, mmh_n2o4],
    element_templates=[
        altair_am,
        altair_dm,
        ares_i_first_stage,
        ares_i_upper_stage,
        ares_v_core,
        ares_v_srbs,
        crew_member,
        eds,
        samples,
        cargo,
        orion_cm,
        orion_las,
        orion_sm,
    ],
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
    demand_models=[],
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
