from fastapi import APIRouter
from polling.core.redis import redis_client

router = APIRouter(prefix="/redisDb",tags=["redisDb"])


@router.post("/set")
async def set_data():

    await redis_client.set("username", "Ajay")

    return {"message": "Data stored successfully"}


@router.get("/get")
async def get_data():

    value = await redis_client.get("username")

    return {"value": value}


@router.delete("/delete")
async def delete_data():

    result = await redis_client.delete("username")

    return {"deleted": result == 1}


@router.get("/exists")
async def check_exists():

    result = await redis_client.exists("username")

    return {"exists": result == 1}