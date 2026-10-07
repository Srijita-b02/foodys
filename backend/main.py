import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from routers.auth import router as auth_router
from routers.donations import router as donations_router
from routers.requests import router as requests_router
from routers.deliveries import router as deliveries_router


load_dotenv()


frontend_origins = [
    origin.strip()
    for origin in os.getenv(
        "FRONTEND_ORIGIN",
        "http://localhost:5173",
    ).split(",")
    if origin.strip()
]


app = FastAPI(
    title="Foodys API",
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=frontend_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth_router)
app.include_router(donations_router)
app.include_router(requests_router)
app.include_router(deliveries_router)


@app.get("/")
def root():
    return {
        "message": "Foodys API is running"
    }