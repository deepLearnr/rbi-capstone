import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import "../styles/LearningPaths.css";

function LearningPaths() {
  const navigate = useNavigate();

  const [searchTerm, setSearchTerm] = useState("");
  const [activeCategory, setActiveCategory] = useState("All");

  const categories = [
    "All",
    "Recommended",
    "Banking",
    "Compliance",
    "Risk",
    "Cyber",
    "Digital",
  ];

  const learningPaths = [
    {
      id: 1,
      icon: "🏦",
      title: "Core Banking",
      category: "Banking",
      courses: 8,
      hours: 6,
    },
    {
      id: 2,
      icon: "📋",
      title: "Compliance",
      category: "Compliance",
      courses: 6,
      hours: 4,
    },
    {
      id: 3,
      icon: "⚠️",
      title: "Risk Management",
      category: "Risk",
      courses: 5,
      hours: 3,
    },
    {
      id: 4,
      icon: "🔐",
      title: "Cyber Security",
      category: "Cyber",
      courses: 5,
      hours: 3,
    },
    {
      id: 5,
      icon: "💻",
      title: "Digital Banking",
      category: "Digital",
      courses: 7,
      hours: 5,
    },
    {
      id: 6,
      icon: "👔",
      title: "Role Based",
      category: "Recommended",
      courses: 10,
      hours: 8,
    },
  ];

  const filteredPaths = learningPaths.filter((path) => {
    const matchesCategory =
      activeCategory === "All" || path.category === activeCategory;

    const matchesSearch = path.title
      .toLowerCase()
      .includes(searchTerm.toLowerCase());

    return matchesCategory && matchesSearch;
  });

  return (
    <div className="learning-page">
      {/* Page Header */}
      <div className="learning-heading">
        <div className="learning-heading-icon">🗺️</div>

        <div>
          <h1>Learning Paths</h1>
          <p>Build your knowledge and skills through structured learning</p>
        </div>
      </div>

      {/* Search */}
      <div className="learning-search">
        <span className="learning-search-icon">🔍</span>

        <input
          type="text"
          placeholder="Search courses and learning paths..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />

        <span className="learning-search-button">🔎</span>
      </div>

      {/* Categories */}
      <div className="learning-category-filter">
        {categories.map((category) => (
          <button
            key={category}
            className={
              activeCategory === category
                ? "learning-category-btn active"
                : "learning-category-btn"
            }
            onClick={() => setActiveCategory(category)}
          >
            {category}
          </button>
        ))}
      </div>

      {/* Recommended */}
      <section className="recommended-section">
        <div className="learning-section-title">
          <span>🎯</span>
          <h2>Recommended For You</h2>
        </div>

        <div className="recommended-card">
          <div className="recommended-icon">🏦</div>

          <div className="recommended-content">
            <h3>Regulatory Compliance</h3>

            <p>Learn the fundamentals of regulatory compliance</p>

            <div className="recommended-meta">
              <span>📚 6 Courses</span>
              <span>⏱️ 4 Hours</span>
              <span className="beginner">🟢 Beginner</span>
            </div>

            <div className="progress-area">
              <div className="progress-label">
                <span>Progress:</span>
                <strong>70%</strong>
              </div>

              <div className="progress-bar">
                <div className="progress-fill" style={{ width: "70%" }}></div>
              </div>
            </div>

            <div className="recommended-action">
              <button
                className="continue-btn"
                onClick={() => navigate("/learning/2")}
              >
                Continue Learning →
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* Explore Learning Paths */}
      <section className="explore-section">
        <div className="learning-section-title">
          <span>📚</span>
          <h2>Explore Learning Paths</h2>
        </div>

        {filteredPaths.length > 0 ? (
          <div className="learning-grid">
            {filteredPaths.map((path) => (
              <div className="learning-card" key={path.id}>
                <div className="learning-card-icon">{path.icon}</div>

                <h3>{path.title}</h3>

                <div className="learning-card-info">
                  <span>{path.courses} Courses</span>
                  <span>{path.hours} Hours</span>
                </div>

                <button
                  className="explore-btn"
                  onClick={() => navigate(`/learning/${path.id}`)}
                >
                  Explore →
                </button>
              </div>
            ))}
          </div>
        ) : (
          <div className="learning-no-results">
            <div>🔍</div>

            <h3>No learning paths found</h3>

            <p>Try a different search term or category.</p>
          </div>
        )}
      </section>
    </div>
  );
}

export default LearningPaths;
