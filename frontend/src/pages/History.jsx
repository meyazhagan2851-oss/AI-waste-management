import React, { useEffect, useState, useCallback } from "react";
import { FaSearch, FaTrash } from "react-icons/fa";
import { toast } from "react-toastify";

import LoadingSpinner from "../components/LoadingSpinner";
import ErrorBanner from "../components/ErrorBanner";
import PredictionBadge from "../components/PredictionBadge";
import { getHistory, deleteHistoryRecord, getImageUrl } from "../services/api";

const PAGE_SIZE = 8;

/**
 * History
 * -------
 * Searchable, filterable, paginated table of all past predictions.
 * Supports deleting records and previewing the uploaded image.
 */
const History = () => {
  const [records, setRecords] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const [filter, setFilter] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const fetchHistory = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const data = await getHistory({ search, prediction: filter, page, pageSize: PAGE_SIZE });
      setRecords(data.results);
      setTotal(data.total);
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to load history.");
    } finally {
      setLoading(false);
    }
  }, [search, filter, page]);

  useEffect(() => {
    fetchHistory();
  }, [fetchHistory]);

  const handleDelete = async (id) => {
    if (!window.confirm("Delete this record permanently?")) return;
    try {
      await deleteHistoryRecord(id);
      toast.success("Record deleted");
      fetchHistory();
    } catch (err) {
      toast.error("Failed to delete record");
    }
  };

  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE));

  return (
    <div>
      <div className="page-header">
        <h1>Prediction History</h1>
        <p>Search and review every AI classification made on bin images.</p>
      </div>

      <ErrorBanner message={error} />

      <div className="filters-bar">
        <div style={{ position: "relative" }}>
          <FaSearch style={{ position: "absolute", left: 12, top: 12, color: "var(--color-text-muted)" }} />
          <input
            className="input-field"
            style={{ paddingLeft: 34, width: 240 }}
            placeholder="Search by image or bin ID..."
            value={search}
            onChange={(e) => { setPage(1); setSearch(e.target.value); }}
          />
        </div>

        <select
          className="select-field"
          value={filter}
          onChange={(e) => { setPage(1); setFilter(e.target.value); }}
        >
          <option value="">All Statuses</option>
          <option value="Empty">Empty</option>
          <option value="Half Full">Half Full</option>
          <option value="Full">Full</option>
        </select>
      </div>

      <div className="card">
        {loading ? (
          <LoadingSpinner label="Loading history..." />
        ) : records.length === 0 ? (
          <p className="empty-state">No prediction records found.</p>
        ) : (
          <>
            <table className="data-table">
              <thead>
                <tr>
                  <th>Image</th>
                  <th>Bin ID</th>
                  <th>Prediction</th>
                  <th>Confidence</th>
                  <th>Uploaded</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {records.map((r) => (
                  <tr key={r.id}>
                    <td>
                      <img
                        src={getImageUrl(r.image_name)}
                        alt={r.image_name}
                        style={{ width: 48, height: 48, objectFit: "cover", borderRadius: 8 }}
                        onError={(e) => { e.target.style.display = "none"; }}
                      />
                    </td>
                    <td>{r.bin_id}</td>
                    <td><PredictionBadge prediction={r.prediction} variant="pill" /></td>
                    <td>{(r.confidence * 100).toFixed(1)}%</td>
                    <td>{new Date(r.upload_time).toLocaleString()}</td>
                    <td>
                      <button
                        className="btn btn-danger"
                        style={{ padding: "6px 10px" }}
                        onClick={() => handleDelete(r.id)}
                        title="Delete record"
                      >
                        <FaTrash />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>

            <div className="pagination">
              <button className="btn btn-secondary" disabled={page <= 1} onClick={() => setPage((p) => p - 1)}>
                Previous
              </button>
              <span>Page {page} of {totalPages} ({total} total)</span>
              <button className="btn btn-secondary" disabled={page >= totalPages} onClick={() => setPage((p) => p + 1)}>
                Next
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default History;
