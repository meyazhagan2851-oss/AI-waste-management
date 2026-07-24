import React, { useState, useRef } from "react";
import { FaCloudUploadAlt } from "react-icons/fa";
import { toast } from "react-toastify";

import LoadingSpinner from "../components/LoadingSpinner";
import ErrorBanner from "../components/ErrorBanner";
import PredictionBadge from "../components/PredictionBadge";
import { predictBinStatus } from "../services/api";

/**
 * UploadPredict
 * -------------
 * Lets the admin upload (or drag-and-drop) a bin photo, tag it with a
 * bin ID, and get back an AI classification with a confidence score.
 * Fires a toast alert immediately if the bin is predicted Full.
 */
const UploadPredict = () => {
  const [file, setFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [binId, setBinId] = useState("BIN-001");
  const [dragging, setDragging] = useState(false);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const fileInputRef = useRef(null);

  const handleFileSelect = (selected) => {
    if (!selected) return;
    if (!selected.type.startsWith("image/")) {
      setError("Please select a valid image file (JPG, PNG, WEBP).");
      return;
    }
    setError("");
    setResult(null);
    setFile(selected);
    setPreviewUrl(URL.createObjectURL(selected));
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragging(false);
    handleFileSelect(e.dataTransfer.files[0]);
  };

  const handleSubmit = async () => {
    if (!file) {
      setError("Please select an image before submitting.");
      return;
    }
    setLoading(true);
    setError("");
    setResult(null);
    try {
      const data = await predictBinStatus(file, binId || "BIN-001");
      setResult(data);
      if (data.is_alert) {
        toast.error(`🚨 ${data.bin_id} detected as FULL! Notify collection team.`);
      } else {
        toast.success(`Prediction complete: ${data.prediction}`);
      }
    } catch (err) {
      setError(err.response?.data?.detail || "Prediction failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const resetForm = () => {
    setFile(null);
    setPreviewUrl(null);
    setResult(null);
    setError("");
  };

  return (
    <div>
      <div className="page-header">
        <h1>Upload &amp; Predict</h1>
        <p>Upload a bin photo to classify its fill level using AI.</p>
      </div>

      <ErrorBanner message={error} />

      <div className="card">
        <label style={{ display: "block", marginBottom: 8, color: "var(--color-text-muted)" }}>
          Bin ID
        </label>
        <input
          className="input-field"
          style={{ marginBottom: 18, width: 220 }}
          value={binId}
          onChange={(e) => setBinId(e.target.value)}
          placeholder="e.g. BIN-001"
        />

        <div
          className={`upload-zone ${dragging ? "dragging" : ""}`}
          onClick={() => fileInputRef.current.click()}
          onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
          onDragLeave={() => setDragging(false)}
          onDrop={handleDrop}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            hidden
            onChange={(e) => handleFileSelect(e.target.files[0])}
          />
          <FaCloudUploadAlt className="upload-icon" />
          <p><strong>Click to upload</strong> or drag and drop</p>
          <p style={{ color: "var(--color-text-muted)", fontSize: "0.85rem" }}>
            JPG, PNG, or WEBP — up to 10MB
          </p>
        </div>

        {previewUrl && <img src={previewUrl} alt="Bin preview" className="preview-image" />}

        <div style={{ display: "flex", gap: 12, marginTop: 16 }}>
          <button className="btn btn-primary" onClick={handleSubmit} disabled={loading || !file}>
            {loading ? "Analyzing..." : "Run AI Prediction"}
          </button>
          <button className="btn btn-secondary" onClick={resetForm} disabled={loading}>
            Reset
          </button>
        </div>
      </div>

      {loading && <LoadingSpinner label="Running AI classification..." />}

      {result && !loading && (
        <div className="card" style={{ marginTop: 20 }}>
          <h3>Prediction Result</h3>
          <PredictionBadge prediction={result.prediction} />
          <p style={{ marginTop: 16, marginBottom: 4, color: "var(--color-text-muted)" }}>
            Confidence: {(result.confidence * 100).toFixed(1)}%
          </p>
          <div className="confidence-bar-track">
            <div
              className="confidence-bar-fill"
              style={{ width: `${(result.confidence * 100).toFixed(1)}%` }}
            />
          </div>
          <p style={{ marginTop: 16, color: "var(--color-text-muted)", fontSize: "0.85rem" }}>
            Bin ID: {result.bin_id} • Uploaded: {new Date(result.upload_time).toLocaleString()}
          </p>
          {result.is_alert && (
            <div className="error-banner" style={{ marginTop: 12 }}>
              This bin is FULL and requires immediate attention.
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default UploadPredict;
