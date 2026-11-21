"""
Endpoints to analyze propellant logistics.
"""

from fastapi import APIRouter

from spacenet.simulation import TankerSizing, TankerSizingRequest, size_tankers

router = APIRouter()


@router.post("/tankers")
def size_tanker_campaign(request: TankerSizingRequest) -> TankerSizing:
    """
    Sizes the number of tanker flights required to aggregate propellant in
    a depot, accounting for boiloff between flights and transfer losses.
    """
    return size_tankers(request)
