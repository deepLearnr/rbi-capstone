import React, { useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import {
  createScenarioAttemptId,
  getScenarioSession,
  saveScenarioSession,
  saveScenarioAttempt,
} from "../services/scenarioProgress";
import { getScenarioCategory } from "../data/scenarios";
import "../styles/ScenarioDetails.css";

function ScenarioDetails() {
  const navigate = useNavigate();
  const { id } = useParams();
  const scenario = getScenarioCategory(id);
  const questions = scenario?.questions ?? [];
  const storedSession = scenario ? getScenarioSession(id) : null;
  const savedSession =
    storedSession?.version === 2 &&
    Number.isInteger(storedSession.currentQuestion) &&
    storedSession.currentQuestion >= 0 &&
    storedSession.currentQuestion < questions.length &&
    Array.isArray(storedSession.answers) &&
    storedSession.answers.length <= questions.length
      ? storedSession
      : null;

  const [currentQuestion, setCurrentQuestion] = useState(
    savedSession?.currentQuestion ?? 0,
  );
  const [selectedAnswer, setSelectedAnswer] = useState(
    savedSession?.selectedAnswer ?? null,
  );
  const [submitted, setSubmitted] = useState(savedSession?.submitted ?? false);
  const [score, setScore] = useState(savedSession?.score ?? 0);
  const [completed, setCompleted] = useState(savedSession?.completed ?? false);
  const [answers, setAnswers] = useState(savedSession?.answers ?? []);
  const [reviewing, setReviewing] = useState(false);
  const persistSession = (session) =>
    saveScenarioSession(id, { version: 2, ...session });
  const question = questions[currentQuestion];

  const handleSubmit = () => {
    if (selectedAnswer === null || !question || submitted) return;

    const isCorrect = selectedAnswer === question.correctAnswer;
    const nextScore = score + (isCorrect ? 1 : 0);
    const nextAnswers = [
      ...answers,
      {
        question: currentQuestion + 1,
        title: question.title,
        selected: selectedAnswer,
        selectedText: question.options[selectedAnswer],
        correct: question.correctAnswer,
        correctText: question.options[question.correctAnswer],
        isCorrect,
      },
    ];

    setScore(nextScore);
    setAnswers(nextAnswers);
    setSubmitted(true);
    persistSession({
      currentQuestion,
      selectedAnswer,
      submitted: true,
      score: nextScore,
      completed: false,
      answers: nextAnswers,
    });
  };

  const handleNext = () => {
    if (currentQuestion === questions.length - 1) {
      const attempt = {
        id: createScenarioAttemptId(id),
        scenarioId: id,
        scenarioTitle: scenario.title,
        score,
        totalQuestions: questions.length,
        scorePercent: Math.round((score / questions.length) * 100),
        answers,
        completedAt: new Date().toISOString(),
      };
      saveScenarioAttempt(attempt);
      setCompleted(true);
      setReviewing(false);
      persistSession({
        currentQuestion,
        selectedAnswer,
        submitted: true,
        score,
        completed: true,
        answers,
      });
      return;
    }

    const nextQuestion = currentQuestion + 1;
    setCurrentQuestion(nextQuestion);
    setSelectedAnswer(null);
    setSubmitted(false);
    persistSession({
      currentQuestion: nextQuestion,
      selectedAnswer: null,
      submitted: false,
      score,
      completed: false,
      answers,
    });
  };

  const handleTryAgain = () => {
    setCurrentQuestion(0);
    setSelectedAnswer(null);
    setSubmitted(false);
    setScore(0);
    setCompleted(false);
    setAnswers([]);
    setReviewing(false);
    persistSession({
      currentQuestion: 0,
      selectedAnswer: null,
      submitted: false,
      score: 0,
      completed: false,
      answers: [],
    });
  };

  if (!scenario || questions.length === 0) {
    return (
      <div className="scenario-details-page">
        <div className="scenario-content">
          <h1>Scenario topic not found</h1>
          <p>This route does not match one of the available demo topic sets.</p>
          <button
            type="button"
            className="continue-learning-btn"
            onClick={() => navigate("/scenarios")}
          >
            Browse available scenarios
          </button>
        </div>
      </div>
    );
  }

  if (completed) {
    const percentage = Math.round((score / questions.length) * 100);

    return (
      <div className="scenario-result-page">
        <div className="scenario-result-card">
          <div className="result-icon">🎯</div>
          <h1>{scenario.title} Complete</h1>
          <div className="result-score">
            {score} / {questions.length}
          </div>
          <div className="result-percentage">{percentage}%</div>

          <div className="result-details">
            <div>
              <span>Questions Answered</span>
              <strong>{questions.length}</strong>
            </div>
            <div>
              <span>Correct Answers</span>
              <strong>{score}</strong>
            </div>
          </div>

          <div className="result-progress">
            <div
              className="result-progress-fill"
              style={{ width: `${percentage}%` }}
            />
          </div>
          <div className="result-progress-text">{percentage}% Complete</div>

          {reviewing && (
            <div
              className="scenario-review-list"
              role="region"
              aria-label="Answer review"
            >
              <h2>Answer Review</h2>
              {answers.map((answer) => (
                <div key={answer.question}>
                  <strong>
                    {answer.question}. {answer.title || `Question ${answer.question}`}
                  </strong>
                  <p>Your answer: {answer.selectedText ?? `Option ${answer.selected + 1}`}</p>
                  <p>Correct answer: {answer.correctText ?? `Option ${answer.correct + 1}`}</p>
                  <p>{answer.isCorrect ? "Correct" : "Incorrect"}</p>
                </div>
              ))}
            </div>
          )}

          <div className="result-actions">
            <button type="button" className="review-btn" onClick={() => setReviewing((previous) => !previous)}>
              {reviewing ? "Hide Review" : "Review Answers"}
            </button>
            <button type="button" className="try-again-btn" onClick={handleTryAgain}>
              Try Again
            </button>
          </div>
          <button
            type="button"
            className="continue-learning-btn"
            onClick={() => navigate("/learning")}
          >
            Continue Learning →
          </button>
          <p className="scenario-storage-note">
            This scenario result is saved in this browser only; it is not synced
            to the backend or across devices.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="scenario-details-page">
      <div className="scenario-top-header">
        <div className="scenario-title">{scenario.icon} {scenario.title} Practice</div>
        <div className="question-count">
          Question {currentQuestion + 1} of {questions.length}
        </div>
      </div>

      <p className="scenario-storage-note">
        Progress is saved in this browser only. It is not synchronized with the
        backend or across devices.
      </p>

      <div className="scenario-progress">
        <div
          className="scenario-progress-fill"
          style={{ width: `${((currentQuestion + 1) / questions.length) * 100}%` }}
        />
      </div>

      <div className="scenario-content">
        <div className="scenario-category">
          <span>{scenario.icon}</span>
          {question.category || scenario.category}
        </div>
        <h1>{question.title}</h1>
        <div className="scenario-situation">
          <p>{question.situation}</p>
        </div>
        <h2>{question.question}</h2>

        <div className="scenario-options">
          {question.options.map((option, index) => {
            let optionClass = "scenario-option";
            if (selectedAnswer === index) optionClass += " selected";
            if (submitted) {
              if (index === question.correctAnswer) optionClass += " correct";
              else if (index === selectedAnswer) optionClass += " wrong";
            }

            return (
              <button
                type="button"
                key={index}
                className={optionClass}
                onClick={() => {
                  if (submitted) return;
                  setSelectedAnswer(index);
                  persistSession({
                    currentQuestion,
                    selectedAnswer: index,
                    submitted: false,
                    score,
                    completed: false,
                    answers,
                  });
                }}
                disabled={submitted}
              >
                <span className="option-radio">
                  {submitted && index === question.correctAnswer
                    ? "✓"
                    : submitted && index === selectedAnswer
                      ? "✕"
                      : selectedAnswer === index
                        ? "●"
                        : "○"}
                </span>
                <span>
                  <strong>{String.fromCharCode(65 + index)}.</strong> {option}
                </span>
              </button>
            );
          })}
        </div>

        {submitted && (
          <div className="scenario-feedback">
            <div className="feedback-heading">
              <span>✓</span>
              <h3>Answer Submitted</h3>
            </div>
            <p>Your response has been evaluated.</p>
            <div className="feedback-why">
              <strong>💡 Why?</strong>
              <p>{question.explanation}</p>
            </div>
            <div className="related-learning">
              <strong>📚 Related Learning</strong>
              <p>{question.learning}</p>
            </div>
            <button type="button" className="next-question-btn" onClick={handleNext}>
              {currentQuestion === questions.length - 1 ? "View Result →" : "Next Question →"}
            </button>
          </div>
        )}

        {!submitted && (
          <div className="submit-container">
            <button
              type="button"
              className="submit-answer-btn"
              onClick={handleSubmit}
              disabled={selectedAnswer === null}
            >
              Submit Answer →
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

export default ScenarioDetails;
