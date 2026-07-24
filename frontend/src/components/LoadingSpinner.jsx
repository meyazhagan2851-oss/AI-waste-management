import React from "react";

/** LoadingSpinner: shown while async requests (upload, prediction, fetch) are in flight. */
const LoadingSpinner = ({ label = "Loading..." }) => (
  <div className="loading-wrap">
    <div className="spinner" />
    <p>{label}</p>
  </div>
);

export default LoadingSpinner;
