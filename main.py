"""
Nexus Backend — entry point
Run with: uvicorn main:app --reload
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.routers import auth, users, coins, weather

app = FastAPI(title="Nexus API")

ALLOWED_ORIGINS = [
    "https://nexus-frontend-pi-lac.vercel.app",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(coins.router)
app.include_router(weather.router)


@app.get("/", tags=["Health"])
def root():
    return {"status": "running", "message": "Nexus API is up!"}
