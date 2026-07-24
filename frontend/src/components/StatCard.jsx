import React from "react";

/**
 * StatCard
 * --------
 * Displays a single dashboard metric (e.g. total predictions, full bins)
 * with an icon and colored accent.
 */
const StatCard = ({ icon, iconClass, label, value }) => (
  <div className="stat-card">
    <div className={`stat-icon ${iconClass}`}>{icon}</div>
    <div className="stat-value">{value}</div>
    <div className="stat-label">{label}</div>
  </div>
);

export default StatCard;
