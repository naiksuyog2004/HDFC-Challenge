from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from .database import Base, engine, get_db
from . import models
from .models import Source, AISummary, Tag, SourceTag
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

@app.get("/api/sources")
def get_sources(
    company: str | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(Source).join(Source.company)

    if company:
        query = query.filter(
            Source.company.has(name=company)
        )

    sources = (
        query
        .order_by(Source.published_at.desc())
        .all()
    )

    results = []

    for source in sources:
        summary = (
            db.query(AISummary)
            .filter(AISummary.source_id == source.id)
            .first()
        )

        tags = (
            db.query(Tag)
            .join(SourceTag, SourceTag.tag_id == Tag.id)
            .filter(SourceTag.source_id == source.id)
            .all()
        )

        results.append(
            {
                "id": source.id,
                "company": source.company.name,
                "title": source.title,
                "source_type": source.source_type,
                "url": source.url,
                "published_at": (
                    source.published_at.isoformat()
                    if source.published_at
                    else None
                ),
                "status": source.status,
                "summary": (
                    summary.summary
                    if summary
                    else None
                ),
                "tags": [
                    tag.name
                    for tag in tags
                ],
            }
        )

    return results