import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import "../styles/AskSaathi.css";

function AskSaathi() {
  const navigate = useNavigate();
  const [question, setQuestion] = useState("");
  const [role, setRole] = useState(() => {
    const saved = localStorage.getItem("rbiSaathiRole");
    return ["bank_employee", "compliance_officer", "branch_manager", "customer_support"].includes(saved)
      ? saved
      : "bank_employee";
  });

  const roleOptions = [
    { value: "bank_employee", label: "Bank employee" },
    { value: "compliance_officer", label: "Compliance officer" },
    { value: "branch_manager", label: "Branch manager" },
    { value: "customer_support", label: "Customer support" },
  ];

  const handleRoleChange = (event) => {
    const nextRole = event.target.value;
    setRole(nextRole);
    localStorage.setItem("rbiSaathiRole", nextRole);
  };

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
        role,
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

        <div style={{ margin: "0 auto 1rem", maxWidth: "34rem", textAlign: "left" }}>
          <label htmlFor="assistant-role" style={{ display: "block", marginBottom: "0.4rem", fontWeight: 600 }}>
            Answer perspective
          </label>
          <select
            id="assistant-role"
            value={role}
            onChange={handleRoleChange}
            style={{ width: "100%", padding: "0.75rem", borderRadius: "0.5rem" }}
          >
            {roleOptions.map((option) => (
              <option key={option.value} value={option.value}>{option.label}</option>
            ))}
          </select>
          <p style={{ margin: "0.4rem 0 0", fontSize: "0.85rem" }}>
            This changes the explanation's framing, not RBI requirements or evidence standards.
          </p>
        </div>

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
