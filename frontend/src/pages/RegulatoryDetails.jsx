import React, { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import "../styles/RegulatoryDetails.css";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

function formatDate(dateString) {
  if (!dateString) return "Date not available";

  return new Date(`${dateString}T00:00:00`).toLocaleDateString("en-GB", {
    day: "2-digit",
    month: "long",
    year: "numeric",
  });
}

function RegulatoryDetails() {
  const navigate = useNavigate();
  const { id } = useParams();

  const [update, setUpdate] = useState(null);
  const [isRead, setIsRead] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const loadUpdate = async () => {
      try {
        setLoading(true);
        setError("");

        const response = await fetch(
          `${API_BASE_URL}/api/regulatory/updates/${id}`,
        );

        if (!response.ok) {
          if (response.status === 404) {
            throw new Error("Regulatory update not found.");
          }

          throw new Error("Unable to load regulatory update.");
        }

        const data = await response.json();
        setUpdate(data);
      } catch (err) {
        setError(err.message || "Unable to load regulatory update.");
      } finally {
        setLoading(false);
      }
    };

    loadUpdate();
  }, [id]);

  const handleMarkAsRead = () => {
    setIsRead(true);
  };

  if (loading) {
    return (
      <div className="regulatory-details-page">
        <button
          className="back-button"
          onClick={() => navigate("/updates")}
        >
          ← Back to Regulatory Updates
        </button>

        <div className="details-card">
          <h1>Loading regulatory update...</h1>
        </div>
      </div>
    );
  }

  if (error || !update) {
    return (
      <div className="regulatory-details-page">
        <button
          className="back-button"
          onClick={() => navigate("/updates")}
        >
          ← Back to Regulatory Updates
        </button>

        <div className="details-card">
          <h1>Unable to load update</h1>
          <p>{error || "Regulatory update not found."}</p>
        </div>
      </div>
    );
  }

  const simplification = update.simplification;

  return (
    <div className="regulatory-details-page">
      {/* Back Button */}
      <button
        className="back-button"
        onClick={() => navigate("/updates")}
      >
        ← Back to Regulatory Updates
      </button>

      {/* Main Card */}
      <div className="details-card">
        {/* Category */}
        <div className="details-category">
          <span className="category-dot"></span>
          {update.category.toUpperCase()}
        </div>

        {/* Title */}
        <h1>{update.title}</h1>

        {/* Meta Information */}
        <div className="details-meta">
          <span>
            📅 {formatDate(update.publication_date)}
          </span>

          <span>
            Effective: {formatDate(update.effective_date)}
          </span>
        </div>

        <div className="details-divider"></div>

        {/* Overview */}
        <section className="details-section">
          <h2>Overview</h2>

          <p>{simplification.executive_summary}</p>
        </section>

        {/* What Changed */}
        <section className="details-section">
          <h2>What Changed</h2>

          <p>{simplification.what_changed}</p>
        </section>

        {/* Why It Matters */}
        <section className="details-section">
          <h2>Why It Matters</h2>

          <p>{simplification.why_it_matters}</p>
        </section>

        {/* Who Is Affected */}
        <section className="details-section">
          <h2>Who Is Affected</h2>

          <ul className="key-points">
            {simplification.who_is_affected.map((item) => (
              <li key={item}>
                <span>✓</span>
                {item}
              </li>
            ))}
          </ul>
        </section>

        {/* What Should I Do */}
        <section className="details-section">
          <h2>What Should I Do?</h2>

          <ul className="key-points">
            {simplification.what_should_i_do.map((item) => (
              <li key={item}>
                <span>✓</span>
                {item}
              </li>
            ))}
          </ul>
        </section>

        {/* Effective Date */}
        <section className="details-section">
          <h2>Effective From</h2>

          <div className="effective-date">
            {formatDate(update.effective_date)}
          </div>
        </section>

        {/* Terminology */}
        {simplification.terminology?.length > 0 && (
          <section className="details-section">
            <h2>Important Terminology</h2>

            <ul className="key-points">
              {simplification.terminology.map((item) => (
                <li key={item.term}>
                  <span>✓</span>
                  <strong>{item.term}:</strong>&nbsp;{item.meaning}
                </li>
              ))}
            </ul>
          </section>
        )}

        {/* Source Provenance */}
        {update.document && (
          <section className="details-section">
            <h2 className="document-heading">📎 Source</h2>

            <div>
              <strong>RBI Reference:</strong>{" "}
              {update.document.rbi_reference || "Not specified"}
            </div>

            <div>
              <strong>Source File:</strong>{" "}
              {update.document.source_file || "Not specified"}
            </div>

            {update.document.source_url && (
              <div style={{ marginTop: "8px" }}>
                <a
                  href={update.document.source_url}
                  target="_blank"
                  rel="noreferrer"
                >
                  View RBI Source
                </a>
              </div>
            )}
          </section>
        )}

        {/* Mark As Read */}
        <div className="mark-read-container">
          <button
            className={`mark-read-button ${isRead ? "read" : ""}`}
            onClick={handleMarkAsRead}
            disabled={isRead}
          >
            {isRead ? "✓ Marked as Read" : "✓ Mark as Read"}
          </button>
        </div>
      </div>
    </div>
  );
}

export default RegulatoryDetails;
