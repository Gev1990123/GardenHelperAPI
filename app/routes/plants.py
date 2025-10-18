from fastapi import APIRouter, HTTPException
from bson import ObjectId
from app.db.mongo import db
from app.models.plant import Plant

router = APIRouter()

def serialize_doc(doc):
    """Convert MongoDB document to JSON-serializable dict."""
    doc["_id"] = str(doc["_id"])
    return doc

@router.get("/plants")
async def list_plants():
    """Get a list of plants (limit 100)"""
    plants = await db.plants.find().to_list(100)
    return [serialize_doc(p) for p in plants]

@router.get("/plants/{plant_id}")
async def get_plant(plant_id: str):
    """Get a single plant by its ID"""
    try:
        plant = await db.plants.find_one({"_id": ObjectId(plant_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid plant ID format")
    if not plant:
        raise HTTPException(status_code=404, detail="Plant not found")
    return serialize_doc(plant)

@router.post("/plants")
async def add_plant(plant: Plant):
    """Add a new plant to the database"""
    plant_dict = plant.dict(by_alias=True, exclude_none=True)
    plant_dict.pop("_id", None)  # Let MongoDB generate its own ID
    result = await db.plants.insert_one(plant_dict)
    new_plant = await db.plants.find_one({"_id": result.inserted_id})
    return serialize_doc(new_plant)