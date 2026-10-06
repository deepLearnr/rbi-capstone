import React from "react";

function AssessmentCard() {
  return (
    <div className="assessment-card">
      <div className="assessment-icon">📝</div>

      <div className="assessment-info">
        <h3>AML Assessment</h3>

        <div className="assessment-meta">
          <span>📅 Due: 28 Sep 2026</span>

          <span>❓ 20 Questions</span>
        </div>
      </div>

      <button className="start-btn">Start</button>
    </div>
  );
}

export default AssessmentCard;
