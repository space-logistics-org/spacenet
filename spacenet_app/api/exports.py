"""
Endpoints to export demands and manifests as delimited text.
"""

from fastapi import APIRouter
from fastapi.responses import Response

from spacenet.simulation import (
    DemandsAnalysis,
    FullSimulator,
    PropellantAnalysis,
    SimManifest,
)
from spacenet.simulation.analysis import (
    export_aggregated_demands,
    export_manifest,
    export_propellant,
    export_raw_demands,
)

from .models import ExportRequest

router = APIRouter()


def _respond(text: str, name: str, delimiter: str) -> Response:
    extension = "csv" if delimiter == "," else "txt"
    return Response(
        content=text,
        media_type="text/csv" if delimiter == "," else "text/plain",
        headers={"Content-Disposition": f'attachment; filename="{name}.{extension}"'},
    )


def _simulate(request: ExportRequest):
    return DemandsAnalysis.simulate(
        request.scenario,
        estimate_container_masses=request.options.estimate_container_masses,
        consume_existing_resources=request.options.consume_existing_resources,
    )


@router.post("/demands/raw", response_class=Response)
def export_raw(request: ExportRequest):
    """
    Exports the logged demands of a scenario.
    """
    text = export_raw_demands(_simulate(request), request.delimiter)
    return _respond(text, "demands", request.delimiter)


@router.post("/demands/aggregated", response_class=Response)
def export_aggregated(request: ExportRequest):
    """
    Exports the demands of a scenario aggregated to transports.
    """
    text = export_aggregated_demands(_simulate(request), request.delimiter)
    return _respond(text, "aggregated_demands", request.delimiter)


@router.post("/manifest", response_class=Response)
def export_scenario_manifest(request: ExportRequest):
    """
    Exports the manifest of a scenario at a level of aggregation.
    """
    manifest = SimManifest.create(request.scenario)
    text = export_manifest(manifest, request.level, request.delimiter)
    return _respond(text, "manifest", request.delimiter)


@router.post("/propellant", response_class=Response)
def export_propellant_budgets(request: ExportRequest):
    """
    Exports the propellant budget of each vehicle tank of a scenario.
    """
    simulator = FullSimulator(request.scenario)
    simulator.simulate()
    text = export_propellant(PropellantAnalysis.create(simulator), request.delimiter)
    return _respond(text, "propellant", request.delimiter)
