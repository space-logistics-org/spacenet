"""
This module contains tests for events which transport elements from one node to another.
"""
import pytest
from hypothesis import given, strategies as st

from spacenet.schemas import FlightTransport, SpaceTransport, SurfaceTransport

pytestmark = [pytest.mark.schema, pytest.mark.unit, pytest.mark.event]


@given(st.builds(FlightTransport))
def test_flight(transport: FlightTransport):
    assert "FlightTransport" == transport.type


@given(st.builds(SpaceTransport))
def test_space(transport: SpaceTransport):
    assert "SpaceTransport" == transport.type


@given(st.builds(SurfaceTransport))
def test_surface(transport: SurfaceTransport):
    assert "SurfaceTransport" == transport.type
