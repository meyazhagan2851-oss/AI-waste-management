import React from "react";
import { FaExclamationTriangle } from "react-icons/fa";

/** ErrorBanner: consistent error message display used across pages. */
const ErrorBanner = ({ message }) => {
  if (!message) return null;
  return (
    <div className="error-banner">
      <FaExclamationTriangle style={{ marginRight: 8 }} />
      {message}
    </div>
  );
};

export default ErrorBanner;
