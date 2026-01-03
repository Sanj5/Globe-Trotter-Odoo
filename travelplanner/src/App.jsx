import {
  BrowserRouter as Router,
  Routes,
  Route,
  Link,
  Navigate,
  useLocation,
} from "react-router-dom";
import React from "react";
import { AuthProvider, useAuth } from "./context/AuthContext";
import Dashboard from "./pages/Dashboard";
import CreateTrip from "./pages/CreateTrip";
import MyTrips from "./pages/MyTrips";
import SavedTrips from "./pages/SavedTrips";
import Profile from "./pages/Profile";
import TripDetail from "./pages/TripDetail";
import TripEdit from "./pages/TripEdit";
import Login from "./pages/Login";
import SignUp from "./pages/SignUp";
import Home from "./pages/Home";
import ChatbaseBot from "./components/ChatbaseBot";
import './App.css';

// Protected Route Component
const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();
  
  if (loading) {
    return <div className="loading">Loading...</div>;
  }
  
  return isAuthenticated ? children : <Navigate to="/login" />;
};

// Navigation Component
const Navbar = () => {
  const { user, isAuthenticated, logout } = useAuth();
  const location = useLocation();

  // Don't show navbar on login/signup pages
  if (location.pathname === "/login" || location.pathname === "/signup") {
    return null;
  }

  const handleLogout = () => {
    logout();
  };

  return (
    <nav className="navbar">
      <div className="nav-left">
        <Link to="/" className="nav-logo">🌍 GlobeTrotter</Link>
        {isAuthenticated && (
          <>
            <Link to="/dashboard">Dashboard</Link>
            <Link to="/trips">My Trips</Link>
            <Link to="/saved-trips">Saved</Link>
          </>
        )}
      </div>

      <div className="nav-right">
        {isAuthenticated ? (
          <>
            <span className="user-name">👋 {user?.name}</span>
            <Link to="/profile">Profile</Link>
            <button onClick={handleLogout} className="btn-logout">Logout</button>
          </>
        ) : (
          <>
            <Link to="/login">Login</Link>
            <Link to="/signup">Sign Up</Link>
          </>
        )}
      </div>
    </nav>
  );
};

// Main App Content
const AppContent = () => {
  const location = useLocation();

  return (
    <>
      <Navbar />

      <Routes>
        {/* Public Routes */}
        <Route path="/" element={<Home />} />
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<SignUp />} />

        {/* Protected Routes */}
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          }
        />
        <Route
          path="/trips"
          element={
            <ProtectedRoute>
              <MyTrips />
            </ProtectedRoute>
          }
        />
        <Route
          path="/trips/:id"
          element={
            <ProtectedRoute>
              <TripDetail />
            </ProtectedRoute>
          }
        />
        <Route
          path="/trips/:id/edit"
          element={
            <ProtectedRoute>
              <TripEdit />
            </ProtectedRoute>
          }
        />
        <Route
          path="/create-trip"
          element={
            <ProtectedRoute>
              <CreateTrip />
            </ProtectedRoute>
          }
        />
        <Route
          path="/saved-trips"
          element={
            <ProtectedRoute>
              <SavedTrips />
            </ProtectedRoute>
          }
        />
        <Route
          path="/profile"
          element={
            <ProtectedRoute>
              <Profile />
            </ProtectedRoute>
          }
        />
      </Routes>

      {/* Show chatbot except on login/signup pages */}
      {location.pathname !== "/login" && location.pathname !== "/signup" && <ChatbaseBot />}
    </>
  );
};

const App = () => (
  <Router>
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  </Router>
);

export default App;
