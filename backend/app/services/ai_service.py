import os

from dotenv import load_dotenv
from google import genai
from pydantic import BaseModel


load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY is not set.")

client = genai.Client(api_key=API_KEY)


class ManagementMetadata(BaseModel):
    summary: str
    tags: list[str]


def generate_summary_and_tags(
    company_name: str,
    source_title: str,
    source_type: str,
    text: str,
) -> dict:

    prompt = f"""
You are an investment-management research assistant.

Analyze the following company disclosure or management transcript.

Company: {company_name}
Source type: {source_type}
Source title: {source_title}

SOURCE CONTENT:
{text}

Instructions:

1. Use ONLY information present in the source content.
2. Do NOT invent facts, numbers, events, dates, or management statements.
3. Write a concise management-focused summary.
4. Identify 3 to 6 useful business or management tags.
5. Tags should be short phrases such as:
   Revenue Growth
   EV Strategy
   AI
   Leadership Change
   Dividend
   Margins
   Guidance
6. Do not use information outside the provided source content.
7. Focus on information useful to an investment-management analyst.
"""

    response = client.models.generate_content(
        model=MODEL,
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": ManagementMetadata,
        },
    )

    result = ManagementMetadata.model_validate_json(response.text)

    return {
        "summary": result.summary,
        "tags": result.tags,
    }