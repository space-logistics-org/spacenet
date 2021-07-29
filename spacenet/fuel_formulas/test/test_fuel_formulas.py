import json
import math
from typing import List, Tuple

import deal
import pkg_resources
import pytest
from hypothesis import assume, given, strategies as st
from pydantic import parse_obj_as

from .utilities import DeltaVTestCase, FinalMassTestCase
from ..functions import delta_v_from, final_mass_from
from .. import test

pytestmark = [pytest.mark.unit, pytest.mark.fuel_use_functions]

POSITIVE_FINITE_FLOATS = st.floats(
    min_value=0, exclude_min=True, allow_nan=False, allow_infinity=False
)

PRACTICAL_ISPS = st.floats(min_value=50, max_value=8000)


@deal.cases(delta_v_from)
def test_delta_v_from(case: deal.TestCase) -> None:
    case()


@deal.cases(final_mass_from)
def test_final_mass_from(case: deal.TestCase) -> None:
    case()


def test_delta_v_exact():
    delta_v_tests = parse_obj_as(
        List[DeltaVTestCase],
        json.loads(
            pkg_resources.resource_string(test.__name__, "delta_v_examples.json")
        ),
    )

    for case in delta_v_tests:
        assert case.expected_dv == pytest.approx(
            delta_v_from(isp=case.isp, m_0=case.m_0, m_f=case.m_f), rel=case.rel_error
        )


def test_final_mass_exact():
    final_mass_tests = parse_obj_as(
        List[FinalMassTestCase],
        json.loads(
            pkg_resources.resource_string(test.__name__, "final_mass_examples.json")
        ),
    )

    for case in final_mass_tests:
        assert case.expected_mf == pytest.approx(
            final_mass_from(delta_v=case.dv, isp=case.isp, m_0=case.m_0),
            rel=case.rel_error,
        )


@given(
    isp=PRACTICAL_ISPS,
    masses=st.tuples(POSITIVE_FINITE_FLOATS, POSITIVE_FINITE_FLOATS)
    .filter(lambda t: t[0] != t[1])
    .map(sorted)
    .map(tuple),
    ratio=POSITIVE_FINITE_FLOATS,
)
def test_constant_mass_ratio_same_delta_v(
    isp: float, masses: Tuple[float, float], ratio: float
) -> None:
    m_f, m_0 = masses
    assume(0 < m_f * ratio < m_0 * ratio < math.inf)
    delta_v = delta_v_from(isp, m_0, m_f)
    assume(0 < delta_v < math.inf)
    assert delta_v_from(isp, m_0 * ratio, m_f * ratio) == pytest.approx(
        delta_v, rel=10 ** -3
    )


@given(
    delta_v=st.floats(min_value=1, allow_infinity=False),
    isp=PRACTICAL_ISPS,
    m_0=POSITIVE_FINITE_FLOATS,
    ratio=POSITIVE_FINITE_FLOATS,
)
def test_same_delta_v_constant_mass_ratio(
    delta_v: float, isp: float, m_0: float, ratio: float
) -> None:
    assume(0 < m_0 * ratio < math.inf)
    m_f = final_mass_from(delta_v, isp, m_0)
    mass_ratio = m_f / m_0
    assert final_mass_from(delta_v, isp, m_0 * ratio) / (m_0 * ratio) == pytest.approx(
        mass_ratio, rel=10 ** -3
    )


@given(
    isp=PRACTICAL_ISPS,
    masses=st.tuples(POSITIVE_FINITE_FLOATS, POSITIVE_FINITE_FLOATS)
    .filter(lambda t: t[0] != t[1])
    .map(sorted)
    .map(tuple),
)
def test_mf_to_dv_to_mf(isp: float, masses: Tuple[float, float]) -> None:
    m_f, m_0 = masses
    delta_v = delta_v_from(isp, m_0, m_f)
    assume(0 < delta_v < math.inf)
    m_f_from_dv = final_mass_from(delta_v, isp, m_0)
    assert m_f == pytest.approx(
        m_f_from_dv, rel=10 ** -3
    )  # <= 0.1% error after one inversion


@given(
    delta_v=st.floats(min_value=1, allow_infinity=False),
    isp=PRACTICAL_ISPS,
    m_0=POSITIVE_FINITE_FLOATS,
)
def test_dv_to_mf_to_dv(delta_v: float, isp: float, m_0: float) -> None:
    m_f = final_mass_from(delta_v, isp, m_0)
    assume(0 < m_f < m_0)
    dv_from_m_f = delta_v_from(isp, m_0, m_f)
    assert delta_v == pytest.approx(dv_from_m_f, rel=10 ** -3)
