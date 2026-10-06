import React from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";

import Sidebar from "./components/Sidebar";
import Header from "./components/Header";

import Dashboard from "./pages/Dashboard";
import RegulatoryUpdates from "./pages/RegulatoryUpdates";
import RegulatoryDetails from "./pages/RegulatoryDetails";
import LearningPaths from "./pages/LearningPaths";
import CourseDetails from "./pages/CourseDetails";
import Scenarios from "./pages/Scenarios";
import ScenarioDetails from "./pages/ScenarioDetails";
import Assessments from "./pages/Assessments";
import AssessmentDetails from "./pages/AssessmentDetails";
import MyResults from "./pages/MyResults";
import AskSaathi from "./pages/AskSaathi";
import AskAnswer from "./pages/AskAnswer";
import Progress from "./pages/Progress";
import Profile from "./pages/Profile";
import Settings from "./pages/Settings";

import "./styles/Global.css";

function App() {
  return (
    <BrowserRouter>
      <div className="app">
        {/* Header */}
        <Header />

        <div className="app-body">
          {/* Sidebar */}
          <Sidebar />

          {/* Main Content */}
          <main className="main-content">
            <Routes>
              {/* Dashboard */}
              <Route path="/" element={<Dashboard />} />

              {/* Regulatory Updates */}
              <Route path="/updates" element={<RegulatoryUpdates />} />

              {/* Regulatory Update Details */}
              <Route path="/updates/:id" element={<RegulatoryDetails />} />

              {/* Learning Paths */}
              <Route path="/learning" element={<LearningPaths />} />

              {/* Course Details */}
              <Route path="/learning/:id" element={<CourseDetails />} />

              {/* Scenarios */}
              <Route path="/scenarios" element={<Scenarios />} />

              {/* Scenario Details / Quiz */}
              <Route path="/scenarios/:id" element={<ScenarioDetails />} />

              {/* Assessments */}
              <Route path="/assessments" element={<Assessments />} />

              {/* Assessment Details / Test */}
              <Route path="/assessments/:id" element={<AssessmentDetails />} />

              {/* My Results */}
              <Route path="/my-results" element={<MyResults />} />

              {/* Ask Saathi */}
              <Route path="/ask-saathi" element={<AskSaathi />} />

              {/* Ask Saathi Answer */}
              <Route path="/ask-answer" element={<AskAnswer />} />

              {/* Progress */}
              <Route path="/progress" element={<Progress />} />

              {/* Profile */}
              <Route path="/profile" element={<Profile />} />

              {/* Settings */}
              <Route path="/settings" element={<Settings />} />
            </Routes>
          </main>
        </div>
      </div>
    </BrowserRouter>
  );
}

export default App;
