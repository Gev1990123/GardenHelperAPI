from fastapi import APIRouter, HTTPException, File, UploadFile
from bson import ObjectId
from app.db.mongo import db
from app.models.plant import Plant
import csv
from io import StringIO
from pydantic import ValidationError

router = APIRouter()

def serialize_doc(doc):
    """Convert MongoDB document to JSON-serializable dict."""
    doc["_id"] = str(doc["_id"])
    return doc

# -------------------------
# GET all plants
# -------------------------
@router.get("/plants")
async def list_plants():
    """Get a list of plants (limit 100)"""
    plants = await db.plants.find().to_list(100)
    return [serialize_doc(p) for p in plants]

# -------------------------
# GET single plant
# -------------------------
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

# -------------------------
# POST single plant
# -------------------------
@router.post("/plants")
async def add_plant(plant: Plant):
    """Add a new plant to the database"""
    plant_dict = plant.dict(by_alias=True, exclude_none=True)
    plant_dict.pop("_id", None)  # Let MongoDB generate its own ID

    # Check for duplicates
    existing = await db.plants.find_one({
        "$or": [
            {"name": plant.name},
            {"latin_name": plant.latin_name} if plant.latin_name else {}
        ]
    })
    if existing:
        raise HTTPException(status_code=400, detail="Plant with same name or latin_name already exists")

    result = await db.plants.insert_one(plant_dict)
    new_plant = await db.plants.find_one({"_id": result.inserted_id})
    return serialize_doc(new_plant)

# -------------------------
# POST CSV upload with validation and duplicate checking
# -------------------------
@router.post("/plants/upload_csv")
async def upload_plants_csv(file: UploadFile = File(...)):
    """
    Upload a CSV file to add multiple plants.
    - Validates each row with Plant model
    - Skips duplicates based on name or latin_name
    Returns inserted_count, skipped_count, and skipped_rows details.
    """
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed")

    content = await file.read()
    decoded = content.decode("utf-8")
    reader = csv.DictReader(StringIO(decoded))

    reader.fieldnames = [h.strip() for h in reader.fieldnames]

    plants_to_insert = []
    skipped_rows = []

    for idx, row in enumerate(reader, start=1):
        clean_row = {k.strip(): v.strip() if isinstance(v, str) else v for k, v in row.items()}

        try:
            # Validate row
            plant = Plant(**clean_row)
            plant_dict = plant.dict(by_alias=True, exclude_none=True)
            plant_dict.pop("_id", None)

            # Check for duplicates in DB
            existing = await db.plants.find_one({
                "$or": [
                    {"name": plant.name},
                    {"latin_name": plant.latin_name} if plant.latin_name else {}
                ]
            })
            if existing:
                skipped_rows.append({
                    "row": idx,
                    "reason": "Duplicate name or latin_name"
                })
                continue

            plants_to_insert.append(plant_dict)
        except ValidationError as e:
            skipped_rows.append({"row": idx, "errors": e.errors()})

    if not plants_to_insert:
        raise HTTPException(status_code=400, detail="No new valid plant records to insert")

    result = await db.plants.insert_many(plants_to_insert)
    return {
        "inserted_count": len(result.inserted_ids),
        "skipped_count": len(skipped_rows),
        "skipped_rows": skipped_rows
    }
