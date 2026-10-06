from fastapi import FastAPI

from routers.auth import router as auth_router


app = FastAPI(
    title="Foodys API",
    version="1.0.0",
)


app.include_router(auth_router)


@app.get("/")
def root():
    return {
        "message": "Foodys API is running"
    }