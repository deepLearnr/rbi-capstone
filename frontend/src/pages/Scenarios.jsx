import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import "../styles/Scenarios.css";

function Scenarios() {
  const navigate = useNavigate();

  const [searchTerm, setSearchTerm] = useState("");
  const [activeCategory, setActiveCategory] = useState("All");

  const categories = [
    "All",
    "Banking",
    "Compliance",
    "Cyber Security",
    "Risk",
    "Digital",
  ];

  const scenarios = [
    {
      id: 1,
      icon: "🏦",
      title: "Banking Operations",
      category: "Banking",
      count: 8,
    },
    {
      id: 2,
      icon: "📋",
      title: "Compliance",
      category: "Compliance",
      count: 10,
    },
    {
      id: 3,
      icon: "🔐",
      title: "Cyber Security",
      category: "Cyber Security",
      count: 6,
    },
    {
      id: 4,
      icon: "⚠️",
      title: "Risk & Fraud",
      category: "Risk",
      count: 7,
    },
    {
      id: 5,
      icon: "💻",
      title: "Digital Banking",
      category: "Digital",
      count: 6,
    },
  ];

  const filteredScenarios = scenarios.filter((scenario) => {
    const matchesCategory =
      activeCategory === "All" || scenario.category === activeCategory;

    const matchesSearch = scenario.title
      .toLowerCase()
      .includes(searchTerm.toLowerCase());

    return matchesCategory && matchesSearch;
  });

  return (
    <div className="scenarios-page">
      {/* Page Header */}
      <div className="scenarios-heading">
        <div className="scenarios-heading-icon">🎯</div>

        <div>
          <h1>Real-World Banking Scenarios</h1>
          <p>Test your decision-making through practical situations.</p>
        </div>
      </div>

      {/* Search */}
      <div className="scenarios-search">
        <span className="scenarios-search-icon">🔍</span>

        <input
          type="text"
          placeholder="Search scenarios..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />

        <span className="scenarios-search-button">🔎</span>
      </div>

      {/* Categories */}
      <div className="scenarios-category-filter">
        {categories.map((category) => (
          <button
            key={category}
            className={
              activeCategory === category
                ? "scenario-category-btn active"
                : "scenario-category-btn"
            }
            onClick={() => setActiveCategory(category)}
          >
            {category}
          </button>
        ))}
      </div>

      {/* Recommended */}
      <section className="recommended-scenario-section">
        <div className="scenario-section-title">
          <span>⭐</span>
          <h2>Recommended For You</h2>
        </div>

        <div className="recommended-scenario-card">
          <div className="scenario-card-icon">🔐</div>

          <div className="recommended-scenario-content">
            <h3>Suspicious Email</h3>

            <p>
              You receive an unexpected email asking you to share confidential
              banking information. What should you do?
            </p>

            <div className="scenario-meta">
              <span className="beginner">🟢 Beginner</span>
              <span>⏱️ 5 min</span>
              <span>📊 5 Questions</span>
            </div>

            <div className="scenario-action">
              <button onClick={() => navigate("/scenarios/1")}>
                Start Scenario →
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* Explore Scenarios */}
      <section className="explore-scenarios-section">
        <div className="scenario-section-title">
          <span>🎯</span>
          <h2>Explore Scenarios</h2>
        </div>

        {filteredScenarios.length > 0 ? (
          <div className="scenarios-grid">
            {filteredScenarios.map((scenario) => (
              <div className="scenario-category-card" key={scenario.id}>
                <div className="scenario-category-icon">{scenario.icon}</div>

                <h3>{scenario.title}</h3>

                <p>{scenario.count} Scenarios</p>

                <button onClick={() => navigate(`/scenarios/${scenario.id}`)}>
                  Explore →
                </button>
              </div>
            ))}

            {/* My Performance */}
            {activeCategory === "All" && searchTerm === "" && (
              <div className="scenario-category-card performance-card">
                <div className="scenario-category-icon">📊</div>

                <h3>My Performance</h3>

                <div className="performance-score">
                  Score: <strong>82%</strong>
                </div>

                <button onClick={() => navigate("/progress")}>View →</button>
              </div>
            )}
          </div>
        ) : (
          <div className="scenario-no-results">
            <div>🔍</div>

            <h3>No scenarios found</h3>

            <p>Try a different search term or category.</p>
          </div>
        )}
      </section>
    </div>
  );
}

export default Scenarios;
