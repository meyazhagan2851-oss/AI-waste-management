import React from "react";
import { FaCheckCircle, FaAdjust, FaExclamationCircle } from "react-icons/fa";

/**
 * PredictionBadge
 * ----------------
 * Renders a color-coded badge/pill for a bin status: Empty, Half Full, Full.
 * `variant="badge"` gives the large pulse-animated badge (used on the
 * prediction result screen); `variant="pill"` gives a compact table pill.
 */
const CONFIG = {
  Empty: { icon: <FaCheckCircle />, badgeClass: "badge-empty", pillBg: "rgba(56,189,248,0.15)", pillColor: "#38bdf8" },
  "Half Full": { icon: <FaAdjust />, badgeClass: "badge-half", pillBg: "rgba(245,158,11,0.15)", pillColor: "#f59e0b" },
  Full: { icon: <FaExclamationCircle />, badgeClass: "badge-full", pillBg: "rgba(239,68,68,0.18)", pillColor: "#ef4444" },
};

const PredictionBadge = ({ prediction, variant = "badge" }) => {
  const config = CONFIG[prediction] || CONFIG["Empty"];

  if (variant === "pill") {
    return (
      <span
        className="status-pill"
        style={{ background: config.pillBg, color: config.pillColor }}
      >
        {prediction}
      </span>
    );
  }

  return (
    <div className={`result-badge ${config.badgeClass}`}>
      {config.icon} {prediction}
    </div>
  );
};

export default PredictionBadge;
