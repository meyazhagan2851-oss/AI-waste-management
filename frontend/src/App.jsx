import React from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";

import Navbar from "./components/Navbar";
import Dashboard from "./pages/Dashboard";
import UploadPredict from "./pages/UploadPredict";
import History from "./pages/History";

/**
 * App
 * ---
 * Root component: sets up routing, the persistent navbar, and the
 * global toast notification container used for "bin Full" alerts.
 */
function App() {
  return (
    <BrowserRouter>
      <div className="app-shell">
        <div style={{ flex: 1 }}>
          <Navbar />
          <div className="main-content">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/upload" element={<UploadPredict />} />
              <Route path="/history" element={<History />} />
            </Routes>
          </div>
        </div>
      </div>
      <ToastContainer position="top-right" theme="dark" autoClose={5000} />
    </BrowserRouter>
  );
}

export default App;
