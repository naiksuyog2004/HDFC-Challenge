from pathlib import Path
import json
import re

from youtube_transcript_api import YouTubeTranscriptApi


CACHE_DIR = Path("data/cache/transcripts")

CHUNK_SIZE = 1800
MAX_TRANSCRIPT_ITEMS = 10000


def extract_video_id(url: str) -> str:
    """Extract the YouTube video ID from common YouTube URL formats."""

    patterns = [
        r"(?:v=)([A-Za-z0-9_-]{11})",
        r"(?:youtu\.be/)([A-Za-z0-9_-]{11})",
        r"(?:youtube\.com/shorts/)([A-Za-z0-9_-]{11})",
    ]

    for pattern in patterns:
        match = re.search(pattern, url)

        if match:
            return match.group(1)

    raise ValueError("Could not extract YouTube video ID.")


def get_cache_path(source_id: int) -> Path:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    return CACHE_DIR / f"source_{source_id}.json"


def fetch_transcript(video_id: str):
    """Fetch the transcript with timestamps."""

    api = YouTubeTranscriptApi()

    transcript = api.fetch(video_id)

    items = []

    for item in transcript:

        if len(items) >= MAX_TRANSCRIPT_ITEMS:
            break

        items.append(
            {
                "text": item.text,
                "start": float(item.start),
                "duration": float(item.duration),
            }
        )

    if not items:
        raise ValueError("YouTube transcript is empty.")

    return items


def save_transcript(path: Path, transcript):
    with open(
        path,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            transcript,
            file,
            ensure_ascii=False,
            indent=2,
        )


def load_cached_transcript(path: Path):
    with open(
        path,
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def get_transcript(video_id: str, cache_path: Path):
    """Load cached transcript or fetch a new one."""

    if cache_path.exists():
        print(f"Using cached transcript: {cache_path}")
        return load_cached_transcript(cache_path)

    print(f"Fetching YouTube transcript: {video_id}")

    transcript = fetch_transcript(video_id)

    save_transcript(
        cache_path,
        transcript,
    )

    return transcript


def create_timestamped_chunks(transcript):
    """
    Group transcript items into chunks while preserving
    the first and last timestamps.
    """

    chunks = []

    current_text = []
    chunk_start = None
    chunk_end = None

    for item in transcript:

        text = item["text"].strip()

        if not text:
            continue

        start = float(item["start"])
        end = start + float(item["duration"])

        if chunk_start is None:
            chunk_start = start

        current_text.append(text)
        chunk_end = end

        combined = " ".join(current_text)

        if len(combined) >= CHUNK_SIZE:

            chunks.append(
                {
                    "text": combined,
                    "start_timestamp": chunk_start,
                    "end_timestamp": chunk_end,
                }
            )

            current_text = []
            chunk_start = None
            chunk_end = None

    if current_text:
        chunks.append(
            {
                "text": " ".join(current_text),
                "start_timestamp": chunk_start,
                "end_timestamp": chunk_end,
            }
        )

    return chunks