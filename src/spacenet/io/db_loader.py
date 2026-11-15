"""
Methods to load data from a spreadsheet (Excel) file database.
"""

from datetime import timedelta
from typing import BinaryIO, List

import numpy as np
import pandas as pd
from fastapi_camelcase import CamelModel
from pydantic import Field, ValidationError

from .. import schemas as s
from ..schemas.elements.element import ElementType


def _parse_node(data: dict) -> s.AllNodes:
    """
    Helper function to manage node polymorphism.

    Args:
        data (dict): the node in dictionary format

    Returns:
        AllNodes: the node in SpaceNet format
    """
    # loop through candidate model classes
    for model_cls in [s.SurfaceNode, s.OrbitalNode, s.LagrangeNode]:
        try:
            return model_cls(**data)
        except ValidationError:
            pass
    raise ValueError("No valid node type found")


def _parse_edge(data: dict) -> s.AllEdges:
    """
    Helper function to manage edge polymorphism.

    Args:
        data (dict): the edge in dictionary format

    Returns:
        AllEdges: the edge in SpaceNet format
    """
    # loop through candidate model classes
    for model_cls in [s.SurfaceEdge, s.SpaceEdge, s.FlightEdge]:
        try:
            return model_cls(**data)
        except ValidationError:
            pass
    raise ValueError("No valid edge type found for " + str(data))


def _parse_resource(data: dict) -> s.AllResources:
    """
    Helper function to manage resource polymorphism.

    Args:
        data (dict): the resource in dictionary format

    Returns:
        AllResources: the resource in SpaceNet format
    """
    # fix `description` null value
    if pd.isna(data["description"]):
        data["description"] = None
    # loop through candidate model classes
    for model_cls in [s.ContinuousResource, s.DiscreteResource]:
        try:
            return model_cls(**data)
        except ValidationError:
            pass
    raise ValueError("No valid resource found for " + str(data))


def _parse_element(data: dict) -> s.AllElements:
    """
    Helper function to manage element polymorphism.

    Args:
        data (dict): the element in dictionary format

    Returns:
        AllElements: the element in SpaceNet format
    """
    # fix `current_state_index` null value
    if pd.isna(data["current_state_index"]):
        data["current_state_index"] = None
    # loop through candidate model classes
    for model_cls in [
        s.Element,
        s.ResourceContainer,
        s.ElementCarrier,
        s.HumanAgent,
        s.RoboticAgent,
        s.PropulsiveVehicle,
        s.SurfaceVehicle,
    ]:
        try:
            return model_cls(**data)
        except ValidationError:
            pass
    raise ValueError("No valid element found for " + str(data))


def _parse_demand_model(
    data: dict,
) -> s.AllElementDemandModels:
    """
    Helper function to manage demand model polymorphism.

    Args:
        data (dict): the demand model in dictionary format

    Returns:
        AllElementDemandModels: the demand model in SpaceNet format
    """
    # loop through candidate model classes
    for model_cls in [
        s.TimedImpulseDemandModel,
        s.RatedDemandModel,
        s.SparingByMassDemandModel,
    ]:
        try:
            return model_cls(**data)
        except ValidationError:
            pass
    raise ValueError("No valid demand model found for " + str(data))


class ModelDatabase(CamelModel):
    """
    Database stores models for nodes, edges, resources, demand models, and elements.
    """

    nodes: List[s.AllNodes] = Field([], description="List of nodes")
    edges: List[s.AllEdges] = Field([], description="List of edges")
    resources: List[s.AllResources] = Field([], description="List of resources")
    demand_models: List[s.AllElementDemandModels] = Field(
        [], description="List of demand models"
    )
    elements: List[s.AllElements] = Field([], description="List of elements")

    def get_node(self, name: str) -> s.AllNodes:
        """
        Gets the node matching a given name.

        Args:
            name (str): the node name

        Returns:
            str: The matchine node if it exsits, otherwise `None`.
        """
        return next(filter(lambda o: o.name == name, self.nodes))

    def get_edge(self, name: str) -> s.AllEdges:
        """
        Gets the edge matching a given name.

        Args:
            name (str): the edge name

        Returns:
            str: The matchine edge if it exsits, otherwise `None`.
        """
        return next(filter(lambda o: o.name == name, self.edges))

    def get_resource(self, name):
        """
        Gets the resource matching a given name.

        Args:
            name (str): the resource name

        Returns:
            str: The matchine resource if it exsits, otherwise `None`.
        """
        return next(filter(lambda o: o.name == name, self.resources))

    def instantiate_element(
        self, cls, template_name: str, prefix: str = None, suffix: str = None
    ) -> s.AllInstElements:
        """
        Instantiates an element for a given template.

        Args:
            cls: the element class
            template_name (str): the template name
            prefix (str, Optional): the prefix to apply before the instance name
            suffix (str, Optional): the suffix to apply after the instance name

        Returns:
            s.AllInstElements: An instantiated element.
        """
        return cls(
            template_id=next(
                filter(lambda o: o.name == template_name, self.elements)
            ).id,
            name=(prefix + " | " if prefix is not None else "")
            + next(filter(lambda o: o.name == template_name, self.elements)).name
            + (" " + suffix if suffix is not None else ""),
        )


def load_db(db_file: BinaryIO) -> ModelDatabase:
    """
    Loads a database from file (Excel).

    Args:
        db_file (BinaryIO): the database file object

    Returns:
        ModelDatabase: the model database
    """
    # pylint: disable=too-many-statements
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
            lambda r: s.Burn(
                time=timedelta(days=r.time),
                delta_v=r.delta_v,
                # the propulsion type of a burn is optional (default: OMS)
                type=(
                    r.type
                    if "type" in burns.columns and pd.notna(r.type)
                    else s.PropulsionType.OMS
                ),
            ),
            axis=1,
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
            lambda r: s.ResourceAmount(
                resource=resources[resources.id == r.resource_id].iloc[0].model.id,
                amount=r.amount,
            )
            if r.resource_id > 0 and pd.notna(r.amount)
            else s.ResourceAmountRate(
                resource=resources[resources.id == r.resource_id].iloc[0].model.id,
                rate=r.rate,
            )
            if r.resource_id > 0 and pd.notna(r.rate)
            else s.GenericResourceAmount(
                class_of_supply=-r.resource_id,
                environment=s.Environment.UNPRESSURIZED,
                amount=r.amount,
            )
            if pd.notna(r.amount)
            else s.GenericResourceAmountRate(
                class_of_supply=-r.resource_id,
                environment=s.Environment.UNPRESSURIZED,
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
            lambda r: s.Part(
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
                s.InstTimedImpulseDemandModel(name=m.name, template_id=m.id)
                if m.type == s.DemandModelType.TIMED_IMPULSE
                else s.InstRatedDemandModel(name=m.name, template_id=m.id)
                if m.type == s.DemandModelType.RATED
                else s.InstSparingByMassDemandModel(name=m.name, template_id=m.id)
                for m in demand_models[demand_models.state_id == i].model.to_list()
            ]
        )
        if not states.empty
        else None
    )
    # parse the states, dropping the `id` field to generate a new uuid
    states["model"] = (
        states.drop("id", axis=1).apply(lambda r: s.State(**r.to_dict()), axis=1)
        if not states.empty
        else None
    )

    # read the resource contents sheet
    contents = pd.read_excel(db_file, "contents")
    # parse the contents
    contents["model"] = (
        contents.apply(
            lambda r: s.ResourceAmount(
                resource=resources[resources.id == r.resource_id].iloc[0].model.id,
                amount=r.amount,
            )
            if r.resource_id > 0
            else s.GenericResourceAmount(
                class_of_supply=-r.resource_id,
                environment=s.Environment.UNPRESSURIZED,
                amount=r.amount,
            ),
            axis=1,
        )
        if not contents.empty
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
    # add the `contents` field
    elements["contents"] = (
        elements.id.apply(
            lambda i: contents[contents.container_id == i].model.to_list()
        )
        if not elements.empty
        else None
    )
    # coerce `max_crew` to an integer data type
    elements["max_crew"] = elements.max_crew.astype("Int64")
    # add the `current_state_index` field
    elements["current_state_index"] = (
        elements.apply(
            lambda r: np.where(states[states.element_id == r.id].initial_state)[0][0]
            if not (states[(states.element_id == r.id) & (states.initial_state)].empty)
            else None,
            axis=1,
        )
        if not (elements.empty or states.empty)
        else None
    )
    # coerce `current_state_index` to an integer data type
    elements["current_state_index"] = elements.current_state_index.astype("Int64")

    def get_value(row, column: str, default=None):
        # gets the value of an optional column
        value = row.get(column)
        return default if value is None or pd.isna(value) else value

    def parse_tank(row, max_column: str, id_column: str) -> s.ResourceTank:
        # parses a (full) fuel tank; a positive resource id refers to the
        # resources sheet and a negative id to a generic class of supply
        amount = get_value(row, max_column, 0.0)
        resource_id = get_value(row, id_column)
        if resource_id is None:
            return None
        return s.ResourceTank(
            max_amount=amount,
            contents=s.ResourceAmount(
                resource=resources[resources.id == resource_id].iloc[0].model.id,
                amount=amount,
            )
            if resource_id > 0
            else s.GenericResourceAmount(
                class_of_supply=-resource_id,
                environment=s.Environment.UNPRESSURIZED,
                amount=amount,
            ),
        )

    def parse_propulsion_systems(row) -> List[s.PropulsionSystem]:
        # parses the orbital maneuvering system (`oms_isp`, `max_oms`, and
        # `oms_id` columns) and the reaction control system (`rcs_isp`,
        # `max_rcs`, and `rcs_id` columns) of a propulsive vehicle
        if row.type != ElementType.PROPULSIVE_VEHICLE.value:
            return None
        systems = []
        oms_tank = parse_tank(row, "max_oms", "oms_id")
        if get_value(row, "oms_isp", 0) > 0 and oms_tank is not None:
            systems.append(
                s.PropulsionSystem(
                    type=s.PropulsionType.OMS, isp=row.oms_isp, fuel_tank=oms_tank
                )
            )
        rcs_tank = parse_tank(row, "max_rcs", "rcs_id")
        if get_value(row, "rcs_isp", 0) > 0:
            if rcs_tank is not None and rcs_tank.max_amount > 0:
                systems.append(
                    s.PropulsionSystem(
                        type=s.PropulsionType.RCS, isp=row.rcs_isp, fuel_tank=rcs_tank
                    )
                )
            elif systems:
                # without a fuel tank the RCS shares the fuel tank of the OMS
                systems.append(
                    s.PropulsionSystem(
                        type=s.PropulsionType.RCS,
                        isp=row.rcs_isp,
                        shared_fuel_tank=s.PropulsionType.OMS,
                    )
                )
        if not systems:
            # a single propulsion system (`isp`, `max_fuel`, and `fuel_id` columns)
            tank = parse_tank(row, "max_fuel", "fuel_id")
            if tank is None:
                raise ValueError(f"No propulsion system found for {row['name']}")
            systems.append(
                s.PropulsionSystem(
                    type=s.PropulsionType.OMS,
                    isp=get_value(row, "isp", 0.0),
                    fuel_tank=tank,
                )
            )
        return systems

    # add the `propulsion_systems` field (propulsive vehicles)
    elements["propulsion_systems"] = (
        elements.apply(parse_propulsion_systems, axis=1) if not elements.empty else None
    )
    # add the `fuel_tank` field (surface vehicles)
    elements["fuel_tank"] = (
        elements.apply(
            lambda r: parse_tank(r, "max_fuel", "fuel_id")
            if r.type == ElementType.SURFACE_VEHICLE.value
            else None,
            axis=1,
        )
        if not elements.empty
        else None
    )
    # parse the elements, dropping the `id` field to generate a new uuid
    elements["model"] = (
        elements.drop("id", axis=1).apply(lambda r: _parse_element(r.to_dict()), axis=1)
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
