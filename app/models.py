from pydantic import BaseModel

class Plant(BaseModel):
    id: int
    name: str
    latin_name: str
    description: str
    watering: str
    sunlight: str
    