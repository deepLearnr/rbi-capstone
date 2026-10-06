import React from "react";
import { useNavigate } from "react-router-dom";
import "../styles/MyResults.css";

function MyResults() {
  const navigate = useNavigate();

  const performance = {
    averageScore: 78,
    testsCompleted: 12,
    passed: 10,
    attempts: 15,
  };

  const history = [
    {
      assessment: "Banking Basics",
      score: "85%",
      status: "Passed",
      date: "20 Sep 2026",
    },
    {
      assessment: "Compliance",
      score: "78%",
      status: "Passed",
      date: "18 Sep 2026",
    },
    {
      assessment: "Cyber Security",
      score: "72%",
      status: "Passed",
      date: "16 Sep 2026",
    },
    {
      assessment: "Risk Management",
      score: "58%",
      status: "Failed",
      date: "15 Sep 2026",
    },
    {
      assessment: "Digital Banking",
      score: "81%",
      status: "Passed",
      date: "12 Sep 2026",
    },
  ];

  return (
    <div className="my-results-page">
      {/* Header */}

      <div className="my-results-header">
        <div>
          <h1>📊 My Assessment Performance</h1>
          <p>
            View your assessment scores and track your learning performance.
          </p>
        </div>

        <button
          className="results-back-btn"
          onClick={() => navigate("/assessments")}
        >
          ← Assessments
        </button>
      </div>

      {/* Performance Cards */}

      <div className="performance-cards">
        <div className="performance-card">
          <span className="performance-label">Average Score</span>

          <strong>{performance.averageScore}%</strong>
        </div>

        <div className="performance-card">
          <span className="performance-label">Tests Completed</span>

          <strong>{performance.testsCompleted}</strong>
        </div>

        <div className="performance-card">
          <span className="performance-label">Passed</span>

          <strong>{performance.passed}</strong>
        </div>

        <div className="performance-card">
          <span className="performance-label">Attempts</span>

          <strong>{performance.attempts}</strong>
        </div>
      </div>

      {/* Performance History */}

      <section className="performance-history">
        <div className="history-header">
          <div>
            <h2>Performance History</h2>
            <p>Your recent assessment results</p>
          </div>
        </div>

        <div className="history-table-wrapper">
          <table className="history-table">
            <thead>
              <tr>
                <th>Assessment</th>
                <th>Score</th>
                <th>Status</th>
                <th>Date</th>
              </tr>
            </thead>

            <tbody>
              {history.map((item, index) => (
                <tr key={index}>
                  <td className="assessment-name">{item.assessment}</td>

                  <td className="assessment-score">{item.score}</td>

                  <td>
                    <span
                      className={`history-status ${
                        item.status === "Passed" ? "passed" : "failed"
                      }`}
                    >
                      {item.status === "Passed" ? "✓ Passed" : "✕ Failed"}
                    </span>
                  </td>

                  <td>{item.date}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      {/* Summary */}

      <div className="performance-summary">
        <div>
          <span>Pass Rate</span>
          <strong>
            {Math.round(
              (performance.passed / performance.testsCompleted) * 100,
            )}
            %
          </strong>
        </div>

        <div>
          <span>Failed Tests</span>
          <strong>{performance.testsCompleted - performance.passed}</strong>
        </div>

        <div>
          <span>Total Attempts</span>
          <strong>{performance.attempts}</strong>
        </div>
      </div>
    </div>
  );
}

export default MyResults;
