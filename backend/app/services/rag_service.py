import os

from dotenv import load_dotenv
from google import genai
from pydantic import BaseModel
from sqlalchemy.orm import Session

from .retrieval_service import retrieve_chunks


load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
MODEL = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")

client = genai.Client(api_key=API_KEY)


class Citation(BaseModel):
    chunk_id: int


class RAGResponse(BaseModel):
    answer: str
    citations: list[Citation]


def format_timestamp(seconds: float | None) -> str | None:
    if seconds is None:
        return None

    seconds = int(seconds)

    minutes = seconds // 60
    remaining_seconds = seconds % 60

    return f"{minutes}:{remaining_seconds:02d}"


def answer_question(
    db: Session,
    question: str,
    company_name: str | None = None,
) -> dict:

    chunks = retrieve_chunks(
        db=db,
        query=question,
        company_name=company_name,
        limit=6,
    )

    if not chunks:
        return {
            "answer": "I could not find relevant information in the available sources.",
            "citations": [],
        }

    context_parts = []

    for chunk in chunks:
        source = chunk.source

        context_parts.append(
            f"""
CHUNK ID: {chunk.id}
SOURCE: {source.title}
SOURCE TYPE: {source.source_type}
PAGE: {chunk.page_number}
START TIMESTAMP: {chunk.start_timestamp}
END TIMESTAMP: {chunk.end_timestamp}

CONTENT:
{chunk.text}
"""
        )

    context = "\n\n".join(context_parts)

    prompt = f"""
You are Management Radar, an investment-management research assistant.

Answer the user's question using ONLY the provided source chunks.

USER QUESTION:
{question}

COMPANY FILTER:
{company_name or "All companies"}

SOURCE CHUNKS:
{context}

STRICT RULES:

1. Do not use outside knowledge.
2. Do not invent facts, numbers, dates, statements, or events.
3. If the sources do not contain enough information, say so.
4. Every factual claim should be supported by one or more provided chunks.
5. Return citations using ONLY the CHUNK IDs provided above.
6. Never create or guess a chunk ID.
7. Keep the answer concise and management-focused.
"""

    response = client.models.generate_content(
        model=MODEL,
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": RAGResponse,
        },
    )

    result = RAGResponse.model_validate_json(response.text)

    # Validate citations against retrieved chunks
    valid_chunk_ids = {chunk.id for chunk in chunks}

    validated_citations = []

    for citation in result.citations:
        if citation.chunk_id in valid_chunk_ids:
            validated_citations.append(citation.chunk_id)

    citation_details = []

    for chunk in chunks:
        if chunk.id not in validated_citations:
            continue

        citation_details.append(
            {
                "chunk_id": chunk.id,
                "source_id": chunk.source_id,
                "source_title": chunk.source.title,
                "source_type": chunk.source.source_type,
                "source_url": chunk.source.url,
                "page_number": chunk.page_number,
                "start_timestamp": format_timestamp(
                    chunk.start_timestamp
                ),
                "end_timestamp": format_timestamp(
                    chunk.end_timestamp
                ),
            }
        )

    return {
        "answer": result.answer,
        "citations": citation_details,
    }