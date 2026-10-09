import React, { useEffect, useState } from "react";
import { learningApi } from "../services/learningApi";
import "../styles/LearningFlow.css";

function Progress() {
  const [data, setData] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    learningApi.progress().then(setData).catch((err) => setError(err.message));
  }, []);

  return (
    <div className="learning-flow-page">
      <header className="learning-flow-header">
        <p className="learning-flow-eyebrow">RBI SAATHI · YOUR LEARNING</p>
        <h1>My Progress</h1>
        <p>Progress and assessment statistics saved by the backend.</p>
      </header>
      {error && <p className="learning-flow-error" role="alert">{error}</p>}
      {!data && !error && <p role="status">Loading progress…</p>}
      {data && (
        <>
          <div className="learning-flow-grid">
            <article className="learning-flow-card"><span>Overall module progress</span><div className="learning-flow-score">{data.overall_progress}%</div></article>
            <article className="learning-flow-card"><span>Modules completed</span><div className="learning-flow-score">{data.modules_completed}/{data.module_count}</div></article>
            <article className="learning-flow-card"><span>Average assessment score</span><div className="learning-flow-score">{data.assessment_average}%</div></article>
            <article className="learning-flow-card"><span>Saved attempts</span><div className="learning-flow-score">{data.attempts_count}</div></article>
          </div>
          <section className="learning-flow-section">
            <h2>Learning modules</h2>
            {data.modules.map((module) => (
              <article className="learning-flow-panel" key={module.module_id}>
                <div className="learning-flow-row">
                  <div><h3>{module.title}</h3><p>{module.category}</p></div>
                  <strong>{module.progress_percent}%</strong>
                </div>
                <div className="learning-flow-progress-track"><span style={{ width: `${module.progress_percent}%` }} /></div>
              </article>
            ))}
          </section>
        </>
      )}
      <p className="learning-flow-disclaimer">This demo currently tracks one shared demo learner because user authentication is not implemented.</p>
    </div>
  );
}

export default Progress;
