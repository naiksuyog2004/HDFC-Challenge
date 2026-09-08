from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session

from .database import Base, engine, get_db
from . import models
from .services.rag_service import answer_question


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


class ChatRequest(BaseModel):
    question: str
    company: str | None = None


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


@app.post("/api/chat")
def chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
):
    return answer_question(
        db=db,
        question=request.question,
        company_name=request.company,
    )