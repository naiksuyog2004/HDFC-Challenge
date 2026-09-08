from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import Base, engine
from . import models


# Create database tables when the application starts.
Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Management Radar API",
    description="Backend API for the Management Radar application",
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "message": "Management Radar API is running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }