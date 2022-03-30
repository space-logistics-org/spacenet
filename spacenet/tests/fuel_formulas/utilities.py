"""
This module contains utilities for testing fuel formula functions.
"""
from pydantic import BaseModel
from ...schemas.types import SafeNonNegFloat, SafePosFloat


class DeltaVTestCase(BaseModel):
    """
    A test case for functions computing delta-v.
    """

    isp: SafePosFloat
    m_0: SafePosFloat
    m_f: SafePosFloat
    expected_dv: SafeNonNegFloat
    rel_error: SafeNonNegFloat = 10 ** -3


class FinalMassTestCase(BaseModel):
    """
    A test case for functions computing final mass.
    """

    dv: SafePosFloat
    isp: SafePosFloat
    m_0: SafePosFloat
    expected_mf: SafeNonNegFloat
    rel_error: SafeNonNegFloat = 10 ** -3
