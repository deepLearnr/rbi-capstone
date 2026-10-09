import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { learningApi } from "../services/learningApi";
import "../styles/LearningFlow.css";

function Assessments() {
  const navigate = useNavigate();
  const [assessments, setAssessments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    learningApi.assessments()
      .then(setAssessments)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="learning-flow-page">
      <header className="learning-flow-header">
        <p className="learning-flow-eyebrow">RBI SAATHI · CHECK YOUR KNOWLEDGE</p>
        <h1>Assessments</h1>
        <p>Questions and scores are checked by the backend; submitted attempts are saved.</p>
      </header>
      {loading && <p role="status">Loading assessments…</p>}
      {error && <p className="learning-flow-error" role="alert">{error}</p>}
      {!loading && !error && assessments.length === 0 && (
        <div className="learning-flow-panel">
          <h2>No assessments available</h2>
          <p>Run the backend demo seed command to add a starter assessment.</p>
        </div>
      )}
      <div className="learning-flow-grid">
        {assessments.map((assessment) => (
          <article className="learning-flow-card" key={assessment.id}>
            <span className="learning-flow-tag">{assessment.module_title}</span>
            <h2>{assessment.title}</h2>
            <p>{assessment.description}</p>
            <div className="learning-flow-meta">
              <span>{assessment.question_count} questions</span>
              <span>{assessment.duration_minutes} min</span>
              <span>Pass: {assessment.passing_score}%</span>
            </div>
            <button className="learning-flow-button" onClick={() => navigate(`/assessments/${assessment.id}`)}>
              Start assessment
            </button>
          </article>
        ))}
      </div>
      <button className="learning-flow-link" onClick={() => navigate("/my-results")}>View saved results →</button>
    </div>
  );
}

export default Assessments;
