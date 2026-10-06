import React from "react";
import "../styles/Progress.css";

function Progress() {
  const learningPaths = [
    {
      name: "Regulatory & Compliance",
      progress: 85,
    },
    {
      name: "Core Banking",
      progress: 72,
    },
    {
      name: "Cyber Security",
      progress: 100,
    },
    {
      name: "Risk Management",
      progress: 50,
    },
    {
      name: "Digital Banking",
      progress: 75,
    },
  ];

  return (
    <div className="progress-page">
      {/* Page Header */}
      <div className="progress-header">
        <h1>My Progress</h1>
        <p>Track your learning journey and performance</p>
      </div>

      {/* Summary Cards */}
      <div className="progress-summary">
        <div className="progress-card">
          <span className="progress-card-title">
            Overall
            <br />
            Progress
          </span>

          <strong>72%</strong>
        </div>

        <div className="progress-card">
          <span className="progress-card-title">
            Courses
            <br />
            Completed
          </span>

          <strong>12</strong>
        </div>

        <div className="progress-card">
          <span className="progress-card-title">
            Learning
            <br />
            Hours
          </span>

          <strong>18h</strong>
        </div>

        <div className="progress-card">
          <span className="progress-card-title">
            Assessments
            <br />
            Average
          </span>

          <strong>82%</strong>
        </div>
      </div>

      {/* Overall Learning Progress */}
      <section className="overall-progress-section">
        <h2>📈 Overall Learning Progress</h2>

        <div className="overall-progress-card">
          <div className="overall-percentage">72%</div>

          <div className="large-progress-bar">
            <div className="large-progress-fill" style={{ width: "72%" }}></div>
          </div>

          <p>12 of 17 courses completed</p>
        </div>
      </section>

      {/* Learning Paths */}
      <section className="learning-paths-progress">
        <h2>📚 Learning Paths</h2>

        <div className="path-list">
          {learningPaths.map((path, index) => (
            <div className="path-item" key={index}>
              <div className="path-name">{path.name}</div>

              <div className="path-progress-wrapper">
                <div className="path-progress-bar">
                  <div
                    className="path-progress-fill"
                    style={{
                      width: `${path.progress}%`,
                    }}
                  ></div>
                </div>

                <span className="path-percentage">{path.progress}%</span>
              </div>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}

export default Progress;
