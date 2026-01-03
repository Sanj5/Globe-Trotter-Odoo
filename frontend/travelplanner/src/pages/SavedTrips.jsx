import React, { useState, useEffect } from "react";
import "./savedtrip.css";

const SavedTrips = () => {
  const [savedTrips, setSavedTrips] = useState([]);
  const [expandedTrip, setExpandedTrip] = useState(null);

  useEffect(() => {
    const trips = JSON.parse(localStorage.getItem("savedTrips")) || [];
    setSavedTrips(trips);
  }, []);

  const handleViewDetails = (id) => {
    setExpandedTrip(expandedTrip === id ? null : id);
  };

  const handleDeleteTrip = (id) => {
    const updatedTrips = savedTrips.filter((trip) => trip.id !== id);
    setSavedTrips(updatedTrips);
    localStorage.setItem("savedTrips", JSON.stringify(updatedTrips));
  };

  return (
    <div className="saved-trips-container">
      {savedTrips.length === 0 ? (
        <p>No saved trips yet. Start planning!</p>
      ) : (
        savedTrips.map((trip) => (
          <div key={trip.id} className="trip-card">
            <h2>{trip.name}</h2>
            <p>{trip.description}</p>

            {/* Buttons grouped together */}
            <div className="button-group">
              <button onClick={() => handleViewDetails(trip.id)}>
                {expandedTrip === trip.id ? "Hide Details" : "View Details"}
              </button>
              <button
                onClick={() => handleDeleteTrip(trip.id)}
                className="delete-button"
              >
                Delete
              </button>
            </div>

            {/* Show itinerary details if the trip is expanded */}
            {expandedTrip === trip.id && (
              <div className="itinerary-details">{trip.itinerary}</div>
            )}
          </div>
        ))
      )}
    </div>
  );
};

export default SavedTrips;
