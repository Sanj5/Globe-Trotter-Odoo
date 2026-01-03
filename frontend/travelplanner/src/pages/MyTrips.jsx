import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { tripAPI } from '../services/api';
import './MyTrips.css';

const MyTrips = () => {
  const [trips, setTrips] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [filter, setFilter] = useState('all'); // all, upcoming, past

  useEffect(() => {
    loadTrips();
  }, []);

  const loadTrips = async () => {
    try {
      const response = await tripAPI.getAll();
      setTrips(response.data.trips);
    } catch (error) {
      setError('Failed to load trips');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (tripId) => {
    if (!window.confirm('Are you sure you want to delete this trip?')) {
      return;
    }

    try {
      await tripAPI.delete(tripId);
      setTrips(trips.filter(trip => trip.id !== tripId));
    } catch (error) {
      alert('Failed to delete trip');
    }
  };

  const getFilteredTrips = () => {
    const now = new Date();
    
    if (filter === 'upcoming') {
      return trips.filter(trip => new Date(trip.start_date) >= now);
    } else if (filter === 'past') {
      return trips.filter(trip => new Date(trip.end_date) < now);
    }
    return trips;
  };

  const filteredTrips = getFilteredTrips();

  if (loading) {
    return <div className="loading">Loading your trips...</div>;
  }

  return (
    <div className="my-trips-container">
      <div className="trips-header">
        <h1>My Trips 🗺️</h1>
        <Link to="/create-trip" className="btn-create-trip">
          ➕ New Trip
        </Link>
      </div>

      {error && <div className="error-message">{error}</div>}

      <div className="filter-tabs">
        <button
          className={filter === 'all' ? 'active' : ''}
          onClick={() => setFilter('all')}
        >
          All ({trips.length})
        </button>
        <button
          className={filter === 'upcoming' ? 'active' : ''}
          onClick={() => setFilter('upcoming')}
        >
          Upcoming ({trips.filter(t => new Date(t.start_date) >= new Date()).length})
        </button>
        <button
          className={filter === 'past' ? 'active' : ''}
          onClick={() => setFilter('past')}
        >
          Past ({trips.filter(t => new Date(t.end_date) < new Date()).length})
        </button>
      </div>

      {filteredTrips.length === 0 ? (
        <div className="empty-trips">
          <div className="empty-icon">✈️</div>
          <h2>No trips found</h2>
          <p>Start planning your next adventure!</p>
          <Link to="/create-trip" className="btn-primary">Create Your First Trip</Link>
        </div>
      ) : (
        <div className="trips-list">
          {filteredTrips.map(trip => (
            <div key={trip.id} className="trip-item">
              {trip.cover_photo_url ? (
                <div className="trip-image-container">
                  <img src={trip.cover_photo_url} alt={trip.name} />
                </div>
              ) : (
                <div className="trip-image-placeholder">
                  <span>🌍</span>
                </div>
              )}

              <div className="trip-details">
                <h3>{trip.name}</h3>
                {trip.description && (
                  <p className="trip-description">{trip.description}</p>
                )}
                
                <div className="trip-meta">
                  <span className="trip-dates">
                    📅 {new Date(trip.start_date).toLocaleDateString()} - {new Date(trip.end_date).toLocaleDateString()}
                  </span>
                  <span className="trip-duration">
                    ⏱️ {trip.total_days} days • {trip.stops_count || 0} stops
                  </span>
                  {trip.is_public && (
                    <span className="trip-public">🌐 Public</span>
                  )}
                </div>

                <div className="trip-actions">
                  <Link to={`/trips/${trip.id}`} className="btn-view">
                    View Details
                  </Link>
                  <Link to={`/trips/${trip.id}/edit`} className="btn-edit">
                    ✏️ Edit
                  </Link>
                  <button 
                    onClick={() => handleDelete(trip.id)}
                    className="btn-delete"
                  >
                    🗑️ Delete
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default MyTrips;
