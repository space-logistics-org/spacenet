"""
Exports demands and manifests as delimited text.
"""

import csv
import io
from typing import Iterable, List

from ..manifest import SimManifest
from ..simulator import DemandSimulator
from .propellant import PropellantAnalysis

#: Manifest export with one row for each packed demand.
LEVEL_DEMANDS = "demands"
#: Manifest export with one row for each container.
LEVEL_CONTAINERS = "containers"
#: Manifest export with one row for each carrier.
LEVEL_CARRIERS = "carriers"
#: Manifest export with one row for each transport.
LEVEL_EDGES = "edges"


def _write(header: List[str], rows: Iterable[list], delimiter: str) -> str:
    buffer = io.StringIO()
    writer = csv.writer(buffer, delimiter=delimiter, lineterminator="\n")
    writer.writerow(header)
    writer.writerows(rows)
    return buffer.getvalue()


def export_raw_demands(simulator: DemandSimulator, delimiter: str = ",") -> str:
    """
    Exports the demands logged by an executed demand simulator with one row
    for each demanded resource.

    Args:
        simulator (:obj:`DemandSimulator`): The demand simulator.
        delimiter (str): The column delimiter.

    Returns:
        str: The delimited text.
    """
    rows = []
    for sim_demand in simulator.unsatisfied_demands:
        for demand in sim_demand.demands:
            rows.append(
                [
                    sim_demand.time,
                    "" if sim_demand.location is None else sim_demand.location.name,
                    "" if sim_demand.element is None else sim_demand.element.name,
                    demand.resource.name,
                    demand.amount,
                    demand.resource.units,
                    demand.mass,
                ]
            )
    return _write(
        ["Time", "Location", "Element", "Resource", "Amount", "Units", "Mass (kg)"],
        rows,
        delimiter,
    )


def export_aggregated_demands(simulator: DemandSimulator, delimiter: str = ",") -> str:
    """
    Exports the demands aggregated by an executed demand simulator. The
    demands of each transport (between two times and nodes) are followed by
    the demands at its arrival (one time and node).

    Args:
        simulator (:obj:`DemandSimulator`): The demand simulator.
        delimiter (str): The column delimiter.

    Returns:
        str: The delimited text.
    """
    node_demands = {id(p): d for p, d in simulator.aggregated_node_demands}
    rows = []
    for edge, demands in simulator.aggregated_edge_demands:
        for demand in demands:
            rows.append(
                [
                    edge.start_time,
                    edge.end_time,
                    edge.origin.name,
                    edge.destination.name,
                    demand.resource.name,
                    demand.amount,
                    demand.resource.units,
                    demand.mass,
                ]
            )
        for demand in node_demands.pop(id(edge.point), []):
            rows.append(
                [
                    edge.end_time,
                    edge.end_time,
                    edge.destination.name,
                    edge.destination.name,
                    demand.resource.name,
                    demand.amount,
                    demand.resource.units,
                    demand.mass,
                ]
            )
    return _write(
        [
            "Time 1",
            "Time 2",
            "Node 1",
            "Node 2",
            "Resource",
            "Amount",
            "Units",
            "Mass (kg)",
        ],
        rows,
        delimiter,
    )


def export_manifest(
    manifest: SimManifest, level: str = LEVEL_DEMANDS, delimiter: str = ","
) -> str:
    """
    Exports the containers loaded on transports at a level of aggregation:
    packed demands, containers, carriers, or transports.

    Args:
        manifest (:obj:`SimManifest`): The manifest.
        level (str): The level of aggregation.
        delimiter (str): The column delimiter.

    Returns:
        str: The delimited text.
    """
    # pylint: disable=protected-access,too-many-locals
    if level not in (LEVEL_DEMANDS, LEVEL_CONTAINERS, LEVEL_CARRIERS, LEVEL_EDGES):
        raise ValueError(f"Invalid manifest export level {level}")
    transport = ["Origin", "Departure", "Destination", "Arrival"]
    rows = []
    for edge in sorted(manifest.edges, key=lambda e: e.start_time):
        point = manifest._canonical_point(edge.point)
        edge_row = [
            edge.origin.name,
            edge.start_time,
            edge.destination.name,
            edge.end_time,
        ]
        edge_mass = 0.0
        edge_volume = 0.0
        edge_count = 0
        for carrier in edge.all_carriers:
            carrier_row = edge_row + [
                carrier.name,
                carrier.cargo_environment,
                carrier.max_cargo_mass - carrier.cargo_mass,
                carrier.max_cargo_volume - carrier.cargo_volume,
            ]
            carrier_mass = 0.0
            carrier_volume = 0.0
            containers = manifest.get_loaded_containers(edge, carrier.id)
            for container in containers:
                items = manifest.get_packed_items(container, point)
                packed_mass = sum(i.mass for i in items)
                packed_volume = sum(i.volume for i in items)
                carrier_mass += container.mass + packed_mass
                carrier_volume += container.volume
                container_row = carrier_row + [
                    container.name,
                    container.environment.value,
                    container.mass,
                    container.volume,
                    container.cargo_environment.value,
                    container.max_cargo_mass,
                    container.max_cargo_volume,
                ]
                if level == LEVEL_CONTAINERS:
                    rows.append(container_row + [packed_mass, packed_volume])
                elif level == LEVEL_DEMANDS:
                    for item in items:
                        resource = item.demand.resource
                        rows.append(
                            container_row
                            + [
                                resource.name,
                                resource.environment.value,
                                item.amount,
                                resource.units,
                                item.mass,
                                item.volume,
                            ]
                        )
            edge_mass += carrier_mass
            edge_volume += carrier_volume
            edge_count += len(containers)
            if level == LEVEL_CARRIERS:
                rows.append(
                    carrier_row + [len(containers), carrier_mass, carrier_volume]
                )
        if level == LEVEL_EDGES:
            rows.append(edge_row + [edge_count, edge_mass, edge_volume])
    carrier = [
        "Carrier",
        "Cargo Environment",
        "Cargo Mass Available (kg)",
        "Cargo Volume Available (m^3)",
    ]
    container = [
        "Container",
        "Environment",
        "Mass (kg)",
        "Volume (m^3)",
        "Container Cargo Environment",
        "Container Max Cargo Mass (kg)",
        "Container Max Cargo Volume (m^3)",
    ]
    if level == LEVEL_EDGES:
        header = transport + [
            "Containers",
            "Manifested Mass (kg)",
            "Manifested Volume (m^3)",
        ]
    elif level == LEVEL_CARRIERS:
        header = (
            transport
            + carrier
            + ["Containers", "Manifested Mass (kg)", "Manifested Volume (m^3)"]
        )
    elif level == LEVEL_CONTAINERS:
        header = (
            transport
            + carrier
            + container
            + ["Packed Mass (kg)", "Packed Volume (m^3)"]
        )
    else:
        header = (
            transport
            + carrier
            + container
            + [
                "Resource",
                "Resource Environment",
                "Amount",
                "Units",
                "Resource Mass (kg)",
                "Resource Volume (m^3)",
            ]
        )
    return _write(header, rows, delimiter)


def export_propellant(analysis: PropellantAnalysis, delimiter: str = ",") -> str:
    """
    Exports the propellant budget of each integral tank of each vehicle.

    Args:
        analysis (:obj:`PropellantAnalysis`): The propellant analysis.
        delimiter (str): The column delimiter.

    Returns:
        str: The delimited text.
    """
    fields = [
        ("Loaded", "loaded"),
        ("Added", "added"),
        ("Transferred In", "transferred_in"),
        ("Transferred Out", "transferred_out"),
        ("Transfer Loss", "transfer_loss"),
        ("Burned", "burned"),
        ("Boiloff", "boiloff"),
        ("Consumed", "consumed"),
        ("Residual", "residual"),
    ]
    rows = [
        [
            budget.vehicle_name,
            budget.tank,
            budget.resource or "",
            budget.unit_mass,
            budget.max_amount,
            *(getattr(budget, name) for _, name in fields),
        ]
        for budget in analysis.budgets
    ]
    return _write(
        ["Vehicle", "Tank", "Resource", "Unit Mass (kg)", "Capacity (units)"]
        + [f"{label} (units)" for label, _ in fields],
        rows,
        delimiter,
    )
