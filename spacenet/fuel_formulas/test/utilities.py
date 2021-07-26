from pydantic import BaseModel
from ...schemas.types import SafeNonNegFloat, SafePosFloat


class DeltaVTestCase(BaseModel):
    isp: SafePosFloat
    m_0: SafePosFloat
    m_f: SafePosFloat
    expected_dv: SafeNonNegFloat
    rel_error: SafeNonNegFloat = 10 ** -3


class FinalMassTestCase(BaseModel):
    dv: SafePosFloat
    isp: SafePosFloat
    m_0: SafePosFloat
    expected_mf: SafeNonNegFloat
    rel_error: SafeNonNegFloat = 10 ** -3
