import React, { useState } from "react";
import { NavLink } from "react-router-dom";
import { FaRecycle, FaTachometerAlt, FaCloudUploadAlt, FaHistory, FaBars } from "react-icons/fa";

/**
 * Navbar
 * ------
 * Responsive top navigation bar. Collapses into a toggleable menu on
 * small/mobile screens.
 */
const Navbar = () => {
  const [menuOpen, setMenuOpen] = useState(false);

  const links = [
    { to: "/", label: "Dashboard", icon: <FaTachometerAlt /> },
    { to: "/upload", label: "Upload & Predict", icon: <FaCloudUploadAlt /> },
    { to: "/history", label: "History", icon: <FaHistory /> },
  ];

  return (
    <nav className="navbar">
      <div className="navbar-brand">
        <FaRecycle className="brand-icon" />
        <span>Smart Waste AI</span>
      </div>

      <button className="navbar-toggle" onClick={() => setMenuOpen(!menuOpen)} aria-label="Toggle menu">
        <FaBars />
      </button>

      <div className={`navbar-links ${menuOpen ? "open" : ""}`}>
        {links.map((link) => (
          <NavLink
            key={link.to}
            to={link.to}
            end={link.to === "/"}
            className={({ isActive }) => `nav-link ${isActive ? "active" : ""}`}
            onClick={() => setMenuOpen(false)}
          >
            {link.icon} {link.label}
          </NavLink>
        ))}
      </div>
    </nav>
  );
};

export default Navbar;
