import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")
MONGO_DB = os.getenv("MONGODB_DB", "GardenHelperAPICluster01")

client = AsyncIOMotorClient(MONGODB_URI)
db = client[MONGO_DB]