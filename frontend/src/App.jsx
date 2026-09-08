import { useEffect, useState } from "react";
import "./index.css";

const API_BASE = "http://127.0.0.1:8000";

function App() {
  const [company, setCompany] = useState("Maruti Suzuki");

  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState(null);

  const [sources, setSources] = useState([]);
  const [sourcesLoading, setSourcesLoading] = useState(true);

  // Milestone 11 filters
  const [searchTerm, setSearchTerm] = useState("");
  const [sourceTypeFilter, setSourceTypeFilter] = useState("ALL");
  const [tagFilter, setTagFilter] = useState("ALL");

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    fetchSources();
  }, [company]);

  const fetchSources = async () => {
    setSourcesLoading(true);

    try {
      const response = await fetch(
        `${API_BASE}/api/sources?company=${encodeURIComponent(company)}`
      );

      if (!response.ok) {
        throw new Error("Failed to load company sources.");
      }

      const data = await response.json();

      setSources(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setSourcesLoading(false);
    }
  };

  const askQuestion = async () => {
    if (!question.trim()) {
      return;
    }

    setLoading(true);
    setError("");
    setAnswer(null);

    try {
      const response = await fetch(`${API_BASE}/api/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          question: question.trim(),
          company: company,
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to get an answer from the server.");
      }

      const data = await response.json();

      setAnswer(data);
    } catch (err) {
      setError(
        err.message ||
        "Something went wrong while contacting Management Radar."
      );
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      askQuestion();
    }
  };

  const formatDate = (date) => {
    if (!date) {
      return "Date unavailable";
    }

    return new Date(date).toLocaleDateString("en-IN", {
      day: "2-digit",
      month: "short",
      year: "numeric",
    });
  };

  // Get unique tags for the selected company
  const availableTags = [
    ...new Set(
      sources.flatMap((source) => source.tags || [])
    ),
  ].sort();

  // Apply search + source type + tag filters
  const filteredSources = sources.filter((source) => {
    const search = searchTerm.toLowerCase().trim();

    const matchesSearch =
      !search ||
      source.title.toLowerCase().includes(search) ||
      (source.summary || "").toLowerCase().includes(search) ||
      (source.tags || []).some((tag) =>
        tag.toLowerCase().includes(search)
      );

    const matchesType =
      sourceTypeFilter === "ALL" ||
      source.source_type === sourceTypeFilter;

    const matchesTag =
      tagFilter === "ALL" ||
      (source.tags || []).includes(tagFilter);

    return matchesSearch && matchesType && matchesTag;
  });

  return (
    <div className="app">
      <header className="topbar">
        <div>
          <h1>Management Radar</h1>
          <p>Management intelligence dashboard</p>
        </div>

        <div className="company-selector">
          <label htmlFor="company">Company</label>

          <select
            id="company"
            value={company}
            onChange={(event) => {
              setCompany(event.target.value);
              setAnswer(null);
              setError("");

              // Reset filters when company changes
              setSearchTerm("");
              setSourceTypeFilter("ALL");
              setTagFilter("ALL");
            }}
          >
            <option value="Maruti Suzuki">Maruti Suzuki</option>
            <option value="Infosys">Infosys</option>
          </select>
        </div>
      </header>

      <main className="container">
        {/* HERO */}
        <section className="hero">
          <span className="eyebrow">Management Intelligence</span>

          <h2>
            Track what management is saying,
            <br />
            doing, and signaling.
          </h2>

          <p>
            Search company disclosures and management commentary using
            grounded AI answers with source citations.
          </p>
        </section>

        {/* TIMELINE */}
        <section className="timeline-section">
          <div className="section-heading">
            <div>
              <span className="eyebrow">Timeline</span>
              <h3>{company}</h3>
            </div>

            <span className="source-count">
              {filteredSources.length} of {sources.length} sources
            </span>
          </div>

          {/* FILTERS */}
          {!sourcesLoading && sources.length > 0 && (
            <div className="filters">
              <input
                type="text"
                placeholder="Search sources..."
                value={searchTerm}
                onChange={(event) =>
                  setSearchTerm(event.target.value)
                }
              />

              <select
                value={sourceTypeFilter}
                onChange={(event) =>
                  setSourceTypeFilter(event.target.value)
                }
              >
                <option value="ALL">All sources</option>
                <option value="BSE_PDF">Disclosures</option>
                <option value="YOUTUBE">Videos</option>
              </select>

              <select
                value={tagFilter}
                onChange={(event) =>
                  setTagFilter(event.target.value)
                }
              >
                <option value="ALL">All tags</option>

                {availableTags.map((tag) => (
                  <option value={tag} key={tag}>
                    {tag}
                  </option>
                ))}
              </select>
            </div>
          )}

          {sourcesLoading ? (
            <div className="empty-state">
              <p>Loading sources...</p>
            </div>
          ) : sources.length === 0 ? (
            <div className="empty-state">
              <p>No sources available.</p>
            </div>
          ) : filteredSources.length === 0 ? (
            <div className="empty-state">
              <p>No matching sources.</p>
              <span>
                Try changing your search or filters.
              </span>
            </div>
          ) : (
            <div className="timeline">
              {filteredSources.map((source) => (
                <article
                  className="source-card"
                  key={source.id}
                >
                  <div className="source-date">
                    {formatDate(source.published_at)}
                  </div>

                  <div className="source-content">
                    <div className="source-top">
                      <span className="source-type">
                        {source.source_type === "YOUTUBE"
                          ? "VIDEO"
                          : "DISCLOSURE"}
                      </span>

                      {source.status === "processed" && (
                        <span className="processed">
                          Processed
                        </span>
                      )}
                    </div>

                    <h4>{source.title}</h4>

                    {source.summary && (
                      <p className="source-summary">
                        {source.summary}
                      </p>
                    )}

                    {source.tags &&
                      source.tags.length > 0 && (
                        <div className="tags">
                          {source.tags.map((tag) => (
                            <button
                              className={`tag ${tagFilter === tag
                                  ? "tag-active"
                                  : ""
                                }`}
                              key={tag}
                              onClick={() =>
                                setTagFilter(tag)
                              }
                            >
                              {tag}
                            </button>
                          ))}
                        </div>
                      )}

                    <a
                      className="source-link"
                      href={source.url}
                      target="_blank"
                      rel="noreferrer"
                    >
                      View original source →
                    </a>
                  </div>
                </article>
              ))}
            </div>
          )}
        </section>

        {/* CHAT */}
        <section className="chat-section">
          <div className="section-heading">
            <div>
              <span className="eyebrow">
                Research Assistant
              </span>

              <h3>Ask Management Radar</h3>
            </div>
          </div>

          <div className="chat-box">
            <textarea
              value={question}
              onChange={(event) =>
                setQuestion(event.target.value)
              }
              onKeyDown={handleKeyDown}
              placeholder={`Ask something about ${company}...`}
              rows={4}
            />

            <div className="chat-actions">
              <span>
                Answers are grounded in available company sources.
              </span>

              <button
                onClick={askQuestion}
                disabled={loading || !question.trim()}
              >
                {loading ? "Thinking..." : "Ask"}
              </button>
            </div>
          </div>

          {/* ERROR */}
          {error && (
            <div className="error-box">
              <strong>Error</strong>
              <p>{error}</p>
            </div>
          )}

          {/* ANSWER */}
          {answer && (
            <div className="answer-card">
              <div className="answer-header">
                <span className="eyebrow">AI Answer</span>
              </div>

              <p className="answer-text">
                {answer.answer}
              </p>

              {answer.citations &&
                answer.citations.length > 0 && (
                  <div className="citations">
                    <h4>Sources</h4>

                    {answer.citations.map((citation) => (
                      <div
                        className="citation-card"
                        key={citation.chunk_id}
                      >
                        <div className="citation-title">
                          {citation.source_title}
                        </div>

                        <div className="citation-meta">
                          {citation.source_type ===
                            "BSE_PDF" &&
                            citation.page_number && (
                              <span>
                                Page{" "}
                                {citation.page_number}
                              </span>
                            )}

                          {citation.source_type ===
                            "YOUTUBE" &&
                            citation.start_timestamp && (
                              <span>
                                {citation.start_timestamp}

                                {citation.end_timestamp &&
                                  ` – ${citation.end_timestamp}`}
                              </span>
                            )}

                          <span>
                            Chunk #{citation.chunk_id}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                )}

              {answer.citations &&
                answer.citations.length === 0 && (
                  <div className="no-citations">
                    No source citations were returned.
                  </div>
                )}
            </div>
          )}
        </section>
      </main>
    </div>
  );
}

export default App;