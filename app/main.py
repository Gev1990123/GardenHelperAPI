from fastapi import FastAPI

app = FastAPI(
    title="GardenHelper API",
    description="An open gardening API",
    version="0.1.0"
)

@app.get("/")
def root():
    return {"message": "Welcome to GardenHelper API"}