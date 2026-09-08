import re

from sqlalchemy.orm import Session

from ..models import Source, TextChunk


def retrieve_chunks(
    db: Session,
    query: str,
    company_name: str | None = None,
    limit: int = 6,
) -> list[TextChunk]:

    # Extract meaningful words from the question
    words = re.findall(r"[a-zA-Z0-9]+", query.lower())

    stop_words = {
        "what", "when", "where", "which", "who",
        "how", "why", "is", "are", "was", "were",
        "the", "a", "an", "of", "to", "in", "on",
        "for", "and", "or", "with", "about",
        "from", "this", "that", "has", "have",
        "did", "does", "do"
    }

    keywords = [
        word for word in words
        if len(word) >= 3 and word not in stop_words
    ]

    query_obj = db.query(TextChunk).join(Source)

    if company_name:
        query_obj = query_obj.filter(
            Source.company.has(name=company_name)
        )

    chunks = query_obj.all()

    scored_chunks = []

    for chunk in chunks:
        text = chunk.text.lower()

        score = 0

        for keyword in keywords:
            score += text.count(keyword)

        if score > 0:
            scored_chunks.append((score, chunk))

    # Highest relevance first
    scored_chunks.sort(
        key=lambda item: item[0],
        reverse=True,
    )

    return [
        chunk
        for _, chunk in scored_chunks[:limit]
    ]