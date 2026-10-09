import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { learningApi } from "../services/learningApi";
import "../styles/LearningFlow.css";

function MyResults() {
  const navigate = useNavigate();
  const [attempts, setAttempts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    learningApi.attempts()
      .then(setAttempts)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="learning-flow-page">
      <header className="learning-flow-header">
        <p className="learning-flow-eyebrow">RBI SAATHI · YOUR LEARNING</p>
        <h1>My Results</h1>
        <p>Assessment attempts retrieved from persistent backend storage.</p>
      </header>
      {loading && <p role="status">Loading saved results…</p>}
      {error && <p className="learning-flow-error" role="alert">{error}</p>}
      {!loading && !error && attempts.length === 0 && (
        <div className="learning-flow-panel">
          <h2>No saved attempts yet</h2>
          <button className="learning-flow-button" onClick={() => navigate("/assessments")}>Take an assessment</button>
        </div>
      )}
      {attempts.map((attempt) => (
        <article className="learning-flow-panel" key={attempt.id}>
          <div className="learning-flow-row">
            <div>
              <h2>{attempt.assessment_title}</h2>
              <p>{attempt.module_title}</p>
              <p>{new Date(attempt.completed_at).toLocaleString()}</p>
            </div>
            <div className="learning-flow-result">
              <strong>{attempt.score_percent}%</strong>
              <span>{attempt.passed ? "Passed" : "Not passed"}</span>
            </div>
          </div>
          <p>{attempt.correct_count} / {attempt.total_questions} correct</p>
        </article>
      ))}
    </div>
  );
}

export default MyResults;
