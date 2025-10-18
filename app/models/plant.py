from pydantic import BaseModel, Field
from typing import Optional

class Plant(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    name: str
    latin_name: Optional[str] = None
    description: Optional[str] = None
    watering: Optional[str] = None
    sunlight: Optional[str] = None

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "name": "Tomato",
                "latin_name": "Solanum lycopersicum",
                "description": "A red fruit often mistaken for a vegetable.",
                "watering": "Regular",
                "sunlight": "Full sun"
            }
        }
