from backend.app.database import SessionLocal
from backend.app.models import (
    Source,
    TextChunk,
    AISummary,
    Tag,
    SourceTag,
)
from backend.app.services.ai_service import generate_summary_and_tags


MAX_SOURCE_TEXT = 12000


def main():
    db = SessionLocal()

    try:
        sources = db.query(Source).all()

        print(f"Found {len(sources)} sources.")

        for source in sources:
            print(f"\nProcessing: {source.title}")

            try:
                # Skip if AI metadata already exists
                existing_summary = (
                    db.query(AISummary)
                    .filter(AISummary.source_id == source.id)
                    .first()
                )

                if existing_summary:
                    print("Already generated. Skipping.")
                    continue

                chunks = (
                    db.query(TextChunk)
                    .filter(TextChunk.source_id == source.id)
                    .order_by(TextChunk.chunk_index)
                    .all()
                )

                if not chunks:
                    print("No text chunks found. Skipping.")
                    continue

                source_text = "\n\n".join(
                    chunk.text for chunk in chunks
                )

                # Keep the prompt reasonably sized
                source_text = source_text[:MAX_SOURCE_TEXT]

                result = generate_summary_and_tags(
                    company_name=source.company.name,
                    source_title=source.title,
                    source_type=source.source_type,
                    text=source_text,
                )

                summary = AISummary(
                    source_id=source.id,
                    summary=result["summary"],
                    model="gemini-3.6-flash",
                )

                db.add(summary)

                for tag_name in result["tags"]:
                    tag_name = tag_name.strip()

                    if not tag_name:
                        continue

                    tag = (
                        db.query(Tag)
                        .filter(Tag.name == tag_name)
                        .first()
                    )

                    if not tag:
                        tag = Tag(name=tag_name)
                        db.add(tag)
                        db.flush()

                    existing_link = (
                        db.query(SourceTag)
                        .filter(
                            SourceTag.source_id == source.id,
                            SourceTag.tag_id == tag.id,
                        )
                        .first()
                    )

                    if not existing_link:
                        db.add(
                            SourceTag(
                                source_id=source.id,
                                tag_id=tag.id,
                            )
                        )

                db.commit()

                print("AI metadata generated successfully.")
                print(f"Tags: {', '.join(result['tags'])}")

            except Exception as exc:
                db.rollback()
                print(f"Failed: {exc}")

        print("\nAI metadata generation completed.")

    finally:
        db.close()


if __name__ == "__main__":
    main()