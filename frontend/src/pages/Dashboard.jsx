import React, { useEffect, useState, useCallback } from "react";
import { Bar, Doughnut } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  ArcElement,
  Tooltip,
  Legend,
} from "chart.js";
import { FaTrashAlt, FaBoxOpen, FaExclamationTriangle, FaChartPie } from "react-icons/fa";
import { toast } from "react-toastify";

import StatCard from "../components/StatCard";
import LoadingSpinner from "../components/LoadingSpinner";
import ErrorBanner from "../components/ErrorBanner";
import PredictionBadge from "../components/PredictionBadge";
import { getDashboardStats, getBinStatuses } from "../services/api";

ChartJS.register(CategoryScale, LinearScale, BarElement, ArcElement, Tooltip, Legend);

const REFRESH_INTERVAL_MS = 15000; // auto-refresh dashboard every 15s

/**
 * Dashboard
 * ---------
 * Admin landing page: summary stat cards, charts, and live per-bin status.
 * Automatically polls the backend and shows a toast alert the moment any
 * bin's latest status becomes "Full".
 */
const Dashboard = () => {
  const [stats, setStats] = useState(null);
  const [bins, setBins] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [alertedBins, setAlertedBins] = useState(new Set());

  const fetchData = useCallback(async (isInitial = false) => {
    try {
      if (isInitial) setLoading(true);
      const [statsData, binsData] = await Promise.all([getDashboardStats(), getBinStatuses()]);
      setStats(statsData);
      setBins(binsData);
      setError("");

      // Notify admin the moment a bin is detected Full (once per bin per session)
      binsData.forEach((bin) => {
        if (bin.is_alert && !alertedBins.has(bin.bin_id)) {
          toast.error(`🚨 ${bin.bin_id} is FULL! Needs immediate collection.`);
          setAlertedBins((prev) => new Set(prev).add(bin.bin_id));
        }
      });
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to load dashboard data. Is the backend running?");
    } finally {
      setLoading(false);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [alertedBins]);

  useEffect(() => {
    fetchData(true);
    const interval = setInterval(() => fetchData(false), REFRESH_INTERVAL_MS);
    return () => clearInterval(interval);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  if (loading) return <LoadingSpinner label="Loading dashboard..." />;

  const barData = {
    labels: ["Empty", "Half Full", "Full"],
    datasets: [
      {
        label: "Predictions",
        data: stats ? [stats.empty_count, stats.half_full_count, stats.full_count] : [0, 0, 0],
        backgroundColor: ["#38bdf8", "#f59e0b", "#ef4444"],
        borderRadius: 8,
      },
    ],
  };

  const doughnutData = {
    labels: ["Empty", "Half Full", "Full"],
    datasets: [
      {
        data: stats ? [stats.empty_count, stats.half_full_count, stats.full_count] : [0, 0, 0],
        backgroundColor: ["#38bdf8", "#f59e0b", "#ef4444"],
        borderWidth: 0,
      },
    ],
  };

  const chartOptions = {
    plugins: { legend: { labels: { color: "#f1f5f9" } } },
    scales: {
      x: { ticks: { color: "#94a3b8" }, grid: { color: "#334155" } },
      y: { ticks: { color: "#94a3b8" }, grid: { color: "#334155" } },
    },
  };

  return (
    <div>
      <div className="page-header">
        <h1>Admin Dashboard</h1>
        <p>Real-time overview of all monitored garbage bins.</p>
      </div>

      <ErrorBanner message={error} />

      <div className="stat-grid">
        <StatCard icon={<FaChartPie />} iconClass="icon-total" label="Total Predictions" value={stats?.total_predictions ?? 0} />
        <StatCard icon={<FaTrashAlt />} iconClass="icon-empty" label="Empty Bins" value={stats?.empty_count ?? 0} />
        <StatCard icon={<FaBoxOpen />} iconClass="icon-half" label="Half Full Bins" value={stats?.half_full_count ?? 0} />
        <StatCard icon={<FaExclamationTriangle />} iconClass="icon-full" label="Full Bins (Alerts)" value={stats?.full_count ?? 0} />
      </div>

      <div className="chart-grid">
        <div className="card">
          <h3>Predictions by Class</h3>
          <Bar data={barData} options={chartOptions} />
        </div>
        <div className="card">
          <h3>Distribution</h3>
          <Doughnut data={doughnutData} options={{ plugins: { legend: { labels: { color: "#f1f5f9" } } } }} />
        </div>
      </div>

      <div className="card" style={{ marginTop: 20 }}>
        <h3>Live Bin Status</h3>
        {bins.length === 0 ? (
          <p className="empty-state">No bins monitored yet. Upload an image to get started.</p>
        ) : (
          <table className="data-table">
            <thead>
              <tr>
                <th>Bin ID</th>
                <th>Status</th>
                <th>Confidence</th>
                <th>Last Checked</th>
              </tr>
            </thead>
            <tbody>
              {bins.map((bin) => (
                <tr key={bin.bin_id}>
                  <td>{bin.bin_id}</td>
                  <td><PredictionBadge prediction={bin.latest_prediction} variant="pill" /></td>
                  <td>{(bin.confidence * 100).toFixed(1)}%</td>
                  <td>{new Date(bin.last_checked).toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
};

export default Dashboard;
