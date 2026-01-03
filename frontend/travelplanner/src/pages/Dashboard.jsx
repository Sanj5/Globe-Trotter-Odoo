import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { dashboardAPI, cityAPI } from '../services/api';
import { useAuth } from '../context/AuthContext';
import './Dashboard.css';

const Dashboard = () => {
  const { user } = useAuth();
  const [stats, setStats] = useState(null);
  const [popularCities, setPopularCities] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      const [statsRes, citiesRes] = await Promise.all([
        dashboardAPI.getStats(),
        cityAPI.getPopular(8)
      ]);
      
      setStats(statsRes.data);
      setPopularCities(citiesRes.data.cities);
    } catch (error) {
      console.error('Error loading dashboard:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="loading">Loading dashboard...</div>;
  }

  return (
    <div className="dashboard-container">
      <div className="dashboard-header">
        <h1>Welcome back, {user?.name}! 🌍</h1>
        <p>Ready to plan your next adventure?</p>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon">✈️</div>
          <div className="stat-info">
            <h3>{stats?.total_trips || 0}</h3>
            <p>Total Trips</p>
          </div>
        </div>
        
        <div className="stat-card">
          <div className="stat-icon">🗓️</div>
          <div className="stat-info">
            <h3>{stats?.upcoming_trips || 0}</h3>
            <p>Upcoming Trips</p>
          </div>
        </div>
        
        <div className="stat-card">
          <div className="stat-icon">❤️</div>
          <div className="stat-info">
            <h3>{stats?.saved_destinations || 0}</h3>
            <p>Saved Destinations</p>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">💵</div>
          <div className="stat-info">
            <h3>${(stats?.budget_total || 0).toFixed(0)}</h3>
            <p>Planned Budget</p>
          </div>
        </div>
      </div>

      <div className="dashboard-actions">
        <Link to="/create-trip" className="btn-primary-large">
          ➕ Plan New Trip
        </Link>
        <Link to="/trips" className="btn-secondary-large">
          📋 My Trips
        </Link>
      </div>

      <div className="section">
        <div className="section-header">
          <h2>Your Recent Trips</h2>
          <Link to="/trips" className="view-all">View All →</Link>
        </div>
        
        <div className="trips-grid">
          {stats?.recent_trips && stats.recent_trips.length > 0 ? (
            stats.recent_trips.map(trip => (
              <Link key={trip.id} to={`/trips/${trip.id}`} className="trip-card">
                {trip.cover_photo_url && (
                  <img src={trip.cover_photo_url} alt={trip.name} className="trip-image" />
                )}
                <div className="trip-info">
                  <h3>{trip.name}</h3>
                  <p className="trip-dates">
                    📅 {new Date(trip.start_date).toLocaleDateString()} - {new Date(trip.end_date).toLocaleDateString()}
                  </p>
                  <p className="trip-duration">⏱️ {trip.total_days} days • {trip.stops_count || 0} stops</p>
                </div>
              </Link>
            ))
          ) : (
            <div className="empty-state">
              <p>No trips yet. Start planning your first adventure!</p>
              <Link to="/create-trip" className="btn-primary">Create Trip</Link>
            </div>
          )}
        </div>
      </div>

      <div className="section">
        <div className="section-header">
          <h2>Popular Destinations 🌟</h2>
        </div>
        
        <div className="cities-grid">
          {popularCities.map(city => (
            <div key={city.id} className="city-card">
              {city.image_url && (
                <img src={city.image_url} alt={city.name} className="city-image" />
              )}
              <div className="city-info">
                <h3>{city.name}</h3>
                <p className="city-country">📍 {city.country}</p>
                <div className="city-meta">
                  <span className="popularity">⭐ {city.popularity_score}</span>
                  <span className="cost-index">💰 {city.cost_index.toFixed(1)}x</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
