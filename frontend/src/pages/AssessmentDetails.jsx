import React, { useCallback, useEffect, useRef, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { learningApi } from "../services/learningApi";
import "../styles/LearningFlow.css";

function AssessmentDetails() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [assessment, setAssessment] = useState(null);
  const [answers, setAnswers] = useState({});
  const [timeLeft, setTimeLeft] = useState(0);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [autoSubmitFailed, setAutoSubmitFailed] = useState(false);
  const [error, setError] = useState("");
  const submissionStarted = useRef(false);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError("");
    learningApi.assessment(id)
      .then((data) => {
        if (cancelled) return;
        setAssessment(data);
        setTimeLeft((data.duration_minutes || 10) * 60);
        setAnswers({});
        setResult(null);
        setAutoSubmitFailed(false);
        setSubmitting(false);
        submissionStarted.current = false;
      })
      .catch((err) => { if (!cancelled) setError(err.message); })
      .finally(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
  }, [id]);

  useEffect(() => {
    if (!assessment || result || loading) return undefined;
    const timer = window.setInterval(() => {
      setTimeLeft((previous) => Math.max(0, previous - 1));
    }, 1000);
    return () => window.clearInterval(timer);
  }, [assessment, result, loading]);

  const submitAssessment = useCallback(async () => {
    if (!assessment || submissionStarted.current || result) return;
    submissionStarted.current = true;
    setSubmitting(true);
    setError("");
    const payload = assessment.questions.map((question) => ({
      question_id: question.id,
      selected_option: Object.prototype.hasOwnProperty.call(answers, question.id)
        ? answers[question.id]
        : null,
    }));
    try {
      const response = await learningApi.submitAssessment(id, payload);
      setResult(response);
      setAutoSubmitFailed(false);
    } catch (err) {
      submissionStarted.current = false;
      setAutoSubmitFailed(true);
      setError(err.message || "Unable to submit assessment.");
    } finally {
      setSubmitting(false);
    }
  }, [assessment, answers, id, result]);

  useEffect(() => {
    if (timeLeft === 0 && assessment && !loading && !result && !submitting && !autoSubmitFailed) {
      submitAssessment();
    }
  }, [timeLeft, assessment, loading, result, submitting, autoSubmitFailed, submitAssessment]);

  const formatTime = (seconds) =>
    `${String(Math.floor(seconds / 60)).padStart(2, "0")}:${String(seconds % 60).padStart(2, "0")}`;

  if (loading) return <div className="learning-flow-page"><p>Loading assessment…</p></div>;
  if (error && !assessment) return (
    <div className="learning-flow-page"><p className="learning-flow-error" role="alert">{error}</p></div>
  );
  if (!assessment) return <div className="learning-flow-page"><p>Assessment not found.</p></div>;

  if (result) {
    return (
      <div className="learning-flow-page">
        <header className="learning-flow-header">
          <p className="learning-flow-eyebrow">ASSESSMENT RESULT · SAVED</p>
          <h1>{assessment.title}</h1>
          <div className="learning-flow-score">{result.score_percent}%</div>
          <p>{result.correct_count} of {result.total_questions} correct · {result.passed ? "Passed" : "Not passed"} (required {result.passing_score}%)</p>
          <p>Your attempt has been saved to the database and will appear in My Results.</p>
        </header>
        <section className="learning-flow-section">
          <h2>Answer review</h2>
          {result.answers.map((answer, index) => (
            <article className="learning-flow-panel" key={answer.question_id}>
              <h3>{index + 1}. {answer.question}</h3>
              <p>Your answer: {answer.selected_option === null ? "Not answered" : answer.options[answer.selected_option]}</p>
              <p>Correct answer: <strong>{answer.options[answer.correct_option]}</strong></p>
              <p>{answer.explanation}</p>
            </article>
          ))}
        </section>
        <div className="learning-flow-actions">
          <button className="learning-flow-button" onClick={() => navigate("/my-results")}>View saved results</button>
          <button className="learning-flow-button secondary" onClick={() => navigate("/assessments")}>Back to assessments</button>
        </div>
      </div>
    );
  }

  return (
    <div className="learning-flow-page">
      <button className="learning-flow-link" onClick={() => navigate("/assessments")}>← Assessments</button>
      <header className="learning-flow-header">
        <p className="learning-flow-eyebrow">{assessment.module_title}</p>
        <h1>{assessment.title}</h1>
        <p>{assessment.description}</p>
        <p className="learning-flow-timer">Time remaining: {formatTime(timeLeft)}</p>
        <p>{assessment.questions.length} questions · Pass mark {assessment.passing_score}%</p>
      </header>
      {error && (
        <div className="learning-flow-error" role="alert">
          <p>{error}</p>
          <button
            className="learning-flow-button secondary"
            type="button"
            disabled={submitting}
            onClick={() => {
              submissionStarted.current = false;
              setAutoSubmitFailed(false);
              submitAssessment();
            }}
          >
            Retry submission
          </button>
        </div>
      )}
      <form onSubmit={(event) => { event.preventDefault(); submitAssessment(); }}>
        <section className="learning-flow-section">
          {assessment.questions.map((question, index) => (
            <article className="learning-flow-panel" key={question.id}>
              <h3>{index + 1}. {question.question}</h3>
              <div className="learning-flow-options">
                {question.options.map((option, optionIndex) => (
                  <label className="learning-flow-option" key={optionIndex}>
                    <input
                      type="radio"
                      name={`question-${question.id}`}
                      value={optionIndex}
                      checked={answers[question.id] === optionIndex}
                      onChange={() => setAnswers((current) => ({ ...current, [question.id]: optionIndex }))}
                      disabled={submitting}
                    />
                    <span>{option}</span>
                  </label>
                ))}
              </div>
            </article>
          ))}
        </section>
        <button className="learning-flow-button" type="submit" disabled={submitting}>
          {submitting ? "Submitting…" : "Submit assessment"}
        </button>
      </form>
      <p className="learning-flow-disclaimer">Correct answers are checked by the server and are not sent to the browser before submission.</p>
    </div>
  );
}

export default AssessmentDetails;
