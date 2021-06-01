from fastapi import APIRouter

# build a new router
router = APIRouter()

# handle get requests to the root of the router
@router.get("/")
async def hello():
    # return a JSON object
    return {"message": "Hello World"}