import { useState } from "react";
import "./index.css";

function App() {
  const [company, setCompany] = useState("Maruti Suzuki");
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const askQuestion = async () => {
    if (!question.trim()) {
      return;
    }

    setLoading(true);
    setError("");
    setAnswer(null);

    try {
      const response = await fetch("http://127.0.0.1:8000/api/chat", {
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
            }}
          >
            <option value="Maruti Suzuki">Maruti Suzuki</option>
            <option value="Infosys">Infosys</option>
          </select>
        </div>
      </header>

      <main className="container">
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

        <section className="timeline-section">
          <div className="section-heading">
            <div>
              <span className="eyebrow">Timeline</span>
              <h3>{company}</h3>
            </div>
          </div>

          <div className="empty-state">
            <p>Source timeline will appear here.</p>
            <span>
              Ask a question below to explore management intelligence.
            </span>
          </div>
        </section>

        <section className="chat-section">
          <div className="section-heading">
            <div>
              <span className="eyebrow">Research Assistant</span>
              <h3>Ask Management Radar</h3>
            </div>
          </div>

          <div className="chat-box">
            <textarea
              value={question}
              onChange={(event) => setQuestion(event.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={`Ask something about ${company}...`}
              rows={4}
            />

            <div className="chat-actions">
              <span>Answers are grounded in available company sources.</span>

              <button
                onClick={askQuestion}
                disabled={loading || !question.trim()}
              >
                {loading ? "Thinking..." : "Ask"}
              </button>
            </div>
          </div>

          {error && (
            <div className="error-box">
              <strong>Error</strong>
              <p>{error}</p>
            </div>
          )}

          {answer && (
            <div className="answer-card">
              <div className="answer-header">
                <span className="eyebrow">AI Answer</span>
              </div>

              <p className="answer-text">{answer.answer}</p>

              {answer.citations && answer.citations.length > 0 && (
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
                        {citation.source_type === "BSE_PDF" &&
                          citation.page_number && (
                            <span>
                              Page {citation.page_number}
                            </span>
                          )}

                        {citation.source_type === "YOUTUBE" &&
                          citation.start_timestamp && (
                            <span>
                              {citation.start_timestamp}
                              {citation.end_timestamp &&
                                ` – ${citation.end_timestamp}`}
                            </span>
                          )}

                        <span>Chunk #{citation.chunk_id}</span>
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