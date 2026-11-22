"""
Normalizes the demand and manifest analyses of the reference (Java) and
Python implementations to a common, compact form for comparison.

Objects are identified by name (the reference implementation reports integer
identifiers) and amounts are rounded; lists are sorted so that the order in
which each implementation reports results does not matter.
"""

from collections import defaultdict
from typing import Any, Dict, List

#: Decimal places of rounded times and amounts.
DIGITS = 6

#: Decimal places of rounded container masses (the reference implementation
#: reports container masses rounded to the mass precision of 0.01 kg).
MASS_DIGITS = 2


def _round(value: float, digits: int = DIGITS) -> float:
    # adding 0.0 avoids distinguishing -0.0 from 0.0
    return round(value, digits) + 0.0


def _name(reference) -> str:
    # an empty name (rather than None) keeps the normalized lists sortable
    return "" if reference is None else reference["name"]


def _resources(items: List[dict]) -> List[list]:
    return sorted([r["resource"]["name"], _round(r["amount"])] for r in items)


def raw_demands(analysis: dict) -> List[list]:
    """Normalizes a raw demands analysis (JSON) of either implementation."""
    return sorted(
        [
            _round(d["time"]),
            _name(d.get("location")),
            _name(d.get("element")),
            _resources(d["consumption"]),
            _resources(d["production"]),
        ]
        for d in analysis["demands"]
    )


def aggregated_demands(analysis: dict) -> Dict[str, List[list]]:
    """Normalizes an aggregated demands analysis (JSON) of either implementation."""
    return {
        "nodes": sorted(
            [
                _round(d["time"]),
                _name(d["location"]),
                _resources(d["consumption"]),
                _resources(d["production"]),
            ]
            for d in analysis["nodes"]
        ),
        "edges": sorted(
            [
                _round(d["startTime"]),
                _round(d["endTime"]),
                _name(d["origin"]),
                _name(d["destination"]),
                _name(d["location"]),
                _resources(d["consumption"]),
                _resources(d["production"]),
                _round(d["maxCargoMass"]),
                _round(d["netCargoMass"]),
            ]
            for d in analysis["edges"]
        ),
    }


def _manifest(containers: List[list], transports: Dict[tuple, float]) -> Dict[str, Any]:
    packed = defaultdict(float)
    for _, _, items in containers:
        for name, amount, node, time in items:
            packed[(name, node, time)] += amount
    return {
        "packed": sorted([*key, _round(amount, 4)] for key, amount in packed.items()),
        "containers": sorted(containers),
        "transports": sorted(
            [*key, _round(mass, MASS_DIGITS)] for key, mass in transports.items()
        ),
    }


def java_manifest(analysis: dict) -> Dict[str, Any]:
    """
    Normalizes the auto-manifest analysis (JSON) of the reference
    implementation to the packed amount of each resource at each supply
    point, the contents of each container, and the mass manifested on each
    transport (by departure time and origin).
    """
    containers = [
        [
            _round(c["mass"], MASS_DIGITS),
            _round(c["maxCargoMass"], MASS_DIGITS),
            sorted(
                [
                    d["resource"]["name"],
                    _round(d["amount"]),
                    d["node"]["name"],
                    _round(d["time"]),
                ]
                for d in c["packedDemands"]
            ),
        ]
        for c in analysis["containers"]
        if c["packedDemands"]
    ]
    transports = defaultdict(float)
    for action in analysis["actions"]:
        key = (_round(action["time"]), action["node"]["name"])
        transports[key] += sum(c["manifestedMass"] for c in action["carriers"])
    return _manifest(containers, transports)


def python_manifest(manifest) -> Dict[str, Any]:
    """
    Normalizes an automatically packed and loaded :class:`SimManifest` in
    the same way as :func:`java_manifest`.
    """
    containers = [
        [
            _round(c.mass, MASS_DIGITS),
            _round(c.max_cargo_mass, MASS_DIGITS),
            sorted(
                [
                    i.demand.resource.name,
                    _round(i.amount),
                    i.demand.point.node.name,
                    _round(i.demand.point.time),
                ]
                for i in c.items
            ),
        ]
        for c in manifest.containers
        if c.items
    ]
    transports = defaultdict(float)
    for edge in manifest.edges:
        key = (_round(edge.start_time), edge.origin.name)
        transports[key] += sum(
            c.mass + manifest.get_container_cargo_mass(c)
            for carrier in edge.carriers
            for c in manifest.get_loaded_containers(edge, carrier.id)
        )
    return _manifest(containers, transports)
