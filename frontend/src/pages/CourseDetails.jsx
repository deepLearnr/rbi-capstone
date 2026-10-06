import React from "react";
import { useNavigate, useParams } from "react-router-dom";
import "../styles/CourseDetails.css";

function CourseDetails() {
  const navigate = useNavigate();
  const { id } = useParams();

  const learningPaths = [
    {
      id: 1,
      title: "Core Banking",
      icon: "🏦",
      courses: 8,
      duration: "6 Hours",
      level: "Beginner",
    },
    {
      id: 2,
      title: "Regulatory & Compliance",
      icon: "📋",
      courses: 6,
      duration: "4 Hours",
      level: "Beginner",
    },
    {
      id: 3,
      title: "Risk Management",
      icon: "⚠️",
      courses: 5,
      duration: "3 Hours",
      level: "Intermediate",
    },
    {
      id: 4,
      title: "Cyber Security",
      icon: "🔐",
      courses: 5,
      duration: "3 Hours",
      level: "Beginner",
    },
    {
      id: 5,
      title: "Digital Banking",
      icon: "💻",
      courses: 7,
      duration: "5 Hours",
      level: "Intermediate",
    },
    {
      id: 6,
      title: "Role-Based Learning",
      icon: "👔",
      courses: 10,
      duration: "8 Hours",
      level: "Advanced",
    },
  ];

  const courseData = {
    1: [
      {
        id: 1,
        title: "Introduction to Core Banking",
        type: "📹 Video",
        duration: "30 min",
        status: "Not Started",
        action: "Start Learning →",
      },
      {
        id: 2,
        title: "Core Banking Operations",
        type: "📄 Reading",
        duration: "45 min",
        status: "In Progress — 40%",
        action: "Continue →",
      },
      {
        id: 3,
        title: "Banking Products & Services",
        type: "🎥 Video + Quiz",
        duration: "60 min",
        status: "Not Started",
        action: "Start Learning →",
      },
    ],

    2: [
      {
        id: 1,
        title: "Introduction to Regulatory Compliance",
        type: "📹 Video",
        duration: "30 min",
        status: "Not Started",
        action: "Start Learning →",
      },
      {
        id: 2,
        title: "KYC Fundamentals",
        type: "📄 Reading",
        duration: "45 min",
        status: "In Progress — 40%",
        action: "Continue →",
      },
      {
        id: 3,
        title: "AML Awareness",
        type: "🎥 Video + Quiz",
        duration: "60 min",
        status: "Not Started",
        action: "Start Learning →",
      },
    ],

    3: [
      {
        id: 1,
        title: "Introduction to Risk Management",
        type: "📹 Video",
        duration: "30 min",
        status: "Not Started",
        action: "Start Learning →",
      },
      {
        id: 2,
        title: "Credit Risk Fundamentals",
        type: "📄 Reading",
        duration: "45 min",
        status: "In Progress — 40%",
        action: "Continue →",
      },
      {
        id: 3,
        title: "Operational Risk",
        type: "🎥 Video + Quiz",
        duration: "60 min",
        status: "Not Started",
        action: "Start Learning →",
      },
    ],

    4: [
      {
        id: 1,
        title: "Cyber Security Basics",
        type: "📹 Video",
        duration: "30 min",
        status: "Not Started",
        action: "Start Learning →",
      },
      {
        id: 2,
        title: "Password & Access Security",
        type: "📄 Reading",
        duration: "45 min",
        status: "In Progress — 40%",
        action: "Continue →",
      },
      {
        id: 3,
        title: "Phishing Awareness",
        type: "🎥 Video + Quiz",
        duration: "60 min",
        status: "Not Started",
        action: "Start Learning →",
      },
    ],

    5: [
      {
        id: 1,
        title: "Introduction to Digital Banking",
        type: "📹 Video",
        duration: "30 min",
        status: "Not Started",
        action: "Start Learning →",
      },
      {
        id: 2,
        title: "Digital Payment Systems",
        type: "📄 Reading",
        duration: "45 min",
        status: "In Progress — 40%",
        action: "Continue →",
      },
      {
        id: 3,
        title: "Digital Banking Security",
        type: "🎥 Video + Quiz",
        duration: "60 min",
        status: "Not Started",
        action: "Start Learning →",
      },
    ],

    6: [
      {
        id: 1,
        title: "Role Based Banking Fundamentals",
        type: "📹 Video",
        duration: "30 min",
        status: "Not Started",
        action: "Start Learning →",
      },
      {
        id: 2,
        title: "Employee Responsibilities",
        type: "📄 Reading",
        duration: "45 min",
        status: "In Progress — 40%",
        action: "Continue →",
      },
      {
        id: 3,
        title: "Role Based Assessment",
        type: "🎥 Video + Quiz",
        duration: "60 min",
        status: "Not Started",
        action: "Start Learning →",
      },
    ],
  };

  const selectedPath = learningPaths.find((path) => path.id === Number(id));

  const courses = courseData[id] || [];

  if (!selectedPath) {
    return (
      <div className="course-not-found">
        <h2>Learning Path Not Found</h2>

        <button onClick={() => navigate("/learning")}>
          ← Back to Learning Paths
        </button>
      </div>
    );
  }

  return (
    <div className="course-details-page">
      {/* Back Button */}
      <button
        className="course-back-button"
        onClick={() => navigate("/learning")}
      >
        ← Back to Learning Paths
      </button>

      {/* Learning Path Header */}
      <div className="course-path-header">
        <div className="course-path-icon">{selectedPath.icon}</div>

        <div>
          <h1>{selectedPath.title}</h1>

          <div className="course-path-meta">
            <span>📚 {selectedPath.courses} Courses</span>

            <span>⏱️ {selectedPath.duration}</span>

            <span>🎯 {selectedPath.level}</span>
          </div>
        </div>
      </div>

      <div className="course-divider"></div>

      {/* Courses */}
      <section className="courses-section">
        <h2>Courses</h2>

        <div className="courses-list">
          {courses.map((course, index) => (
            <div className="course-item" key={course.id}>
              <div className="course-number">Course {index + 1}</div>

              <div className="course-content">
                <h3>{course.title}</h3>

                <div className="course-info">
                  <span>{course.type}</span>

                  <span>⏱️ {course.duration}</span>
                </div>

                <div
                  className={`course-status ${
                    course.status.includes("In Progress")
                      ? "in-progress"
                      : "not-started"
                  }`}
                >
                  {course.status}
                </div>

                <div className="course-action">
                  <button
                    onClick={() =>
                      navigate(`/learning/${id}/course/${course.id}`)
                    }
                  >
                    {course.action}
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}

export default CourseDetails;
