from backend.app.database import SessionLocal
from backend.app.models import Source, TextChunk

from backend.app.services.youtube_processor import (
    extract_video_id,
    get_cache_path,
    get_transcript,
    create_timestamped_chunks,
)


def main():
    db = SessionLocal()

    youtube_sources = (
        db.query(Source)
        .filter(Source.source_type == "YOUTUBE")
        .all()
    )

    print(
        f"Found {len(youtube_sources)} YouTube sources."
    )

    successful = 0
    failed = 0

    try:

        for source in youtube_sources:

            print()
            print("=" * 60)
            print(f"Processing: {source.title}")
            print(f"URL: {source.url}")

            try:

                video_id = extract_video_id(source.url)

                cache_path = get_cache_path(source.id)

                transcript = get_transcript(
                    video_id,
                    cache_path,
                )

                chunks = create_timestamped_chunks(
                    transcript
                )

                if not chunks:
                    raise ValueError(
                        "No transcript chunks were created."
                    )

                # Remove old chunks if reprocessing.
                old_chunks = (
                    db.query(TextChunk)
                    .filter(
                        TextChunk.source_id == source.id
                    )
                    .all()
                )

                for old_chunk in old_chunks:
                    db.delete(old_chunk)

                db.flush()

                for index, chunk in enumerate(chunks):

                    text_chunk = TextChunk(
                        source_id=source.id,
                        chunk_index=index,
                        text=chunk["text"],
                        start_timestamp=chunk[
                            "start_timestamp"
                        ],
                        end_timestamp=chunk[
                            "end_timestamp"
                        ],
                    )

                    db.add(text_chunk)

                source.local_path = str(cache_path)
                source.status = "processed"
                source.processing_error = None

                db.commit()

                print(
                    f"SUCCESS: {len(chunks)} transcript "
                    f"chunks created."
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
        print("YouTube processing completed.")
        print(f"Successful: {successful}")
        print(f"Failed: {failed}")

    finally:
        db.close()


if __name__ == "__main__":
    main()