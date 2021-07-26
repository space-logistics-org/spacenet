import math
from typing import Tuple

import deal
import pytest
from hypothesis import assume, given, strategies as st

from ..functions import delta_v_from, final_mass_from

POSITIVE_FINITE_FLOATS = st.floats(
    min_value=0, exclude_min=True, allow_nan=False, allow_infinity=False
)

PRACTICAL_ISPS = st.floats(min_value=50, max_value=8000)


@deal.cases(delta_v_from)
def test_delta_v_from(case: deal.TestCase) -> None:
    case()


def test_delta_v_exact():
    assert 468.29 == pytest.approx(
        delta_v_from(isp=214.07, m_0=1, m_f=0.8), rel=10 ** -3
    )


@deal.cases(final_mass_from)
def test_final_mass_from(case: deal.TestCase) -> None:
    case()


def test_final_mass_exact():
    assert 0.8 == pytest.approx(
        final_mass_from(delta_v=468.29, isp=214.07, m_0=1), rel=10 ** -3
    )


@given(
    isp=PRACTICAL_ISPS,
    masses=st.tuples(POSITIVE_FINITE_FLOATS, POSITIVE_FINITE_FLOATS)
    .filter(lambda t: t[0] != t[1])
    .map(sorted)
    .map(tuple),
)
def test_mf_to_dv_to_mf(isp: float, masses: Tuple[float, float]):
    m_f, m_0 = masses
    delta_v = delta_v_from(isp, m_0, m_f)
    assume(0 < delta_v < math.inf)
    m_f_from_dv = final_mass_from(delta_v, isp, m_0)
    assert m_f == pytest.approx(m_f_from_dv, rel=10 ** -3)  # <= 0.1% error after one inversion


@given(
    delta_v=st.floats(min_value=1, allow_infinity=False),
    isp=PRACTICAL_ISPS,
    m_0=POSITIVE_FINITE_FLOATS
)
def test_dv_to_mf_to_dv(delta_v: float, isp: float, m_0: float):
    m_f = final_mass_from(delta_v, isp, m_0)
    assume(0 < m_f < m_0)
    dv_from_m_f = delta_v_from(isp, m_0, m_f)
    assert delta_v == pytest.approx(dv_from_m_f, rel=10 ** -3)
