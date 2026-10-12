import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { SCENARIO_CATEGORIES } from "../data/scenarios";
import { getScenarioPerformance } from "../services/scenarioProgress";
import "../styles/Scenarios.css";

function Scenarios() {
  const navigate = useNavigate();
  const [searchTerm, setSearchTerm] = useState("");
  const [activeCategory, setActiveCategory] = useState("All");
  const performance = getScenarioPerformance();
  const recommendedScenario = SCENARIO_CATEGORIES.find(
    (scenario) => scenario.id === "cyber-security",
  );
  const categories = ["All", ...SCENARIO_CATEGORIES.map((scenario) => scenario.title)];

  const filteredScenarios = SCENARIO_CATEGORIES.filter((scenario) => {
    const matchesCategory =
      activeCategory === "All" || scenario.title === activeCategory;
    const searchableText = `${scenario.title} ${scenario.description}`.toLowerCase();
    const matchesSearch = searchableText.includes(searchTerm.toLowerCase().trim());
    return matchesCategory && matchesSearch;
  });

  return (
    <div className="scenarios-page">
      <div className="scenarios-heading">
        <div className="scenarios-heading-icon">🎯</div>
        <div>
          <h1>Practice Banking Scenarios</h1>
          <p>Work through the scenario questions currently included in this demo.</p>
        </div>
      </div>

      <p className="scenario-storage-note">
        Demo scope: 5 questions across 3 topic sets. Scenario sessions and attempts
        are saved in this browser only; they are not synchronized with the backend
        or across devices.
      </p>

      <div className="scenarios-search">
        <span className="scenarios-search-icon" aria-hidden="true">⌕</span>
        <input
          type="text"
          aria-label="Search scenario topics"
          placeholder="Search scenario topics..."
          value={searchTerm}
          onChange={(event) => setSearchTerm(event.target.value)}
        />
      </div>

      <div className="scenarios-category-filter" aria-label="Filter scenario topics">
        {categories.map((category) => (
          <button
            key={category}
            type="button"
            className={
              activeCategory === category
                ? "scenario-category-btn active"
                : "scenario-category-btn"
            }
            aria-pressed={activeCategory === category}
            onClick={() => setActiveCategory(category)}
          >
            {category}
          </button>
        ))}
      </div>

      {activeCategory === "All" && searchTerm.trim() === "" && recommendedScenario && (
        <section className="recommended-scenario-section">
          <div className="scenario-section-title">
            <span aria-hidden="true">★</span>
            <h2>Recommended For You</h2>
          </div>
          <div className="recommended-scenario-card">
            <div className="scenario-card-icon">{recommendedScenario.icon}</div>
            <div className="recommended-scenario-content">
              <h3>Suspicious Email</h3>
              <p>
                You receive an unexpected email asking you to share confidential
                banking information. What should you do?
              </p>
              <div className="scenario-meta">
                <span className="beginner">Beginner</span>
                <span>3 questions in the Cyber Security set</span>
              </div>
              <div className="scenario-action">
                <button
                  type="button"
                  onClick={() => navigate(`/scenarios/${recommendedScenario.id}`)}
                >
                  Start Scenario →
                </button>
              </div>
            </div>
          </div>
        </section>
      )}

      <section className="explore-scenarios-section">
        <div className="scenario-section-title">
          <span aria-hidden="true">🎯</span>
          <h2>Available Demo Topic Sets</h2>
        </div>

        {filteredScenarios.length > 0 ? (
          <div className="scenarios-grid">
            {filteredScenarios.map((scenario) => {
              const questionCount = scenario.questions.length;
              return (
                <article className="scenario-category-card" key={scenario.id}>
                  <div className="scenario-category-icon">{scenario.icon}</div>
                  <h3>{scenario.title}</h3>
                  <p>{scenario.description}</p>
                  <p className="scenario-question-count">
                    {questionCount} demo question{questionCount === 1 ? "" : "s"}
                  </p>
                  <button
                    type="button"
                    onClick={() => navigate(`/scenarios/${scenario.id}`)}
                  >
                    Start practice →
                  </button>
                </article>
              );
            })}

            {activeCategory === "All" && searchTerm.trim() === "" && (
              <article className="scenario-category-card performance-card">
                <div className="scenario-category-icon">📊</div>
                <h3>My Scenario Performance</h3>
                <div className="performance-score">
                  {performance.attempts > 0 ? (
                    <>
                      Average score: <strong>{performance.averageScore}%</strong>
                      <p>{performance.attempts} saved attempt(s) in this browser</p>
                    </>
                  ) : (
                    <p>No completed scenario attempts in this browser yet.</p>
                  )}
                </div>
                <button type="button" onClick={() => navigate("/progress")}>
                  View learning progress →
                </button>
              </article>
            )}
          </div>
        ) : (
          <div className="scenario-no-results">
            <div aria-hidden="true">⌕</div>
            <h3>No topics found</h3>
            <p>Try a different search term or category.</p>
          </div>
        )}
      </section>
    </div>
  );
}

export default Scenarios;
