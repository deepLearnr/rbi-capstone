import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import "../styles/AskSaathi.css";

function AskSaathi() {
  const navigate = useNavigate();
  const [question, setQuestion] = useState("");

  const suggestedQuestions = [
    {
      icon: "🏦",
      title: "Banking",
      question: "What is CRR?",
    },
    {
      icon: "📋",
      title: "Compliance",
      question: "What is KYC?",
    },
    {
      icon: "📢",
      title: "Regulations",
      question: "What are the latest regulations?",
    },
    {
      icon: "🔐",
      title: "Cyber Security",
      question: "What is phishing awareness?",
    },
    {
      icon: "📚",
      title: "Learning",
      question: "Explain banking compliance.",
    },
  ];

  const recentQuestions = [
    {
      question: "What is KYC?",
      date: "25 Sep 2026",
    },
    {
      question: "Explain the latest compliance update.",
      date: "24 Sep 2026",
    },
    {
      question: "What is phishing?",
      date: "22 Sep 2026",
    },
  ];

  const handleAsk = (text = question) => {
    const finalQuestion = text.trim();

    if (!finalQuestion) {
      return;
    }

    navigate("/ask-answer", {
      state: {
        question: finalQuestion,
      },
    });
  };

  return (
    <div className="ask-saathi-page">
      <div className="ask-saathi-header">
        <h1>💬 Ask</h1>
        <p>Get quick answers to your banking and learning questions.</p>
      </div>

      <div className="ask-main">
        <div className="ask-icon">💬</div>

        <h2>How can I help?</h2>

        <p className="ask-description">
          Ask about banking, regulations or learning.
        </p>

        {/* Question Input */}
        <div className="question-input-wrapper">
          <input
            type="text"
            placeholder="Type your question here..."
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter") {
                handleAsk();
              }
            }}
          />

          <button className="voice-button" type="button">
            🎤
          </button>

          <button
            className="ask-button"
            type="button"
            onClick={() => handleAsk()}
          >
            ➤
          </button>
        </div>

        {/* Suggested Questions */}
        <section className="suggested-section">
          <h3>💡 Suggested Questions</h3>

          <div className="suggested-grid">
            {suggestedQuestions.map((item, index) => (
              <button
                className="suggested-card"
                key={index}
                onClick={() => handleAsk(item.question)}
              >
                <span className="suggested-icon">{item.icon}</span>

                <div>
                  <strong>{item.title}</strong>
                  <p>{item.question}</p>
                </div>
              </button>
            ))}
          </div>
        </section>

        {/* Recent Questions */}
        <section className="recent-questions-section">
          <h3>🕘 Recent Questions</h3>

          <div className="recent-questions-list">
            {recentQuestions.map((item, index) => (
              <button
                className="recent-question"
                key={index}
                onClick={() => handleAsk(item.question)}
              >
                <span className="recent-question-text">{item.question}</span>

                <span className="recent-question-date">{item.date} →</span>
              </button>
            ))}
          </div>
        </section>
      </div>
    </div>
  );
}

export default AskSaathi;
