import React, { useState, useEffect } from "react";
import { useAuth } from "../context/AuthContext";
import { userAPI } from "../services/api";
import { useNavigate } from "react-router-dom";

const Profile = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const response = await userAPI.getProfile();
        setProfile(response.data);
      } catch (error) {
        console.error("Error fetching profile:", error);
      } finally {
        setLoading(false);
      }
    };

    if (user) {
      fetchProfile();
    }
  }, [user]);

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  if (loading) {
    return (
      <div style={{ padding: "2rem", textAlign: "center" }}>
        <p>Loading profile...</p>
      </div>
    );
  }

  return (
    <div
      style={{
        padding: "2rem",
        backgroundColor: "#f0f8ff",
        borderRadius: "10px",
        boxShadow: "0 4px 8px rgba(0, 0, 0, 0.2)",
        maxWidth: "600px",
        margin: "auto",
        color: "#333",
      }}
    >
      <h2 style={{ textAlign: "center", fontFamily: "'Roboto', sans-serif" }}>
        User Profile
      </h2>

      {profile ? (
        <div style={{ textAlign: "center" }}>
          {/* Profile Picture Placeholder */}
          <div
            style={{
              borderRadius: "50%",
              width: "150px",
              height: "150px",
              margin: "0 auto 1rem",
              backgroundColor: "#2575fc",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              color: "#fff",
              fontSize: "3rem",
              fontWeight: "bold",
              boxShadow: "0 4px 8px rgba(0, 0, 0, 0.2)",
            }}
          >
            {profile.name ? profile.name.charAt(0).toUpperCase() : "U"}
          </div>

          {/* User Info */}
          <div style={{ marginBottom: "1rem" }}>
            <p style={{ fontSize: "1.2rem", fontWeight: "bold" }}>
              <strong>Name:</strong> {profile.name || "Not set"}
            </p>
            <p style={{ fontSize: "1.1rem" }}>
              <strong>Email:</strong> {profile.email}
            </p>
            {profile.preferences && (
              <p style={{ fontSize: "1rem", marginTop: "1rem" }}>
                <strong>Preferences:</strong> {profile.preferences}
              </p>
            )}
          </div>

          {/* Edit Profile / Log Out Buttons */}
          <div>
            <button
              onClick={() => alert("Edit profile feature coming soon!")}
              style={{
                backgroundColor: "#2575fc",
                border: "none",
                color: "#fff",
                padding: "10px 20px",
                borderRadius: "5px",
                cursor: "pointer",
                margin: "10px",
                fontSize: "1rem",
                boxShadow: "0 4px 6px rgba(0, 0, 0, 0.2)",
                transition: "background-color 0.3s ease",
              }}
            >
              Edit Profile
            </button>

            <button
              onClick={handleLogout}
              style={{
                backgroundColor: "#e74c3c",
                border: "none",
                color: "#fff",
                padding: "10px 20px",
                borderRadius: "5px",
                cursor: "pointer",
                margin: "10px",
                fontSize: "1rem",
                boxShadow: "0 4px 6px rgba(0, 0, 0, 0.2)",
                transition: "background-color 0.3s ease",
              }}
            >
              Log Out
            </button>
          </div>
        </div>
      ) : (
        <p style={{ textAlign: "center", fontSize: "1.1rem" }}>
          No user is logged in.
        </p>
      )}
    </div>
  );
};

export default Profile;
