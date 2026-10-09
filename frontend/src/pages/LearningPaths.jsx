import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { learningApi } from "../services/learningApi";
import "../styles/LearningFlow.css";

function LearningPaths() {
  const navigate = useNavigate();
  const [modules, setModules] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    learningApi.modules()
      .then(setModules)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="learning-flow-page">
      <header className="learning-flow-header">
        <p className="learning-flow-eyebrow">RBI SAATHI · LEARN</p>
        <h1>Learning Paths</h1>
        <p>Study practical banking concepts and track your progress.</p>
      </header>
      {loading && <p role="status">Loading learning modules…</p>}
      {error && <p className="learning-flow-error" role="alert">{error}</p>}
      {!loading && !error && modules.length === 0 && (
        <div className="learning-flow-panel">
          <h2>No published modules yet</h2>
          <p>Run the backend demo seed command to add the starter module.</p>
        </div>
      )}
      <div className="learning-flow-grid">
        {modules.map((module) => (
          <article className="learning-flow-card" key={module.id}>
            <span className="learning-flow-tag">{module.category}</span>
            <h2>{module.title}</h2>
            <p>{module.description}</p>
            <div className="learning-flow-meta">
              <span>{module.difficulty}</span>
              <span>{module.estimated_minutes ?? "—"} min</span>
              <span>{module.section_count} sections</span>
            </div>
            <div className="learning-flow-progress-track">
              <span style={{ width: `${module.progress_percent}%` }} />
            </div>
            <p className="learning-flow-progress-label">
              {module.progress_percent}% complete
            </p>
            <button className="learning-flow-button" onClick={() => navigate(`/learning/${module.id}`)}>
              {module.completed ? "Review module" : "Continue learning"}
            </button>
          </article>
        ))}
      </div>
    </div>
  );
}

export default LearningPaths;
