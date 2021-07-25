import deal

from ..functions import delta_v_from, final_mass_from


@deal.cases(delta_v_from)
def test_delta_v_from(case: deal.TestCase) -> None:
    case()


@deal.cases(final_mass_from)
def test_final_mass_from(case: deal.TestCase) -> None:
    case()
