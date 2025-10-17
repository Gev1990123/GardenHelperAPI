from fastapi import FastAPI
from app.routes import plants

app = FastAPI(
    title="GardenHelper API",
    description="An open gardening API",
    version="0.1.0"
)

app.include_router(plants.router)

@app.get("/")
def root():
    return {"message": "Welcome to GardenHelper API"}