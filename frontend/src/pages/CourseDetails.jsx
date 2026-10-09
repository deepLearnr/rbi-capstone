import React, { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { learningApi } from "../services/learningApi";
import "../styles/LearningFlow.css";

function CourseDetails() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [module, setModule] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  const loadModule = () => learningApi.module(id).then(setModule);

  useEffect(() => {
    setLoading(true);
    loadModule()
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [id]);

  const markComplete = async () => {
    try {
      setSaving(true);
      await learningApi.updateProgress(id, 100);
      await loadModule();
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <div className="learning-flow-page"><p>Loading module…</p></div>;
  if (error || !module) return (
    <div className="learning-flow-page">
      <button className="learning-flow-link" onClick={() => navigate("/learning")}>← Learning paths</button>
      <p className="learning-flow-error" role="alert">{error || "Module not found."}</p>
    </div>
  );

  return (
    <div className="learning-flow-page">
      <button className="learning-flow-link" onClick={() => navigate("/learning")}>← Learning paths</button>
      <header className="learning-flow-header">
        <p className="learning-flow-eyebrow">{module.category} · {module.difficulty}</p>
        <h1>{module.title}</h1>
        <p>{module.description}</p>
        <p className="learning-flow-progress-label">
          Saved progress: {module.progress_percent}%{module.completed ? " · Completed" : ""}
        </p>
      </header>

      <section className="learning-flow-section">
        <h2>Learning sections</h2>
        {module.sections.map((section) => (
          <article className="learning-flow-panel" key={section.id}>
            <h3>{section.section_order}. {section.title}</h3>
            <p>{section.content}</p>
          </article>
        ))}
        <button
          className="learning-flow-button"
          onClick={markComplete}
          disabled={saving || module.completed}
        >
          {saving ? "Saving…" : module.completed ? "Module completed ✓" : "Mark module complete"}
        </button>
      </section>

      <section className="learning-flow-section">
        <h2>Assessments</h2>
        {module.assessments.length === 0 && <p>No assessment is attached to this module yet.</p>}
        {module.assessments.map((assessment) => (
          <article className="learning-flow-panel learning-flow-row" key={assessment.id}>
            <div>
              <h3>{assessment.title}</h3>
              <p>{assessment.question_count} questions · {assessment.duration_minutes} minutes · Pass: {assessment.passing_score}%</p>
            </div>
            <button className="learning-flow-button" onClick={() => navigate(`/assessments/${assessment.id}`)}>
              Start assessment
            </button>
          </article>
        ))}
      </section>
      <p className="learning-flow-disclaimer">
        This module provides foundational learning and does not replace applicable current RBI directions or approved institutional policy.
      </p>
    </div>
  );
}

export default CourseDetails;
