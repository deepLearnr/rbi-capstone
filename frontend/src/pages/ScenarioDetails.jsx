import React, { useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import "../styles/ScenarioDetails.css";

function ScenarioDetails() {
  const navigate = useNavigate();
  const { id } = useParams();

  const questions = [
    {
      category: "CYBER SECURITY",
      icon: "🔐",
      title: "Suspicious Email",
      situation:
        "You receive an email that appears to come from an official source. The email asks you to click a link and provide confidential information.",
      question: "What should you do?",
      options: [
        "Click the link and verify the information",
        "Share the requested information",
        "Follow the organization's security procedure and report the suspicious email through the appropriate channel",
        "Forward the email to colleagues",
      ],
      correctAnswer: 2,
      explanation:
        "Follow the organization's approved security procedure when handling suspicious communications.",
      learning: "Cyber Security → Phishing Awareness",
    },
    {
      category: "CYBER SECURITY",
      icon: "🔐",
      title: "Unknown USB Device",
      situation:
        "You find an unknown USB device near your workstation. You are unsure who owns it.",
      question: "What should you do?",
      options: [
        "Connect it to your computer to identify the owner",
        "Give it to a colleague to check",
        "Report it through the organization's security procedure",
        "Use it only on a personal computer",
      ],
      correctAnswer: 2,
      explanation:
        "Unknown devices should not be connected to organizational systems. Report them through the approved security process.",
      learning: "Cyber Security → Device Security",
    },
    {
      category: "CYBER SECURITY",
      icon: "🔐",
      title: "Password Security",
      situation:
        "A colleague asks you to share your system password because they need quick access to complete a task.",
      question: "What should you do?",
      options: [
        "Share your password because the colleague is trusted",
        "Write the password on a note",
        "Refuse to share it and follow the approved access process",
        "Send the password through email",
      ],
      correctAnswer: 2,
      explanation:
        "Passwords must remain confidential. Access should be provided through the organization's approved access process.",
      learning: "Cyber Security → Password & Access Security",
    },
    {
      category: "COMPLIANCE",
      icon: "📋",
      title: "Customer Information",
      situation:
        "A person outside your team asks you to send customer information for an unofficial purpose.",
      question: "What should you do?",
      options: [
        "Send the information immediately",
        "Share only some of the information",
        "Verify authorization and follow the approved data-sharing procedure",
        "Forward the request to another employee",
      ],
      correctAnswer: 2,
      explanation:
        "Customer information should only be shared with authorized people through approved procedures.",
      learning: "Compliance → Data Protection",
    },
    {
      category: "RISK",
      icon: "⚠️",
      title: "Unusual Transaction",
      situation:
        "You notice an unusual transaction that does not match the normal pattern of activity.",
      question: "What should you do?",
      options: [
        "Ignore it because it may be normal",
        "Discuss it with friends",
        "Report it through the appropriate internal process",
        "Delete the transaction record",
      ],
      correctAnswer: 2,
      explanation:
        "Unusual activity should be reported through the organization's approved risk and fraud reporting process.",
      learning: "Risk Management → Fraud Awareness",
    },
  ];

  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [selectedAnswer, setSelectedAnswer] = useState(null);
  const [submitted, setSubmitted] = useState(false);
  const [score, setScore] = useState(0);
  const [completed, setCompleted] = useState(false);
  const [answers, setAnswers] = useState([]);

  const question = questions[currentQuestion];

  const handleSubmit = () => {
    if (selectedAnswer === null) {
      return;
    }

    const isCorrect = selectedAnswer === question.correctAnswer;

    if (isCorrect) {
      setScore((prev) => prev + 1);
    }

    setAnswers((prev) => [
      ...prev,
      {
        question: currentQuestion + 1,
        selected: selectedAnswer,
        correct: question.correctAnswer,
        isCorrect,
      },
    ]);

    setSubmitted(true);
  };

  const handleNext = () => {
    if (currentQuestion === questions.length - 1) {
      setCompleted(true);
      return;
    }

    setCurrentQuestion((prev) => prev + 1);
    setSelectedAnswer(null);
    setSubmitted(false);
  };

  const handleTryAgain = () => {
    setCurrentQuestion(0);
    setSelectedAnswer(null);
    setSubmitted(false);
    setScore(0);
    setCompleted(false);
    setAnswers([]);
  };

  const handleReview = () => {
    alert("Review Answers feature can be connected here.");
  };

  if (completed) {
    const finalScore = score;
    const percentage = (finalScore / questions.length) * 100;

    return (
      <div className="scenario-result-page">
        <div className="scenario-result-card">
          <div className="result-icon">🎯</div>

          <h1>Scenario Complete</h1>

          <div className="result-score">
            {finalScore} / {questions.length}
          </div>

          <div className="result-percentage">{percentage}%</div>

          <div className="result-details">
            <div>
              <span>Questions Answered</span>
              <strong>{questions.length}</strong>
            </div>

            <div>
              <span>Correct Answers</span>
              <strong>{finalScore}</strong>
            </div>

            <div>
              <span>Time Taken</span>
              <strong>04:32</strong>
            </div>
          </div>

          <div className="result-progress">
            <div
              className="result-progress-fill"
              style={{ width: `${percentage}%` }}
            ></div>
          </div>

          <div className="result-progress-text">{percentage}% Complete</div>

          <div className="result-actions">
            <button className="review-btn" onClick={handleReview}>
              Review Answers
            </button>

            <button className="try-again-btn" onClick={handleTryAgain}>
              Try Again
            </button>
          </div>

          <button
            className="continue-learning-btn"
            onClick={() => navigate("/learning/4")}
          >
            Continue Learning →
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="scenario-details-page">
      {/* Header */}
      <div className="scenario-top-header">
        <div className="scenario-title">
          🎯 Scenario {String(id).padStart(2, "0")}
        </div>

        <div className="question-count">
          Question {currentQuestion + 1} of {questions.length}
        </div>
      </div>

      {/* Progress */}
      <div className="scenario-progress">
        <div
          className="scenario-progress-fill"
          style={{
            width: `${((currentQuestion + 1) / questions.length) * 100}%`,
          }}
        ></div>
      </div>

      <div className="scenario-content">
        {/* Category */}
        <div className="scenario-category">
          <span>{question.icon}</span>
          {question.category}
        </div>

        {/* Title */}
        <h1>{question.title}</h1>

        {/* Situation */}
        <div className="scenario-situation">
          <p>{question.situation}</p>
        </div>

        {/* Question */}
        <h2>{question.question}</h2>

        {/* Options */}
        <div className="scenario-options">
          {question.options.map((option, index) => {
            let optionClass = "scenario-option";

            if (selectedAnswer === index) {
              optionClass += " selected";
            }

            if (submitted) {
              if (index === question.correctAnswer) {
                optionClass += " correct";
              } else if (
                index === selectedAnswer &&
                index !== question.correctAnswer
              ) {
                optionClass += " wrong";
              }
            }

            return (
              <button
                key={index}
                className={optionClass}
                onClick={() => {
                  if (!submitted) {
                    setSelectedAnswer(index);
                  }
                }}
                disabled={submitted}
              >
                <span className="option-radio">
                  {submitted && index === question.correctAnswer
                    ? "✓"
                    : submitted &&
                        index === selectedAnswer &&
                        index !== question.correctAnswer
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

        {/* Feedback */}
        {submitted && (
          <div className="scenario-feedback">
            <div className="feedback-heading">
              <span>✓</span>
              <h3>Answer Submitted</h3>
            </div>

            <p>Your response has been recorded.</p>

            <div className="feedback-why">
              <strong>💡 Why?</strong>

              <p>{question.explanation}</p>
            </div>

            <div className="related-learning">
              <strong>📚 Related Learning</strong>

              <p>{question.learning}</p>
            </div>

            <button className="next-question-btn" onClick={handleNext}>
              {currentQuestion === questions.length - 1
                ? "View Result →"
                : "Next Question →"}
            </button>
          </div>
        )}

        {/* Submit */}
        {!submitted && (
          <div className="submit-container">
            <button
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
