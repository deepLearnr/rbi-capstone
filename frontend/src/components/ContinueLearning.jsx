import React from "react";

function ContinueLearning() {
  return (
    <div className="continue-card">
      <div className="card-heading">
        <h2>Continue Learning</h2>
      </div>

      <div className="learning-content">
        <div className="course-thumbnail">📖</div>

        <div className="learning-details">
          <span className="course-label">Compliance</span>

          <h3>KYC & AML Fundamentals</h3>

          <p>
            Learn the fundamentals of KYC and Anti-Money Laundering regulations.
          </p>

          <div className="progress-info">
            <span>80% completed</span>
            <span>80%</span>
          </div>

          <div className="progress-bar">
            <div className="progress-fill" style={{ width: "80%" }}></div>
          </div>

          <button className="primary-btn">Continue Learning</button>
        </div>
      </div>
    </div>
  );
}

export default ContinueLearning;
