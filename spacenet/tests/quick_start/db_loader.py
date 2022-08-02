from spacenet.schemas import *
from pydantic import ValidationError
from typing import Union, List

import pandas as pd
import numpy as np
from pydantic import BaseModel, Field
from datetime import timedelta


def _parse_node(data: dict) -> Union[SurfaceNode, OrbitalNode, LagrangeNode]:
    """
    Helper function to manage node polymorphism.

    Args:
        data (dict): the node in dictionary format

    Returns:
        Union[SurfaceNode, OrbitalNode, LagrangeNode]: the node in SpaceNet format
    """
    # loop through candidate model classes
    for model_cls in [SurfaceNode, OrbitalNode, LagrangeNode]:
        try:
            return model_cls(**data)
        except ValidationError as e:
            pass
    raise ValueError("No valid node type found")


def _parse_edge(data: dict) -> Union[SurfaceEdge, SpaceEdge, FlightEdge]:
    """
    Helper function to manage edge polymorphism.

    Args:
        data (dict): the edge in dictionary format

    Returns:
        Union[SurfaceEdge, SpaceEdge, FlightEdge]: the edge in SpaceNet format
    """
    # loop through candidate model classes
    for model_cls in [SurfaceEdge, SpaceEdge, FlightEdge]:
        try:
            return model_cls(**data)
        except ValidationError as e:
            pass
    raise ValueError("No valid edge type found for " + str(data))


def _parse_resource(data: dict) -> Union[ContinuousResource, DiscreteResource]:
    """
    Helper function to manage resource polymorphism.

    Args:
        data (dict): the resource in dictionary format

    Returns:
        Union[ContinuousResource, DiscreteResource]: the resource in SpaceNet format
    """
    # fix `description` null value
    if pd.isna(data["description"]):
        data["description"] = None
    # loop through candidate model classes
    for model_cls in [ContinuousResource, DiscreteResource]:
        try:
            return model_cls(**data)
        except ValidationError as e:
            pass
    raise ValueError("No valid resource found for " + str(data))


def _parse_element(
    data: dict,
) -> Union[
    Element,
    CargoCarrier,
    ResourceContainer,
    ElementCarrier,
    HumanAgent,
    RoboticAgent,
    PropulsiveVehicle,
    SurfaceVehicle,
]:
    """
    Helper function to manage element polymorphism.

    Args:
        data (dict): the element in dictionary format

    Returns:
        Union[Element, CargoCarrier, ResourceContainer, ElementCarrier, HumanAgent, RoboticAgent, PropulsiveVehicle, SurfaceVehicle]: the element in SpaceNet format
    """
    # fix `current_state_index` null value
    if pd.isna(data["current_state_index"]):
        data["current_state_index"] = None
    # loop through candidate model classes
    for model_cls in [
        Element,
        CargoCarrier,
        ResourceContainer,
        ElementCarrier,
        HumanAgent,
        RoboticAgent,
        PropulsiveVehicle,
        SurfaceVehicle,
    ]:
        try:
            return model_cls(**data)
        except ValidationError as e:
            pass
    raise ValueError("No valid element found for " + str(data))


def _parse_demand_model(
    data: dict,
) -> Union[TimedImpulseDemandModel, RatedDemandModel, SparingByMassDemandModel]:
    """
    Helper function to manage demand model polymorphism.

    Args:
        data (dict): the demand model in dictionary format

    Returns:
        Union[TimedImpulseDemandModel, RatedDemandModel, SparingByMassDemandModel]: the demand model in SpaceNet format
    """
    # loop through candidate model classes
    for model_cls in [
        TimedImpulseDemandModel,
        RatedDemandModel,
        SparingByMassDemandModel,
    ]:
        try:
            return model_cls(**data)
        except ValidationError as e:
            pass
    raise ValueError("No valid demand model found for " + str(data))


class ModelDatabase(BaseModel):
    """
    Database stores models for nodes, edges, resources, demand models, and elements.
    """

    nodes: List[Union[SurfaceNode, OrbitalNode, LagrangeNode]] = Field(
        [], description="List of nodes"
    )
    edges: List[Union[SurfaceEdge, SpaceEdge, FlightEdge]] = Field(
        [], description="List of edges"
    )
    resources: List[Union[ContinuousResource, DiscreteResource]] = Field(
        [], description="List of resources"
    )
    demand_models: List[
        Union[TimedImpulseDemandModel, RatedDemandModel, SparingByMassDemandModel]
    ] = Field([], description="List of demand models")
    elements: List[
        Union[
            Element,
            CargoCarrier,
            ResourceContainer,
            ElementCarrier,
            HumanAgent,
            RoboticAgent,
            PropulsiveVehicle,
            SurfaceVehicle,
        ]
    ] = Field([], description="List of elements")


def load_db(file_name: str) -> ModelDatabase:
    """
    Loads a database from file (Excel).

    Args:
        file_name (str): the database file

    Returns:
        ModelDatabase: the model database
    """
    # open the database file
    with open(file_name, "rb") as db_file:
        # read the nodes sheet
        nodes = pd.read_excel(db_file, "nodes")
        # parse the nodes, dropping the `id` field to generate a new uuid
        nodes["model"] = (
            nodes.drop("id", axis=1).apply(lambda r: _parse_node(r.to_dict()), axis=1)
            if not nodes.empty
            else None
        )

        # read the burns sheet
        burns = pd.read_excel(db_file, "burns")
        # parse the burns
        burns["model"] = (
            burns.apply(
                lambda r: Burn(time=timedelta(days=r.time), delta_v=r.delta_v), axis=1
            )
            if not burns.empty
            else None
        )

        # read the edges sheet
        edges = pd.read_excel(db_file, "edges")
        # add the `origin` field by matching with node ids
        edges["origin"] = (
            edges.origin_id.apply(lambda i: nodes[nodes.id == i].iloc[0].model.id)
            if not edges.empty
            else None
        )
        # add the `destination` field by matching with node ids
        edges["destination"] = (
            edges.destination_id.apply(lambda i: nodes[nodes.id == i].iloc[0].model.id)
            if not edges.empty
            else None
        )
        # convert the numeric duration (in days) to a Python timedelta
        edges["duration"] = edges.duration.apply(lambda i: timedelta(days=i))
        # add the `burns` field by matching with burn edge_ids
        edges["burns"] = (
            edges.id.apply(lambda i: burns[burns.edge_id == i].model.to_list())
            if not (edges.empty or burns.empty)
            else None
        )
        # parse the edges, dropping the `id` field to generate a new uuid
        edges["model"] = (
            edges.drop("id", axis=1).apply(lambda r: _parse_edge(r.to_dict()), axis=1)
            if not edges.empty
            else None
        )

        # read the resources sheet
        resources = pd.read_excel(db_file, "resources")
        # parse the resources, dropping the `id` field to generate a new uuid
        resources["model"] = (
            resources.drop("id", axis=1).apply(
                lambda r: _parse_resource(r.to_dict()), axis=1
            )
            if not resources.empty
            else None
        )

        # read the demands sheet
        demands = pd.read_excel(db_file, "demands")
        # parse the demands
        demands["model"] = (
            demands.apply(
                lambda r: ResourceAmount(
                    resource=resources[resources.id == r.resource_id].iloc[0].model.id,
                    amount=r.amount,
                )
                if r.resource_id > 0 and pd.notna(r.amount)
                else ResourceAmountRate(
                    resource=resources[resources.id == r.resource_id].iloc[0].model.id,
                    rate=r.rate,
                )
                if r.resource_id > 0 and pd.notna(r.rate)
                else GenericResourceAmount(
                    class_of_supply=-r.resource_id,
                    environment=Environment.Unpressurized,
                    amount=r.amount,
                ) if pd.notna(r.amount)
                else GenericResourceAmountRate(
                    class_of_supply=-r.resource_id,
                    environment=Environment.Unpressurized,
                    rate=r.rate,
                ),
                axis=1,
            )
            if not demands.empty
            else None
        )

        # read the demand models sheet
        demand_models = pd.read_excel(db_file, "demand_models")
        # add the `demands` field by matching with demand `demand_model_id`
        demand_models["demands"] = (
            demand_models.id.apply(
                lambda i: demands[demands.demand_model_id == i].model.to_list()
            )
            if not demand_models.empty
            else None
        )
        # parse the demand models, dropping the `id` field to generate a new uuid
        demand_models["model"] = (
            demand_models.drop("id", axis=1).apply(
                lambda r: _parse_demand_model(r.to_dict()), axis=1
            )
            if not demand_models.empty
            else None
        )

        # read the parts sheet
        parts = pd.read_excel(db_file, "parts")
        # parse the parts
        parts["model"] = (
            parts.apply(
                lambda r: Part(
                    resource=resources[resources.id == r.resource_id].iloc[0].model.id,
                    mean_time_to_failure=timedelta(hours=float(r.mean_time_to_failure))
                    if r.mean_time_to_failure > 0
                    else None,
                    mean_time_to_repair=timedelta(hours=float(r.mean_time_to_repair))
                    if r.mean_time_to_repair > 0
                    else None,
                    mass_to_repair=r.mass_to_repair,
                    quantity=r.quantity,
                    duty_cycle=r.duty_cycle,
                ),
                axis=1,
            )
            if not parts.empty
            else None
        )

        # read the states sheet
        states = pd.read_excel(db_file, "states")
        # add the `demand_models` field
        states["demand_models"] = (
            states.id.apply(
                lambda i: [
                    InstTimedImpulseDemandModel(name=m.name, template_id=m.id) if m.type==DemandModelType.TimedImpulse
                    else InstRatedDemandModel(name=m.name, template_id=m.id) if m.type==DemandModelType.Rated
                    else InstSparingByMassDemandModel(name=m.name, template_id=m.id)
                    for m in demand_models[demand_models.state_id == i].model.to_list()
                ]
            )
            if not states.empty
            else None
        )
        # parse the states, dropping the `id` field to generate a new uuid
        states["model"] = (
            states.drop("id", axis=1).apply(lambda r: State(**r.to_dict()), axis=1)
            if not states.empty
            else None
        )

        # read the elements sheet
        elements = pd.read_excel(db_file, "elements")
        # add the `parts` field
        elements["parts"] = (
            elements.id.apply(lambda i: parts[parts.element_id == i].model.to_list())
            if not elements.empty
            else None
        )
        # add the `states` field
        elements["states"] = (
            elements.id.apply(lambda i: states[states.element_id == i].model.to_list())
            if not elements.empty
            else None
        )
        # coerce `max_crew` to an integer data type
        elements["max_crew"] = elements.max_crew.astype("Int64")
        # add the `current_state_index` field
        elements["current_state_index"] = (
            elements.apply(
                lambda r: np.where(
                    states[states.element_id == r.id].initial_state == True
                )[0][0]
                if not (
                    states[
                        (states.element_id == r.id) & (states.initial_state == True)
                    ].empty
                )
                else None,
                axis=1,
            )
            if not (elements.empty or states.empty)
            else None
        )
        # coerce `current_state_index` to an integer data type
        elements["current_state_index"] = elements.current_state_index.astype("Int64")
        # add the `fuel` field
        elements["fuel"] = (
            elements.apply(
                lambda r: ResourceAmount(
                    resource=resources[resources.id == r.fuel_id].iloc[0].model.id,
                    amount=r.max_fuel,
                )
                if pd.notna(r.fuel_id) and r.fuel_id > 0
                else GenericResourceAmount(
                    class_of_supply=-r.fuel_id,
                    environment=Environment.Unpressurized,
                    amount=r.max_fuel,
                )
                if pd.notna(r.fuel_id)
                else None,
                axis=1,
            )
            if not elements.empty
            else None
        )
        # parse the elements, dropping the `id` field to generate a new uuid
        elements["model"] = (
            elements.drop("id", axis=1).apply(
                lambda r: _parse_element(r.to_dict()), axis=1
            )
            if not elements.empty
            else None
        )

    return ModelDatabase(
        nodes=nodes.model.to_list(),
        edges=edges.model.to_list(),
        resources=resources.model.to_list(),
        demand_models=demand_models.model.to_list(),
        elements=elements.model.to_list(),
    )
