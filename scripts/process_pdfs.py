from backend.app.database import SessionLocal
from backend.app.models import Source, TextChunk
from backend.app.services.pdf_processor import (
    download_pdf,
    extract_pdf_chunks,
    get_cache_path,
)


def process_pdf(source):
    """Download, extract and store one PDF source."""

    pdf_path = get_cache_path(source.id)

    # Download or use existing cached PDF.
    download_pdf(
        source.url,
        pdf_path,
    )

    # Extract page-aware chunks.
    chunks = extract_pdf_chunks(pdf_path)

    if not chunks:
        raise ValueError("No text could be extracted from the PDF.")

    # Remove previous chunks if this source is being reprocessed.
    old_chunks = (
        db.query(TextChunk)
        .filter(TextChunk.source_id == source.id)
        .all()
    )

    for old_chunk in old_chunks:
        db.delete(old_chunk)

    db.flush()

    # Store new chunks.
    for chunk in chunks:
        text_chunk = TextChunk(
            source_id=source.id,
            chunk_index=chunk["chunk_index"],
            text=chunk["text"],
            page_number=chunk["page_number"],
        )

        db.add(text_chunk)

    source.local_path = str(pdf_path)
    source.status = "processed"
    source.processing_error = None

    db.commit()

    return len(chunks)


def main():
    global db

    db = SessionLocal()

    pdf_sources = (
        db.query(Source)
        .filter(Source.source_type == "BSE_PDF")
        .all()
    )

    print(f"Found {len(pdf_sources)} PDF sources.")

    successful = 0
    failed = 0

    try:
        for source in pdf_sources:

            print()
            print("=" * 60)
            print(f"Processing: {source.title}")
            print(f"URL: {source.url}")

            try:
                chunk_count = process_pdf(source)

                print(
                    f"SUCCESS: {chunk_count} text chunks created."
                )

                successful += 1

            except Exception as error:
                db.rollback()

                source.status = "failed"
                source.processing_error = str(error)

                db.commit()

                print(f"FAILED: {error}")

                failed += 1

        print()
        print("=" * 60)
        print("PDF processing completed.")
        print(f"Successful: {successful}")
        print(f"Failed: {failed}")

    finally:
        db.close()


if __name__ == "__main__":
    main()