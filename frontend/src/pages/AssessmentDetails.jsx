import React, { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import "../styles/AssessmentDetails.css";

function AssessmentDetails() {
  const navigate = useNavigate();
  const { id } = useParams();

  const assessmentData = {
    1: {
      title: "Regulatory Compliance Assessment",
      totalQuestions: 20,
      duration: 20 * 60,
      passingScore: 70,
      recommended: "Risk Management",
    },
    2: {
      title: "Cyber Security Assessment",
      totalQuestions: 15,
      duration: 15 * 60,
      passingScore: 70,
      recommended: "Digital Banking",
    },
  };

  const assessment = assessmentData[id] || assessmentData[1];

  /*
   * Questions
   * The same structure can later be replaced with API data.
   */
  const questions = [
    {
      question: "Which area is being tested in this assessment?",
      options: [
        "Banking Operations",
        "Regulatory Compliance",
        "Digital Marketing",
        "Human Resources",
      ],
      answer: 1,
    },
    {
      question: "What is the main purpose of regulatory compliance?",
      options: [
        "To increase marketing activities",
        "To ensure rules and regulations are followed",
        "To reduce employee training",
        "To increase website traffic",
      ],
      answer: 1,
    },
    {
      question: "Which activity helps an organization maintain compliance?",
      options: [
        "Ignoring regulatory changes",
        "Following approved policies and procedures",
        "Sharing confidential information",
        "Avoiding internal controls",
      ],
      answer: 1,
    },
    {
      question: "Why are customer records protected?",
      options: [
        "To improve advertisements",
        "To protect confidential customer information",
        "To increase office attendance",
        "To reduce system performance",
      ],
      answer: 1,
    },
    {
      question:
        "What should an employee do when a new regulation is introduced?",
      options: [
        "Ignore it",
        "Follow the updated approved procedure",
        "Share it publicly",
        "Delete old records",
      ],
      answer: 1,
    },
    {
      question: "What does KYC generally help an organization understand?",
      options: [
        "Customer identity",
        "Employee salary",
        "Office attendance",
        "Marketing budget",
      ],
      answer: 0,
    },
    {
      question: "Which practice supports data protection?",
      options: [
        "Sharing passwords",
        "Using approved access controls",
        "Leaving systems unlocked",
        "Sending data to unknown users",
      ],
      answer: 1,
    },
    {
      question: "What is an internal control?",
      options: [
        "A business advertisement",
        "A process designed to manage risks and ensure proper operations",
        "A social media post",
        "A customer complaint",
      ],
      answer: 1,
    },
    {
      question: "Who should handle confidential customer information?",
      options: [
        "Any person",
        "Only authorized employees",
        "External friends",
        "Public users",
      ],
      answer: 1,
    },
    {
      question:
        "What should you do if you identify a possible compliance issue?",
      options: [
        "Ignore it",
        "Report it through the approved internal process",
        "Delete the evidence",
        "Post it online",
      ],
      answer: 1,
    },
    {
      question: "What is the purpose of maintaining proper records?",
      options: [
        "To support accountability and compliance",
        "To reduce security",
        "To avoid audits",
        "To remove controls",
      ],
      answer: 0,
    },
    {
      question: "Which action can create a compliance risk?",
      options: [
        "Following company policy",
        "Sharing confidential information without authorization",
        "Completing required training",
        "Reporting suspicious activity",
      ],
      answer: 1,
    },
    {
      question: "What is an audit mainly used for?",
      options: [
        "Checking whether controls and processes are working properly",
        "Creating advertisements",
        "Hiring employees",
        "Designing websites",
      ],
      answer: 0,
    },
    {
      question: "Why is employee training important for compliance?",
      options: [
        "It helps employees understand their responsibilities",
        "It removes all company policies",
        "It replaces security controls",
        "It avoids customer verification",
      ],
      answer: 0,
    },
    {
      question: "What should happen to sensitive information?",
      options: [
        "It should be protected using approved security measures",
        "It should be shared with everyone",
        "It should be posted publicly",
        "It should be stored without access control",
      ],
      answer: 0,
    },
    {
      question: "What does AML generally refer to?",
      options: [
        "Account Management Login",
        "Anti-Money Laundering",
        "Application Management Language",
        "Automated Marketing List",
      ],
      answer: 1,
    },
    {
      question:
        "What is the safest approach when you are unsure about a compliance requirement?",
      options: [
        "Guess and continue",
        "Ask the appropriate authorized team or check the approved guidance",
        "Ignore the requirement",
        "Share the information externally",
      ],
      answer: 1,
    },
    {
      question: "Which is an example of good compliance behavior?",
      options: [
        "Following approved procedures",
        "Sharing login credentials",
        "Ignoring suspicious activity",
        "Bypassing controls",
      ],
      answer: 0,
    },
    {
      question: "Why should access to sensitive data be limited?",
      options: [
        "To reduce unauthorized access",
        "To increase public access",
        "To remove accountability",
        "To reduce employee training",
      ],
      answer: 0,
    },
    {
      question: "What should employees do with updated compliance guidance?",
      options: [
        "Ignore the changes",
        "Understand and follow the updated guidance",
        "Share it on social media",
        "Delete the guidance",
      ],
      answer: 1,
    },
  ];

  const totalQuestions = Math.min(assessment.totalQuestions, questions.length);

  const testQuestions = questions.slice(0, totalQuestions);

  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [answers, setAnswers] = useState(Array(totalQuestions).fill(null));

  const [timeLeft, setTimeLeft] = useState(assessment.duration);

  const [showSubmitModal, setShowSubmitModal] = useState(false);

  const [completed, setCompleted] = useState(false);

  const [reviewMode, setReviewMode] = useState(false);

  const [timeTaken, setTimeTaken] = useState(0);

  /* Timer */

  useEffect(() => {
    if (completed) return;

    if (timeLeft <= 0) {
      handleSubmitAssessment();
      return;
    }

    const timer = setInterval(() => {
      setTimeLeft((prev) => prev - 1);
    }, 1000);

    return () => clearInterval(timer);
  }, [timeLeft, completed]);

  const formatTime = (seconds) => {
    const minutes = Math.floor(seconds / 60);
    const secs = seconds % 60;

    return `${String(minutes).padStart(
      2,
      "0",
    )}:${String(secs).padStart(2, "0")}`;
  };

  const selectAnswer = (answerIndex) => {
    const updatedAnswers = [...answers];

    updatedAnswers[currentQuestion] = answerIndex;

    setAnswers(updatedAnswers);
  };

  const goToQuestion = (index) => {
    setCurrentQuestion(index);
    setReviewMode(false);
  };

  const handleNext = () => {
    if (currentQuestion < totalQuestions - 1) {
      setCurrentQuestion((prev) => prev + 1);
    }
  };

  const handlePrevious = () => {
    if (currentQuestion > 0) {
      setCurrentQuestion((prev) => prev - 1);
    }
  };

  const handleSubmitAssessment = () => {
    const elapsedTime = assessment.duration - timeLeft;

    setTimeTaken(elapsedTime);
    setShowSubmitModal(false);
    setCompleted(true);
  };

  const calculateScore = () => {
    let correct = 0;

    answers.forEach((answer, index) => {
      if (answer !== null && answer === testQuestions[index].answer) {
        correct++;
      }
    });

    return correct;
  };

  const correctAnswers = calculateScore();

  const incorrectAnswers = answers.filter(
    (answer, index) =>
      answer !== null && answer !== testQuestions[index].answer,
  ).length;

  const answeredQuestions = answers.filter((answer) => answer !== null).length;

  const unansweredQuestions = totalQuestions - answeredQuestions;

  const percentage = Math.round((correctAnswers / totalQuestions) * 100);

  const passed = percentage >= assessment.passingScore;

  /*
   * RESULT SCREEN
   */

  if (completed && !reviewMode) {
    return (
      <div className="assessment-result-page">
        <div className="assessment-result-card">
          <div className="result-trophy">🎉</div>

          <h1>Assessment Completed</h1>

          <div className="final-score">{percentage}%</div>

          <div className={`result-status ${passed ? "passed" : "failed"}`}>
            {passed ? "✓ PASSED" : "✕ FAILED"}
          </div>

          <div className="result-info">
            <div>
              <span>Total Questions</span>
              <strong>{totalQuestions}</strong>
            </div>

            <div>
              <span>Correct Answers</span>
              <strong>{correctAnswers}</strong>
            </div>

            <div>
              <span>Incorrect Answers</span>
              <strong>{incorrectAnswers}</strong>
            </div>

            <div>
              <span>Time Taken</span>
              <strong>{formatTime(timeTaken)}</strong>
            </div>
          </div>

          <div className="result-progress">
            <div
              className="result-progress-fill"
              style={{
                width: `${percentage}%`,
              }}
            ></div>
          </div>

          <div className="result-progress-text">{percentage}%</div>

          <div className="result-buttons">
            <button
              className="review-result-btn"
              onClick={() => {
                setReviewMode(true);
                setCurrentQuestion(0);
              }}
            >
              Review Answers
            </button>

            <button
              className="back-assessment-btn"
              onClick={() => navigate("/assessments")}
            >
              Back to Assessments
            </button>
          </div>

          <div className="recommended-learning">
            <span>📚</span>

            <div>
              <strong>Recommended Learning</strong>

              <p>
                Continue with <b>{assessment.recommended}</b>
              </p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  /*
   * REVIEW SCREEN
   */

  if (completed && reviewMode) {
    const question = testQuestions[currentQuestion];
    const userAnswer = answers[currentQuestion];

    return (
      <div className="assessment-review-page">
        <div className="review-header">
          <div>
            <h1>Review Answers</h1>
            <p>{assessment.title}</p>
          </div>

          <button onClick={() => setReviewMode(false)}>← Back to Result</button>
        </div>

        <div className="review-layout">
          <div className="review-question-card">
            <div className="review-question-number">
              Question {currentQuestion + 1} of {totalQuestions}
            </div>

            <h2>{question.question}</h2>

            <div className="review-options">
              {question.options.map((option, index) => {
                const isCorrect = index === question.answer;

                const isSelected = index === userAnswer;

                let className = "review-option";

                if (isCorrect) {
                  className += " correct";
                }

                if (isSelected && !isCorrect) {
                  className += " wrong";
                }

                return (
                  <div key={index} className={className}>
                    <span>{String.fromCharCode(65 + index)}.</span>

                    <span>{option}</span>

                    {isCorrect && <strong>✓ Correct</strong>}

                    {isSelected && !isCorrect && <strong>✕ Your Answer</strong>}
                  </div>
                );
              })}
            </div>

            <div className="review-navigation">
              <button disabled={currentQuestion === 0} onClick={handlePrevious}>
                ← Previous
              </button>

              <button
                disabled={currentQuestion === totalQuestions - 1}
                onClick={handleNext}
              >
                Next →
              </button>
            </div>
          </div>

          <div className="review-palette">
            <h3>Question Navigator</h3>

            <div className="review-palette-grid">
              {testQuestions.map((_, index) => {
                const answered = answers[index] !== null;

                const correct =
                  answered && answers[index] === testQuestions[index].answer;

                return (
                  <button
                    key={index}
                    className={`review-number ${
                      index === currentQuestion ? "current" : ""
                    } ${
                      correct
                        ? "correct-number"
                        : answered
                          ? "wrong-number"
                          : ""
                    }`}
                    onClick={() => goToQuestion(index)}
                  >
                    {String(index + 1).padStart(2, "0")}
                  </button>
                );
              })}
            </div>
          </div>
        </div>
      </div>
    );
  }

  /*
   * TEST SCREEN
   */

  const question = testQuestions[currentQuestion];

  const progress = Math.round(((currentQuestion + 1) / totalQuestions) * 100);

  return (
    <div className="assessment-page">
      {/* Top Header */}

      <div className="assessment-top-header">
        <h1>{assessment.title}</h1>

        <span>
          Question {currentQuestion + 1} of {totalQuestions}
        </span>
      </div>

      <div className="assessment-layout">
        {/* Main Test */}

        <div className="assessment-main">
          <div className="progress-title">Progress</div>

          <div className="assessment-progress">
            <div
              className="assessment-progress-fill"
              style={{
                width: `${progress}%`,
              }}
            ></div>
          </div>

          <div className="progress-percent">{progress}%</div>

          <div className="question-card">
            <div className="question-number">
              Question {currentQuestion + 1}
            </div>

            <h2>{question.question}</h2>

            <div className="question-options">
              {question.options.map((option, index) => (
                <button
                  key={index}
                  className={`question-option ${
                    answers[currentQuestion] === index ? "selected" : ""
                  }`}
                  onClick={() => selectAnswer(index)}
                >
                  <span className="radio">
                    {answers[currentQuestion] === index ? "●" : "○"}
                  </span>

                  <span>
                    <b>{String.fromCharCode(65 + index)}.</b> {option}
                  </span>
                </button>
              ))}
            </div>

            <div className="question-actions">
              <button
                className="previous-btn"
                onClick={handlePrevious}
                disabled={currentQuestion === 0}
              >
                ← Previous
              </button>

              <button
                className="next-btn"
                onClick={handleNext}
                disabled={currentQuestion === totalQuestions - 1}
              >
                Next Question →
              </button>
            </div>

            <div className="timer">⏱️ {formatTime(timeLeft)} remaining</div>
          </div>
        </div>

        {/* Question Navigator */}

        <aside className="question-navigator">
          <h3>Question Navigator</h3>

          <div className="navigator-grid">
            {testQuestions.map((_, index) => {
              const answered = answers[index] !== null;

              return (
                <button
                  key={index}
                  className={`navigator-number ${
                    index === currentQuestion ? "current" : ""
                  } ${answered ? "answered" : ""}`}
                  onClick={() => goToQuestion(index)}
                >
                  <span>{String(index + 1).padStart(2, "0")}</span>

                  <span>
                    {index === currentQuestion ? "●" : answered ? "✓" : "○"}
                  </span>
                </button>
              );
            })}
          </div>

          <div className="navigator-legend">
            <div>
              <span>✓</span>
              Answered
            </div>

            <div>
              <span>●</span>
              Current
            </div>

            <div>
              <span>○</span>
              Not Answered
            </div>
          </div>

          <button
            className="submit-assessment-btn"
            onClick={() => setShowSubmitModal(true)}
          >
            Submit Assessment
          </button>
        </aside>
      </div>

      {/* Submit Modal */}

      {showSubmitModal && (
        <div className="modal-overlay">
          <div className="submit-modal">
            <h2>Submit Assessment?</h2>

            <div className="submission-summary">
              <div>
                <span>Answered:</span>
                <strong>
                  {answeredQuestions} / {totalQuestions}
                </strong>
              </div>

              <div>
                <span>Not Answered:</span>
                <strong>{unansweredQuestions}</strong>
              </div>
            </div>

            <p>Are you sure you want to submit?</p>

            <div className="modal-actions">
              <button
                className="cancel-btn"
                onClick={() => setShowSubmitModal(false)}
              >
                Cancel
              </button>

              <button
                className="confirm-submit-btn"
                onClick={handleSubmitAssessment}
              >
                Submit Assessment
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default AssessmentDetails;
