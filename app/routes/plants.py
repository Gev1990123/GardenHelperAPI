from fastapi import APIRouter
from app.db.mongo import db

router = APIRouter()

@router.get("/plants")
async def list_plants():
    plants = await db.plants.find().to_list(100)
    return plants

@router.get("/plants/{plant_id}")
async def get_plant(plant_id: int):
    plant = await db.plants.find_one({"_id": plant_id})
    if not plant:
        return {"error": "Plant not found"}
    return plant
    
