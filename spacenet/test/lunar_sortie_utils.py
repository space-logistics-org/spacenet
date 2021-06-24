import json
import pkg_resources
import pytest

from spacenet import schemas


@pytest.fixture(params=["altair", "ares_1", "ares_5", "orion", "sortie_elements"])
def elements(request):
    yield json.loads(
        pkg_resources.resource_string(
            schemas.__name__, f"lunar_sortie/{request.param}.json"
        )
    )


@pytest.fixture()
def edges():
    yield json.loads(
        pkg_resources.resource_string(
            schemas.__name__, "lunar_sortie/sortie_edges.json"
        )
    )


@pytest.fixture()
def nodes():
    yield json.loads(
        pkg_resources.resource_string(
            schemas.__name__, "lunar_sortie/sortie_nodes.json"
        )
    )


@pytest.fixture()
def resources():
    yield json.loads(
        pkg_resources.resource_string(schemas.__name__, "lunar_sortie/fuels.json")
    )
