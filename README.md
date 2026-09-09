# Management Radar

Management Radar is a lightweight research assistant built for the
**HDFC AMC AI & Digital Group — Management Radar Intern Build
Challenge**.

The idea is simple: analysts often have to go through exchange
announcements, company filings, and management interviews before they
can understand what a company is saying or planning. This prototype
brings those sources into one place and lets an analyst ask questions
about them.

The application currently covers the two companies from the supplied
source list:

- **Maruti Suzuki**
- **Infosys**

Instead of asking the LLM to answer from general knowledge, the
application first retrieves relevant passages from the processed source
material stored in SQLite. Only that retrieved context is sent to the
LLM, and the resulting answer is returned with citations to the original
document page or video timestamp.

------------------------------------------------------------------------
Demo Video Link : https://drive.google.com/file/d/1M5EGsbkTvGU4JnrpYkXyuFH4vEEIgLRU/view?usp=sharing

## 1. Overview

Management Radar has four main parts:

1.  **Fetch & Read** — process the supplied BSE announcement PDFs and
    YouTube management interviews.
2.  **Store** — keep companies, sources, extracted text, metadata,
    summaries, and tags in SQLite.
3.  **Understand & Answer** — generate source summaries and topic tags,
    then answer analyst questions using retrieval-augmented generation.
4.  **Show** — provide a clean single-page React dashboard with a
    company timeline and research chat.

The implementation intentionally stays lightweight. A vector database,
authentication system, and distributed architecture were not added
because they are unnecessary for the supplied dataset and the 24-hour
prototype scope.

------------------------------------------------------------------------

## 2. Features

### Source ingestion

- Reads the supplied CSV source list.
- Supports BSE PDF announcements.
- Supports YouTube management interviews with captions.
- Downloads and caches PDF files locally.
- Caches YouTube transcripts instead of downloading raw videos.
- Handles individual source failures without stopping the complete
  ingestion process.
- Stores source processing status and errors.

### Document processing

- Extracts PDF text using PyMuPDF.
- Preserves PDF page numbers.
- Retrieves YouTube transcripts with timestamps.
- Splits source content into searchable chunks.
- Stores page numbers for PDF chunks.
- Stores start/end timestamps for YouTube chunks.

### AI processing

- Generates a short plain-language summary for each processed source.
- Generates relevant topic tags.
- Uses structured JSON output from Gemini.
- Validates the structured response before storing it.
- Persists AI-generated metadata in the database.

### Grounded research chat

The question-answering flow is:

``` text
User question
      ↓
Retrieve relevant database chunks
      ↓
Collect source metadata
      ↓
Send only retrieved context to Gemini
      ↓
Generate grounded answer
      ↓
Validate citation chunk IDs
      ↓
Return answer + citations
```

The LLM is explicitly instructed to use only the supplied source context
and to treat documents and transcripts as untrusted data rather than
instructions.

If the supplied sources do not contain enough evidence, the system is
designed to say so instead of guessing.

### Citations

PDF citations include:

- Document title
- Page number
- Original source URL

YouTube citations include:

- Video title
- Timestamp
- Original YouTube URL

Citations are clickable from the UI where practical.

### Dashboard

The frontend provides:

- Company selector
- Management intelligence overview
- Source statistics
- Source timeline
- Source type labels
- AI summaries
- Topic tags
- Source search
- Source-type filtering
- Tag filtering
- Research chat
- Answer citations
- Loading states
- Error states
- Empty-result states

The visual direction uses **deep navy, red, and white**, with an
intentionally clean and professional layout.

------------------------------------------------------------------------

## 3. Tech Stack

### Frontend

- React
- Vite
- JavaScript
- CSS

### Backend

- Python
- FastAPI
- SQLAlchemy

### Database

- SQLite

### Data processing

- Pandas
- PyMuPDF
- Requests
- youtube-transcript-api

### AI

- Google Gemini API
- google-genai
- Pydantic for structured response validation

------------------------------------------------------------------------


------------------------------------------------------------------------

## 4 . Project Structure

``` text
management-radar/
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── database.py
│   │   ├── models.py
│   │   └── services/
│   │       ├── ai_service.py
│   │       ├── rag_service.py
│   │       ├── retrieval_service.py
│   │       └── youtube_processor.py
│   │
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   └── index.css
│   ├── package.json
│   └── ...
│
├── scripts/
│   ├── load_sources.py
│   ├── process_youtube.py
│   └── generate_ai_metadata.py
│
├── data/
│   └── cache/
│       ├── pdfs/
│       └── transcripts/
│
├── database/
│   └── management_radar.db
│
├── .env.example
├── .gitignore
├── NOTES.md
└── README.md
```

------------------------------------------------------------------------

## 5. Database Design

SQLite was chosen because the supplied dataset is small and a real
relational database is explicitly required by the assignment. It also
keeps the project easy to run and explain.

### `companies`

Stores the companies supported by the application.

Typical fields:

- `id`
- `name`
- `ticker`

### `sources`

Stores the original announcements and videos.

It contains information such as:

- company relationship
- source type
- title
- URL
- publication date
- local cached path
- processing status
- processing error

### `text_chunks`

Stores searchable pieces of extracted source content.

Each chunk keeps its source relationship and location metadata.

For PDFs:

- page number

For YouTube transcripts:

- start timestamp
- end timestamp

This metadata is later used to produce citations.

### `tags`

Stores reusable topic tags.

### `source_tags`

Connects sources with their AI-generated tags.

### `ai_summaries`

Stores the AI-generated summary and model information used to generate
it.

------------------------------------------------------------------------

## 6. Data Flow

The ingestion pipeline follows:

``` text
CSV
 ↓
Identify source
 ↓
Check local cache
 ↓
Download/retrieve if required
 ↓
Extract content
 ↓
Normalize content
 ↓
Create chunks
 ↓
Store in SQLite
 ↓
Generate AI summary + tags
 ↓
Retrieve relevant chunks
 ↓
Answer analyst questions
```

The pipeline is designed so that one bad source does not stop the rest
of the dataset from being processed.

------------------------------------------------------------------------

## 7. Retrieval / RAG Approach

This prototype deliberately uses a simple keyword-based retrieval
strategy instead of introducing a separate vector database.

The retrieval service:

1.  Receives the analyst’s question.
2.  Normalizes the query.
3.  Scores database chunks for keyword relevance.
4.  Applies the selected company filter.
5.  Selects the highest-scoring relevant chunks.
6.  Sends only those chunks to Gemini.

For this relatively small dataset, this is fast, reliable, and easy to
explain.

If the system were expanded to thousands of documents, semantic
embeddings or hybrid retrieval would be a sensible next step.

------------------------------------------------------------------------

## 8. Citation Design

Citation metadata is not invented by the frontend.

The LLM returns the IDs of the chunks it believes support the answer.
The backend checks those IDs against the chunks that were actually
retrieved.

Only valid retrieved chunk IDs are converted into citations.

Example:

``` text
PDF:
Q1 FY27 Results — Page 4

YouTube:
Management Interview — 12:35
```

This design helps prevent the model from creating page numbers or
timestamps that do not exist in the source database.

------------------------------------------------------------------------

## 9. Security

The project includes practical security measures:

- Gemini API keys are stored in `.env`.
- `.env` is included in `.gitignore`.
- `.env.example` contains configuration without a real secret.
- API keys are not hardcoded in application code.
- PDFs and transcripts are treated as external/untrusted data.
- The RAG prompt tells the model to ignore instructions contained inside
  retrieved source text.
- Structured Gemini responses are validated with Pydantic.
- Citation IDs returned by the LLM are validated against actually
  retrieved chunks.
- The application does not execute code or instructions found inside
  documents or LLM responses.

------------------------------------------------------------------------

## 10. Setup

### Prerequisites

- Python 3.x
- Node.js and npm
- A Gemini API key

### Clone the repository

``` powershell
git clone <repository-url>
cd management-radar
```

### Create the Python environment

On Windows PowerShell:

``` powershell
python -m venv venv
.env\Scripts\Activate.ps1
```

### Install backend dependencies

``` powershell
pip install -r backendequirements.txt
```

### Configure Gemini

Create `.env` in the project root:

``` env
GEMINI_API_KEY=YOUR_GEMINI_API_KEY
GEMINI_MODEL=gemini-3.6-flash
```

Never commit the real `.env` file or API key.

### Install frontend dependencies

``` powershell
cd frontend
npm install
cd ..
```

------------------------------------------------------------------------

## 11. Database and Ingestion

The submitted project is intended to contain the populated SQLite
database and cached processed source material so the evaluator can
inspect and run the prototype quickly.

If rebuilding the database from the supplied CSV, load the source
records:

``` powershell
python scripts\load_sources.py
```

Process the YouTube transcripts:

``` powershell
python scripts\process_youtube.py
```

Run the project’s PDF processing step to populate the PDF text chunks.

Then generate summaries and tags:

``` powershell
python scripts\generate_ai_metadata.py
```

The ingestion scripts are designed to continue when an individual source
fails.

------------------------------------------------------------------------

## 12. Run the Backend

From the project root:

``` powershell
.env\Scripts\Activate.ps1
uvicorn backend.app.main:app --reload
```

The API runs at:

``` text
http://127.0.0.1:8000
```

FastAPI’s interactive documentation:

``` text
http://127.0.0.1:8000/docs
```

------------------------------------------------------------------------

## 13. Run the Frontend

Open another terminal:

``` powershell
cd frontend
npm run dev
```

Vite will show the local URL, normally:

``` text
http://localhost:5173
```

Open that address in the browser.

------------------------------------------------------------------------

## 14. Example Questions

Try questions such as:

``` text
What has management said about expansion plans?
```

``` text
What did management say about margins?
```

``` text
What are the company's major risks?
```

``` text
What new orders have been announced?
```

``` text
What is management's strategy for technology and AI?
```

Questions about information that is not present in the supplied sources
should result in an explicit “not enough information” response rather
than a guessed answer.

------------------------------------------------------------------------

## 15. Handling Failed Sources

External links can become unavailable or return unexpected content.

During development, one supplied BSE source returned HTML instead of the
expected PDF. The ingestion pipeline recorded the failure and continued
processing the remaining sources.

This behavior is intentional. The assignment asks the system to handle
bad links and unavailable content gracefully rather than crashing the
complete ingestion run.

------------------------------------------------------------------------

## 16. AI-Assisted Development

AI-assisted coding was used openly during development, including:

- project structure and implementation guidance
- Gemini prompt design
- summarization and tagging
- grounded RAG prompt design
- frontend implementation
- debugging and refinement

The important prompts, accepted suggestions, rejected suggestions,
manual fixes, and engineering decisions are documented in `NOTES.md`.

AI-generated summaries and tags are persisted in SQLite rather than
generated again every time the dashboard is opened.

------------------------------------------------------------------------

## 17. Design Decisions

### Why SQLite?

The dataset is small, and SQLite satisfies the requirement for a real
database without requiring a separate database server.

### Why keyword retrieval?

The supplied dataset contains a relatively small number of documents.
Keyword retrieval is simple, fast, and easy to explain during an
interview.

### Why Gemini?

The assignment allows any LLM. Gemini provided the structured response
capability needed for summaries, tags, and grounded question answering.

### Why React + Vite?

React is well suited to the required single-page dashboard, while Vite
keeps the frontend lightweight.

### Why cache transcripts instead of videos?

The application only needs the transcript for analysis and citations.
Caching transcripts keeps the project smaller and follows the
requirement not to include raw YouTube video files.

------------------------------------------------------------------------

## 18. Limitations

This is a prototype rather than a production financial research
platform.

Current limitations:

- Retrieval is keyword-based rather than embedding-based.
- The source collection is limited to the supplied CSV.
- External source availability can change.
- AI output depends on the retrieved context and Gemini API.
- There is no authentication.
- There is no production deployment configuration.
- Ingestion is script-driven rather than continuously scheduled.
- The system does not automatically monitor new company disclosures.

These limitations were deliberately accepted to keep the implementation
reliable and achievable within the 24-hour challenge.

------------------------------------------------------------------------

## 19. Future Improvements

If the project were taken further, useful improvements would include:

- Semantic/vector retrieval for larger collections.
- Hybrid keyword + embedding search.
- Scheduled ingestion of new exchange filings.
- Automatic monitoring of new management interviews.
- More detailed management-event analytics.
- Saved research queries.
- User authentication.
- Production database and deployment.
- Automated evaluation of groundedness and citation accuracy.

------------------------------------------------------------------------

