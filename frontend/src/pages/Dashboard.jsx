import React, { useEffect, useState } from "react";

import StatCard from "../components/StatCard";
import ContinueLearning from "../components/ContinueLearning";
import RegulatoryUpdates from "./RegulatoryUpdates";
import AssessmentCard from "../components/AssessmentCard";
import CourseCard from "../components/CourseCard";

import "../styles/Dashboard.css";

function Dashboard() {
  const [greeting, setGreeting] = useState("Good Morning");

  // Dynamic greeting based on current time
  useEffect(() => {
    const updateGreeting = () => {
      const hour = new Date().getHours();

      if (hour >= 5 && hour < 12) {
        setGreeting("Good Morning");
      } else if (hour >= 12 && hour < 17) {
        setGreeting("Good Afternoon");
      } else {
        setGreeting("Good Evening");
      }
    };

    updateGreeting();

    // Update every minute
    const interval = setInterval(updateGreeting, 60000);

    return () => clearInterval(interval);
  }, []);

  // Dashboard statistics
  const stats = [
    {
      title: "Learning",
      value: "08",
      icon: "📚",
    },
    {
      title: "Completed",
      value: "05",
      icon: "✅",
    },
    {
      title: "Pending",
      value: "03",
      icon: "⏳",
    },
    {
      title: "Progress",
      value: "72%",
      icon: "📈",
    },
  ];

  // Recommended courses
  const courses = [
    {
      title: "Digital Banking & Security",
      category: "Banking",
      duration: "2h 30m",
      progress: 45,
    },
    {
      title: "Customer Service Excellence",
      category: "Professional Skills",
      duration: "1h 45m",
      progress: 25,
    },
    {
      title: "RBI Guidelines & Compliance",
      category: "Compliance",
      duration: "3h 10m",
      progress: 10,
    },
  ];

  return (
    <div className="dashboard">
      {/* =========================
          WELCOME SECTION
      ========================= */}
      <section className="welcome-section">
        <h1>{greeting}, Siddhu 👋</h1>

        <p>
          Welcome back to <strong>RBI SAATHI</strong>
        </p>
      </section>

      {/* =========================
          STATISTICS
      ========================= */}
      <section className="stats-grid">
        {stats.map((stat) => (
          <StatCard
            key={stat.title}
            title={stat.title}
            value={stat.value}
            icon={stat.icon}
          />
        ))}
      </section>

      {/* =========================
          CONTINUE LEARNING + UPDATES
      ========================= */}
      <section className="dashboard-two-column">
        <ContinueLearning />

        {/* <RegulatoryUpdates /> */}
      </section>

      {/* =========================
          UPCOMING ASSESSMENTS
      ========================= */}
      <section className="dashboard-section">
        <div className="section-heading">
          <h2>Upcoming Assessments</h2>
        </div>

        <AssessmentCard />
      </section>

      {/* =========================
          RECOMMENDED COURSES
      ========================= */}
      <section className="dashboard-section">
        <div className="section-heading">
          <h2>Recommended For You</h2>

          <button className="view-all-btn">View All</button>
        </div>

        <div className="course-grid">
          {courses.map((course) => (
            <CourseCard
              key={course.title}
              title={course.title}
              category={course.category}
              duration={course.duration}
              progress={course.progress}
            />
          ))}
        </div>
      </section>
    </div>
  );
}

export default Dashboard;
