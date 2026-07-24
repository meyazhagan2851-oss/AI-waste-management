/**
 * api.js
 * ------
 * Centralized Axios instance and API call functions.
 * Keeping all HTTP calls here means pages/components never talk to
 * Axios directly, making the app easier to maintain and test.
 */

import axios from "axios";

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || "http://localhost:8000";

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
});

// ---------------------------------------------
// Prediction APIs
// ---------------------------------------------

/** Uploads a bin image and returns the AI prediction result. */
export const predictBinStatus = async (file, binId = "BIN-001") => {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("bin_id", binId);

  const response = await apiClient.post("/api/predict", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return response.data;
};

// ---------------------------------------------
// History APIs
// ---------------------------------------------

/** Fetches paginated, filterable prediction history. */
export const getHistory = async ({ search = "", prediction = "", page = 1, pageSize = 10 } = {}) => {
  const response = await apiClient.get("/api/history", {
    params: { search, prediction, page, page_size: pageSize },
  });
  return response.data;
};

/** Deletes a single history record by id. */
export const deleteHistoryRecord = async (id) => {
  const response = await apiClient.delete(`/api/history/${id}`);
  return response.data;
};

/** Builds the URL used to display a stored bin image. */
export const getImageUrl = (imageName) => `${API_BASE_URL}/api/history/image/${imageName}`;

// ---------------------------------------------
// Dashboard APIs
// ---------------------------------------------

/** Fetches aggregate dashboard statistics (counts, averages). */
export const getDashboardStats = async () => {
  const response = await apiClient.get("/api/dashboard/stats");
  return response.data;
};

/** Fetches the latest status for every tracked bin. */
export const getBinStatuses = async () => {
  const response = await apiClient.get("/api/dashboard/bins");
  return response.data;
};

/** Basic API/AI health check. */
export const getHealth = async () => {
  const response = await apiClient.get("/api/health");
  return response.data;
};

export default apiClient;
