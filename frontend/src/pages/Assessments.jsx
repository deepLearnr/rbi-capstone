import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import "../styles/Assessments.css";

function Assessments() {
  const navigate = useNavigate();

  const [searchTerm, setSearchTerm] = useState("");
  const [activeFilter, setActiveFilter] = useState("All");

  const filters = ["All", "Available", "In Progress", "Completed", "Mandatory"];

  const assessments = [
    {
      id: 1,
      icon: "📋",
      title: "Regulatory Compliance Assessment",
      description: "Test your understanding of regulatory compliance concepts.",
      questions: 20,
      duration: "20 Minutes",
      passing: "70%",
      status: "Available",
      mandatory: true,
    },
    {
      id: 2,
      icon: "🔐",
      title: "Cyber Security Assessment",
      description:
        "Check your knowledge of cyber security and data protection.",
      questions: 15,
      duration: "15 Minutes",
      passing: "70%",
      status: "Available",
      mandatory: false,
    },
    {
      id: 3,
      icon: "🏦",
      title: "Banking Basics Assessment",
      description:
        "Test your knowledge of basic banking operations and concepts.",
      questions: 20,
      duration: "20 Minutes",
      passing: "70%",
      status: "Completed",
      mandatory: false,
    },
    {
      id: 4,
      icon: "⚠️",
      title: "Risk Management Assessment",
      description: "Evaluate your understanding of risk management practices.",
      questions: 15,
      duration: "15 Minutes",
      passing: "70%",
      status: "Completed",
      mandatory: true,
    },
  ];

  const recentResults = [
    {
      assessment: "Banking Basics",
      score: "85%",
      status: "Passed",
      date: "20 Sep 2026",
    },
    {
      assessment: "Cyber Security",
      score: "72%",
      status: "Passed",
      date: "18 Sep 2026",
    },
    {
      assessment: "Risk Management",
      score: "58%",
      status: "Failed",
      date: "15 Sep 2026",
    },
  ];

  /* =========================
     FILTER ASSESSMENTS
  ========================= */

  const filteredAssessments = assessments.filter((assessment) => {
    const matchesSearch = assessment.title
      .toLowerCase()
      .includes(searchTerm.toLowerCase());

    let matchesFilter = true;

    if (activeFilter === "Available") {
      matchesFilter = assessment.status === "Available";
    } else if (activeFilter === "In Progress") {
      matchesFilter = assessment.status === "In Progress";
    } else if (activeFilter === "Completed") {
      matchesFilter = assessment.status === "Completed";
    } else if (activeFilter === "Mandatory") {
      matchesFilter = assessment.mandatory === true;
    }

    return matchesSearch && matchesFilter;
  });

  /* =========================
     START ASSESSMENT
  ========================= */

  const handleStartAssessment = (id) => {
    navigate(`/assessments/${id}`);
  };

  /* =========================
     VIEW MY RESULTS
  ========================= */

  const handleViewResult = () => {
    navigate("/my-results");
  };

  return (
    <div className="assessments-page">
      {/* =========================
          PAGE HEADER
      ========================= */}

      <div className="assessments-header">
        <h1>📝 Assessments</h1>

        <p>Test your knowledge and track your learning performance.</p>
      </div>

      {/* =========================
          SEARCH
      ========================= */}

      <div className="assessment-search">
        <span>🔍</span>

        <input
          type="text"
          placeholder="Search assessments..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />

        <span className="search-icon">🔎</span>
      </div>

      {/* =========================
          FILTERS
      ========================= */}

      <div className="assessment-filters">
        {filters.map((filter) => (
          <button
            key={filter}
            className={activeFilter === filter ? "active" : ""}
            onClick={() => setActiveFilter(filter)}
          >
            {filter}
          </button>
        ))}
      </div>

      {/* =========================
          ASSESSMENTS
      ========================= */}

      <section className="assessment-section">
        <h2>📌 Available Assessments</h2>

        <div className="assessment-list">
          {filteredAssessments.length > 0 ? (
            filteredAssessments.map((assessment) => (
              <div className="assessment-card" key={assessment.id}>
                <div className="assessment-card-top">
                  {/* Icon */}

                  <div className="assessment-icon">{assessment.icon}</div>

                  {/* Information */}

                  <div className="assessment-info">
                    <h3>{assessment.title}</h3>

                    <p>{assessment.description}</p>

                    <div className="assessment-meta">
                      <span>📝 {assessment.questions} Questions</span>

                      <span>⏱️ {assessment.duration}</span>

                      <span>🎯 Passing: {assessment.passing}</span>
                    </div>

                    <div className="assessment-status">
                      <span className="status-dot"></span>

                      {assessment.status}
                    </div>

                    {assessment.mandatory && (
                      <span className="mandatory-badge">Mandatory</span>
                    )}
                  </div>

                  {/* Action */}

                  <div className="assessment-action">
                    {/* Available */}

                    {assessment.status === "Available" && (
                      <button
                        onClick={() => handleStartAssessment(assessment.id)}
                      >
                        Start Assessment →
                      </button>
                    )}

                    {/* Completed */}

                    {assessment.status === "Completed" && (
                      <button
                        className="view-result-btn"
                        onClick={handleViewResult}
                      >
                        View Result →
                      </button>
                    )}
                  </div>
                </div>
              </div>
            ))
          ) : (
            <div className="no-assessments">
              <div>🔍</div>

              <h3>No assessments found</h3>

              <p>Try another search term or select a different filter.</p>
            </div>
          )}
        </div>
      </section>

      {/* =========================
          RECENT RESULTS
      ========================= */}

      <section className="recent-results-section">
        <h2>📊 Recent Results</h2>

        <div className="results-table-wrapper">
          <table className="results-table">
            <thead>
              <tr>
                <th>Assessment</th>
                <th>Score</th>
                <th>Status</th>
                <th>Date</th>
              </tr>
            </thead>

            <tbody>
              {recentResults.map((result, index) => (
                <tr key={index}>
                  <td>{result.assessment}</td>

                  <td className="score-cell">{result.score}</td>

                  <td>
                    <span
                      className={`result-status ${
                        result.status === "Passed" ? "passed" : "failed"
                      }`}
                    >
                      {result.status === "Passed" ? "✓" : "✕"} {result.status}
                    </span>
                  </td>

                  <td>{result.date}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}

export default Assessments;
