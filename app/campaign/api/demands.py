from fastapi import APIRouter, Depends, HTTPException

router = APIRouter()

#bind a route to calculate the required food needed
@router.get("/food")
def food_demand(crew: int, days: int, evas: int):
    crew = 2
    days = 5
    evas = 1
    return (0.83 * crew * days) + (0.2075 * evas)

@router.get("/water")
def food_demand(crew: int, days: int, evas: int):
    crew = 2
    days = 5
    evas = 1
    return (0.83 * crew * days) + (0.2075 * evas)
