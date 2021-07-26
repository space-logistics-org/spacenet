import math

import deal

from .constants import G_0


__all__ = ["delta_v_from", "final_mass_from"]


@deal.pure
@deal.pre(lambda _: 0 < _.isp < math.inf)
@deal.pre(lambda _: 0 < _.m_f < _.m_0 < math.inf)
@deal.post(lambda x: 0 <= x)
def delta_v_from(isp: float, m_0: float, m_f: float):
    """
    Find the delta-v resulting from the burn described by the
    given specific impulse and masses.

    :param isp: specific impulse in seconds
    :param m_0: initial mass
    :param m_f: final mass; must be same units as m_0
    :return: change in velocity resulting from burning (m_0 - m_f) units of fuel
        with given specific impulse
    """
    delta_v = isp * G_0 * math.log(m_0 / m_f)
    return delta_v


@deal.pure
@deal.pre(lambda _: 0 < _.delta_v < math.inf)
@deal.pre(lambda _: 0 < _.isp < math.inf)
@deal.pre(lambda _: 0 < _.m_0 < math.inf)
@deal.post(lambda x: 0 <= x)  # for real numbers, this is <
@deal.ensure(
    lambda delta_v, isp, m_0, result: result <= m_0
)  # for real numbers, this is <
def final_mass_from(delta_v: float, isp: float, m_0: float):
    """
    Find the final mass after a burn with the given velocity change, specific impulse,
    and initial mass.

    :param delta_v: change in velocity
    :param isp: specific impulse
    :param m_0: initial mass
    :return: final mass, in same units as initial mass
    """
    m_f = m_0 * math.exp(-delta_v / (isp * G_0))
    return m_f
