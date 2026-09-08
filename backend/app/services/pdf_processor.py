from urllib3 import response
from pathlib import Path

import fitz
import requests


CACHE_DIR = Path("data/cache/pdfs")

CHUNK_SIZE = 1800
CHUNK_OVERLAP = 200

DOWNLOAD_TIMEOUT = 30
MAX_PDF_SIZE = 30 * 1024 * 1024  # 30 MB


def get_cache_path(source_id: int) -> Path:
    """Return the local cache path for a source."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    return CACHE_DIR / f"source_{source_id}.pdf"


def download_pdf(url: str, destination: Path) -> Path:
    """Download a PDF if it is not already cached."""

    if destination.exists() and destination.stat().st_size > 0:
        print(f"Using cached PDF: {destination}")
        return destination

    print(f"Downloading PDF: {url}")

    response = requests.get(
        url,
        stream=True,
        timeout=DOWNLOAD_TIMEOUT,
        headers={
            "User-Agent": "ManagementRadar/1.0",
        },
    )

    response.raise_for_status()

    content_type = response.headers.get("content-type", "")

    print(f"HTTP status: {response.status_code}")
    print(f"Content-Type: {content_type}")

    content_length = response.headers.get("content-length")

    if content_length and int(content_length) > MAX_PDF_SIZE:
        raise ValueError("PDF is larger than the allowed 30 MB limit.")

    total_size = 0

    with open(destination, "wb") as file:
        for chunk in response.iter_content(chunk_size=8192):
            if not chunk:
                continue

            total_size += len(chunk)

            if total_size > MAX_PDF_SIZE:
                file.close()

                if destination.exists():
                    destination.unlink()

                raise ValueError(
                    "PDF exceeded the allowed 30 MB limit."
                )

            file.write(chunk)

    # Basic validation that we actually downloaded a PDF.
    with open(destination, "rb") as file:
        header = file.read(5)

    if header != b"%PDF-":
        destination.unlink(missing_ok=True)
    
        raise ValueError(
            f"Downloaded content is not a PDF "
            f"(Content-Type: {content_type}, "
            f"first bytes: {header!r})"
        )

    return destination


def clean_text(text: str) -> str:
    """Clean obvious PDF extraction whitespace problems."""

    return " ".join(text.split())


def create_chunks(text: str):
    """Split page text into overlapping chunks."""

    if not text:
        return []

    if len(text) <= CHUNK_SIZE:
        return [text]

    chunks = []

    start = 0

    while start < len(text):
        end = start + CHUNK_SIZE

        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end >= len(text):
            break

        start = end - CHUNK_OVERLAP

    return chunks


def extract_pdf_chunks(pdf_path: Path):
    """
    Extract text from every PDF page.

    Returns:
        [
            {
                "chunk_index": 0,
                "text": "...",
                "page_number": 1,
            },
            ...
        ]
    """

    document = fitz.open(pdf_path)

    chunks = []
    chunk_index = 0

    try:
        for page_number, page in enumerate(document, start=1):

            raw_text = page.get_text()

            text = clean_text(raw_text)

            page_chunks = create_chunks(text)

            for chunk_text in page_chunks:
                chunks.append(
                    {
                        "chunk_index": chunk_index,
                        "text": chunk_text,
                        "page_number": page_number,
                    }
                )

                chunk_index += 1

    finally:
        document.close()

    return chunks