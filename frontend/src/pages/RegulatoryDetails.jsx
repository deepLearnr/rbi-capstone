import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import "../styles/RegulatoryDetails.css";

function RegulatoryDetails() {
  const navigate = useNavigate();
  const [isRead, setIsRead] = useState(false);

  const handleMarkAsRead = () => {
    setIsRead(true);
  };

  return (
    <div className="regulatory-details-page">
      {/* Back Button */}
      <button className="back-button" onClick={() => navigate("/updates")}>
        ← Back to Regulatory Updates
      </button>

      {/* Main Card */}
      <div className="details-card">
        {/* Category */}
        <div className="details-category">
          <span className="category-dot"></span>
          COMPLIANCE
        </div>

        {/* Title */}
        <h1>New Regulatory Guidelines</h1>

        {/* Meta Information */}
        <div className="details-meta">
          <span>📅 25 September 2026</span>

          <span>👁 245 views</span>
        </div>

        <div className="details-divider"></div>

        {/* Overview */}
        <section className="details-section">
          <h2>Overview</h2>

          <p>
            This update provides information about the latest regulatory
            requirements applicable to employees.
          </p>
        </section>

        {/* Key Points */}
        <section className="details-section">
          <h2>Key Points</h2>

          <ul className="key-points">
            <li>
              <span>✓</span>
              Important regulatory changes
            </li>

            <li>
              <span>✓</span>
              Employee responsibilities
            </li>

            <li>
              <span>✓</span>
              Effective date
            </li>

            <li>
              <span>✓</span>
              Compliance requirements
            </li>
          </ul>
        </section>

        {/* Effective Date */}
        <section className="details-section">
          <h2>Effective From</h2>

          <div className="effective-date">01 October 2026</div>
        </section>

        {/* Related Document */}
        <section className="details-section">
          <h2 className="document-heading">📎 Related Document</h2>

          <button className="document-button">View / Download Circular</button>
        </section>

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
