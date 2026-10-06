import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import "../styles/RegulatoryUpdates.css";

function RegulatoryUpdates() {
  const navigate = useNavigate();

  const [searchTerm, setSearchTerm] = useState("");
  const [activeCategory, setActiveCategory] = useState("All");

  const categories = [
    "All",
    "Banking",
    "Compliance",
    "Risk",
    "Cyber Security",
    "Digital",
  ];

  const updates = [
    {
      category: "Compliance",
      title: "New Compliance Requirements",
      description:
        "Important updates regarding new compliance requirements for bank employees.",
      date: "24 Sep 2026",
    },
    {
      category: "Cyber Security",
      title: "Security Guidelines",
      description:
        "Updated security guidelines and cyber security practices for employees.",
      date: "23 Sep 2026",
    },
    {
      category: "Digital",
      title: "Digital Banking Update",
      description:
        "Latest regulatory information related to digital banking services.",
      date: "22 Sep 2026",
    },
    {
      category: "Risk",
      title: "Updated Risk Framework",
      description:
        "Important changes and updates to the risk management framework.",
      date: "20 Sep 2026",
    },
  ];

  const filteredUpdates = updates.filter((update) => {
    const matchesCategory =
      activeCategory === "All" || update.category === activeCategory;

    const matchesSearch =
      update.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      update.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
      update.category.toLowerCase().includes(searchTerm.toLowerCase());

    return matchesCategory && matchesSearch;
  });

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

          <h3>New Regulatory Guidelines</h3>

          <p>Important information for bank employees</p>

          <div className="important-bottom">
            <span className="update-date">📅 25 Sep 2026</span>

            {/* Important Update Details */}
            <button
              className="read-more-btn"
              onClick={() => navigate("/updates/1")}
            >
              Read More →
            </button>
          </div>
        </div>
      </section>

      {/* Latest Updates */}
      <section className="latest-section">
        <div className="section-title">
          <span>🆕</span>
          <h2>Latest Updates</h2>
        </div>

        {filteredUpdates.length > 0 ? (
          <div className="updates-grid">
            {filteredUpdates.map((update, index) => (
              <div className="regulatory-card" key={index}>
                <span className="update-category">
                  {update.category.toUpperCase()}
                </span>

                <h3>{update.title}</h3>

                <p>{update.description}</p>

                <div className="card-bottom">
                  <span className="update-date">📅 {update.date}</span>

                  {/* Latest Update Details */}
                  <button
                    className="read-more-btn"
                    onClick={() => navigate(`/updates/${index + 2}`)}
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
