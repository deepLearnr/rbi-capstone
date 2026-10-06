import React from "react";

function StatCard({ title, value, icon }) {
  return (
    <div className="stat-card">
      <div className="stat-top">
        <span className="stat-title">{title}</span>

        <span className="stat-icon">{icon}</span>
      </div>

      <h2>{value}</h2>
    </div>
  );
}

export default StatCard;
