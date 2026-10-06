import React from "react";
import { useLocation, useNavigate } from "react-router-dom";
import "../styles/Sidebar.css";

function Sidebar() {
  const navigate = useNavigate();
  const location = useLocation();

  const menuItems = [
    {
      icon: "🏠",
      label: "Dashboard",
      path: "/",
    },
    {
      icon: "📢",
      label: "Updates",
      path: "/updates",
    },
    {
      icon: "🗺️",
      label: "Learning",
      path: "/learning",
    },

    {
      icon: "🎯",
      label: "Scenarios",
      path: "/scenarios",
    },
    {
      icon: "📝",
      label: "Assessments",
      path: "/assessments",
    },
    {
      icon: "💬",
      label: "Ask Saathi",
      path: "/ask-saathi",
    },
    {
      icon: "📊",
      label: "Progress",
      path: "/progress",
    },
    {
      icon: "👤",
      label: "Profile",
      path: "/profile",
    },
    {
      icon: "⚙️",
      label: "Settings",
      path: "/settings",
    },
  ];

  return (
    <aside className="sidebar">
      <nav className="sidebar-menu">
        {menuItems.map((item) => {
          const isActive = location.pathname === item.path;

          return (
            <button
              key={item.label}
              className={`sidebar-item ${isActive ? "active" : ""}`}
              onClick={() => navigate(item.path)}
            >
              <span className="sidebar-icon">{item.icon}</span>

              <span>{item.label}</span>
            </button>
          );
        })}
      </nav>
    </aside>
  );
}

export default Sidebar;
