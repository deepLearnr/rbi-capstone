import React, { useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import "../styles/AskAnswer.css";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

function AskAnswer() {
  const navigate = useNavigate();
  const location = useLocation();

  const question = location.state?.question || "";

  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(Boolean(question));
  const [error, setError] = useState("");
  const [feedback, setFeedback] = useState("");
  const [followUp, setFollowUp] = useState("");

  useEffect(() => {
    let cancelled = false;

    async function fetchAnswer() {
      if (!question.trim()) {
        setLoading(false);
        return;
      }

      setLoading(true);
      setError("");
      setResult(null);

      try {
        const response = await fetch(
          `${API_BASE_URL}/api/assistant/query`,
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({
              question: question.trim(),
            }),
          },
        );

        let data = null;

        try {
          data = await response.json();
        } catch {
          data = null;
        }

        if (!response.ok) {
          const detail =
            typeof data?.detail === "string"
              ? data.detail
              : "Unable to get an answer from RBI Saathi.";

          throw new Error(detail);
        }

        if (!cancelled) {
          setResult(data);
        }
      } catch (requestError) {
        if (!cancelled) {
          setError(
            requestError instanceof Error
              ? requestError.message
              : "Unable to connect to RBI Saathi.",
          );
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    fetchAnswer();

    return () => {
      cancelled = true;
    };
  }, [question]);

  const handleFollowUp = () => {
    const nextQuestion = followUp.trim();

    if (!nextQuestion) {
      return;
    }

    navigate("/ask-answer", {
      state: {
        question: nextQuestion,
      },
    });

    setFollowUp("");
    setFeedback("");
  };

  const renderCitations = () => {
    if (!result || result.evidence_status !== "supported") {
      return null;
    }

    if (!result.citations?.length) {
      return null;
    }

    return (
      <section className="rbi-citations">
        <h2>📌 RBI Sources</h2>

        <div className="rbi-citations-list">
          {result.citations.map((citation) => (
            <div className="rbi-citation-card" key={citation.chunk_id}>
              <div className="rbi-citation-title">
                {citation.document_title}
              </div>

              {citation.section && (
                <div className="rbi-citation-detail">
                  <strong>Section:</strong> {citation.section}
                </div>
              )}

              {(citation.page_start || citation.page_end) && (
                <div className="rbi-citation-detail">
                  <strong>Page:</strong>{" "}
                  {citation.page_start === citation.page_end
                    ? citation.page_start
                    : `${citation.page_start ?? "?"}-${citation.page_end ?? "?"}`}
                </div>
              )}

              {citation.rbi_reference && (
                <div className="rbi-citation-detail">
                  <strong>RBI reference:</strong> {citation.rbi_reference}
                </div>
              )}

              {citation.source_file && (
                <div className="rbi-citation-detail">
                  <strong>Source:</strong> {citation.source_file}
                </div>
              )}

              {citation.source_url && (
                <a
                  className="rbi-citation-link"
                  href={citation.source_url}
                  target="_blank"
                  rel="noreferrer"
                >
                  Open RBI source →
                </a>
              )}
            </div>
          ))}
        </div>
      </section>
    );
  };

  return (
    <div className="ask-answer-page">
      {/* Header */}
      <div className="ask-answer-header">
        <button
          className="back-button"
          type="button"
          onClick={() => navigate("/ask-saathi")}
        >
          ← Back
        </button>

        <h1>💬 Ask</h1>
      </div>

      {/* User Question */}
      <div className="conversation">
        <div className="message user-message">
          <div className="message-label">👤 You</div>

          <div className="user-question">
            {question || "No question entered"}
          </div>
        </div>

        {/* Assistant */}
        <div className="message assistant-message">
          <div className="message-label">🤖 Assistant</div>

          {loading && (
            <div className="assistant-answer">
              Searching verified RBI material...
            </div>
          )}

          {!loading && error && (
            <div className="assistant-error">
              <strong>Unable to get an answer.</strong>
              <p>{error}</p>
              <p>
                Please make sure the RBI Saathi backend is running and try
                again.
              </p>
            </div>
          )}

          {!loading && !error && result?.evidence_status === "insufficient" && (
            <div className="assistant-answer">
              <div className="evidence-status insufficient">
                ⚠️ Insufficient RBI evidence
              </div>

              <p>{result.answer}</p>
            </div>
          )}

          {!loading &&
            !error &&
            result?.evidence_status === "supported" && (
              <div className="assistant-answer">
                <div className="evidence-status supported">
                  ✓ Supported by RBI material
                </div>

                <p>{result.answer}</p>
              </div>
            )}
        </div>
      </div>

      {/* RBI Citations */}
      {renderCitations()}

      {/* Related Resources */}
      <section className="related-resources">
        <h2>📚 Related Resources</h2>

        <div className="resource-card">
          <div className="resource-icon">📖</div>

          <div className="resource-info">
            <h3>RBI Compliance Learning</h3>

            <p>Learning Path → Compliance</p>
          </div>

          <button
            className="resource-view-button"
            type="button"
            onClick={() => navigate("/learning")}
          >
            View →
          </button>
        </div>
      </section>

      {/* Feedback */}
      <div className="answer-feedback">
        <span>Was this answer helpful?</span>

        <button
          type="button"
          className={feedback === "yes" ? "selected" : ""}
          onClick={() => setFeedback("yes")}
          disabled={loading || Boolean(error)}
        >
          👍 Yes
        </button>

        <button
          type="button"
          className={feedback === "no" ? "selected" : ""}
          onClick={() => setFeedback("no")}
          disabled={loading || Boolean(error)}
        >
          👎 No
        </button>
      </div>

      {feedback && (
        <div className="feedback-message">
          {feedback === "yes"
            ? "Thank you for your feedback!"
            : "Thank you. We will try to improve this answer."}
        </div>
      )}

      {/* Ask Another Question */}
      <div className="another-question-wrapper">
        <input
          type="text"
          placeholder="Ask another question..."
          value={followUp}
          onChange={(e) => setFollowUp(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter") {
              handleFollowUp();
            }
          }}
        />

        <button className="voice-button" type="button">
          🎤
        </button>

        <button
          className="send-button"
          type="button"
          onClick={handleFollowUp}
        >
          ➤
        </button>
      </div>
    </div>
  );
}

export default AskAnswer;
