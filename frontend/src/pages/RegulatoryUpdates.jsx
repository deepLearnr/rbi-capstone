import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import "../styles/RegulatoryUpdates.css";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

function formatDate(dateString) {
  if (!dateString) return "Date not available";

  return new Date(`${dateString}T00:00:00`).toLocaleDateString("en-GB", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  });
}

function RegulatoryUpdates() {
  const navigate = useNavigate();

  const [searchTerm, setSearchTerm] = useState("");
  const [activeCategory, setActiveCategory] = useState("All");
  const [updates, setUpdates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const categories = [
    "All",
    "Banking",
    "Compliance",
    "Risk",
    "Cyber Security",
    "Digital",
  ];

  useEffect(() => {
    const loadUpdates = async () => {
      try {
        setLoading(true);
        setError("");

        const response = await fetch(
          `${API_BASE_URL}/api/regulatory/updates`,
        );

        if (!response.ok) {
          throw new Error("Unable to load regulatory updates.");
        }

        const data = await response.json();
        setUpdates(data);
      } catch (err) {
        setError(err.message || "Unable to load regulatory updates.");
      } finally {
        setLoading(false);
      }
    };

    loadUpdates();
  }, []);

  const filteredUpdates = updates.filter((update) => {
    const matchesCategory =
      activeCategory === "All" || update.category === activeCategory;

    const searchableText = [
      update.title,
      update.category,
      update.simplification?.executive_summary,
      update.simplification?.what_changed,
    ]
      .filter(Boolean)
      .join(" ")
      .toLowerCase();

    const matchesSearch = searchableText.includes(
      searchTerm.toLowerCase(),
    );

    return matchesCategory && matchesSearch;
  });

  const importantUpdate = updates[0];

  return (
    <div className="regulatory-page">
      {/* Page Header */}
      <div className="regulatory-heading">
        <div className="heading-icon">📢</div>

        <div>
          <h1>Regulatory Updates</h1>
          <p>Stay informed about the latest regulatory information</p>
        </div>
      </div>

      {/* Search */}
      <div className="regulatory-search">
        <span className="search-icon">🔍</span>

        <input
          type="text"
          placeholder="Search regulatory updates..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />

        <span className="search-button">🔎</span>
      </div>

      {/* Categories */}
      <div className="category-filter">
        {categories.map((category) => (
          <button
            key={category}
            className={
              activeCategory === category
                ? "category-btn active"
                : "category-btn"
            }
            onClick={() => setActiveCategory(category)}
          >
            {category}
          </button>
        ))}
      </div>

      {/* Important Update */}
      {importantUpdate && (
        <section className="important-section">
          <div className="section-title">
            <span>⭐</span>
            <h2>Important Updates</h2>
          </div>

          <div className="important-card">
            <div className="important-label">
              <span className="red-dot"></span>
              IMPORTANT
            </div>

            <h3>{importantUpdate.title}</h3>

            <p>
              {importantUpdate.simplification?.executive_summary ||
                "Regulatory update available."}
            </p>

            <div className="important-bottom">
              <span className="update-date">
                📅 {formatDate(importantUpdate.publication_date)}
              </span>

              <button
                className="read-more-btn"
                onClick={() =>
                  navigate(`/updates/${importantUpdate.id}`)
                }
              >
                Read More →
              </button>
            </div>
          </div>
        </section>
      )}

      {/* Latest Updates */}
      <section className="latest-section">
        <div className="section-title">
          <span>🆕</span>
          <h2>Latest Updates</h2>
        </div>

        {loading ? (
          <div className="no-results">
            <div>⏳</div>
            <h3>Loading updates...</h3>
            <p>Please wait while regulatory updates are loaded.</p>
          </div>
        ) : error ? (
          <div className="no-results">
            <div>⚠️</div>
            <h3>Unable to load updates</h3>
            <p>{error}</p>
          </div>
        ) : filteredUpdates.length > 0 ? (
          <div className="updates-grid">
            {filteredUpdates.map((update) => (
              <div className="regulatory-card" key={update.id}>
                <span className="update-category">
                  {update.category.toUpperCase()}
                </span>

                <h3>{update.title}</h3>

                <p>
                  {update.simplification?.executive_summary ||
                    "Regulatory update available."}
                </p>

                <div className="card-bottom">
                  <span className="update-date">
                    📅 {formatDate(update.publication_date)}
                  </span>

                  <button
                    className="read-more-btn"
                    onClick={() =>
                      navigate(`/updates/${update.id}`)
                    }
                  >
                    Read More →
                  </button>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="no-results">
            <div>🔍</div>

            <h3>No updates found</h3>

            <p>Try a different search term or category.</p>
          </div>
        )}
      </section>
    </div>
  );
}

export default RegulatoryUpdates;
