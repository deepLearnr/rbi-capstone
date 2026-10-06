import React from "react";

function CourseCard({ title, category, duration, progress }) {
  return (
    <div className="course-card">
      <div className="course-image">📚</div>

      <div className="course-card-content">
        <span className="course-category">{category}</span>

        <h3>{title}</h3>

        <div className="course-duration">⏱ {duration}</div>

        <div className="course-progress">
          <div className="progress-text">
            <span>Progress</span>
            <span>{progress}%</span>
          </div>

          <div className="progress-bar">
            <div
              className="progress-fill"
              style={{
                width: `${progress}%`,
              }}
            ></div>
          </div>
        </div>

        <button className="course-btn">Start Learning</button>
      </div>
    </div>
  );
}

export default CourseCard;
