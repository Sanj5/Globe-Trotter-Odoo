import React, { useEffect, useState } from 'react';
import api from '../services/api';
import '../styles.css';
import './ActivitySearch.css';

const ActivitySearch = ({ stopId, cityId, onActivityAdded, onClose }) => {
  const [activities, setActivities] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  
  const [filters, setFilters] = useState({
    category: '',
    max_cost: '',
    max_duration: '',
    search: ''
  });
  
  const [pagination, setPagination] = useState({
    offset: 0,
    limit: 12,
    total: 0,
    hasMore: false
  });
  
  const [categories, setCategories] = useState([]);
  const [selectedActivities, setSelectedActivities] = useState(new Set());

  useEffect(() => {
    loadCategories();
  }, []);

  useEffect(() => {
    setPagination((prev) => ({ ...prev, offset: 0 }));
    loadActivities();
  }, [cityId, filters]);

  const loadActivities = async () => {
    setLoading(true);
    setError('');
    try {
      const params = new URLSearchParams({
        limit: pagination.limit,
        offset: pagination.offset,
      });
      
      if (filters.category) params.append('category', filters.category);
      if (filters.max_cost) params.append('max_cost', filters.max_cost);
      if (filters.max_duration) params.append('max_duration', filters.max_duration);
      
      // Always include city_id for scoped searches
      params.append('city_id', cityId);
      
      const endpoint = filters.search 
        ? `/activities/search?q=${encodeURIComponent(filters.search)}&${params.toString()}`
        : `/cities/${cityId}/activities?${params.toString()}`;
      
      const res = await api.get(endpoint);
      setActivities(res.data.activities || []);
      setPagination({
        ...pagination,
        total: res.data.pagination?.total || 0,
        hasMore: res.data.pagination?.has_more || false
      });
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to load activities');
      console.error('Activity loading error:', err);
    } finally {
      setLoading(false);
    }
  };

  const loadCategories = async () => {
    try {
      const res = await api.get('/activities/categories');
      setCategories(res.data.categories || []);
    } catch (err) {
      console.error('Failed to load categories:', err);
    }
  };

  const handleFilterChange = (field, value) => {
    setFilters((prev) => ({ ...prev, [field]: value }));
    setPagination((prev) => ({ ...prev, offset: 0 }));
  };

  const handleSearch = (value) => {
    handleFilterChange('search', value);
  };

  const toggleActivitySelection = (activityId) => {
    const newSelected = new Set(selectedActivities);
    if (newSelected.has(activityId)) {
      newSelected.delete(activityId);
    } else {
      newSelected.add(activityId);
    }
    setSelectedActivities(newSelected);
  };

  const handleAddActivities = async () => {
    if (selectedActivities.size === 0) {
      setError('Please select at least one activity');
      return;
    }

    try {
      for (const activityId of selectedActivities) {
        await api.post(`/stops/${stopId}/activities`, {
          activity_id: activityId,
          day_number: 1,
          time_of_day: 'morning',
        });
      }
      onActivityAdded && onActivityAdded();
      setSelectedActivities(new Set());
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to add activities');
    }
  };

  const handleLoadMore = () => {
    setPagination((prev) => ({
      ...prev,
      offset: prev.offset + prev.limit
    }));
  };

  const handleRefreshActivities = async () => {
    setLoading(true);
    setError('');
    try {
      const res = await api.post(`/cities/${cityId}/activities/refresh`, {
        interests: ['cultural', 'adventure', 'food', 'shopping'],
        max_budget: 2000
      });
      // Reload activities after refresh
      await loadActivities();
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to refresh activities');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="activity-search-container">
      <div className="activity-search-header">
        <div className="header-title-section">
          <h3>🎯 Browse Activities</h3>
          <button 
            className="btn-refresh" 
            onClick={handleRefreshActivities}
            disabled={loading}
            title="Refresh activities using AI"
          >
            🔄 Refresh
          </button>
        </div>
        <button className="btn-close" onClick={onClose}>✕</button>
      </div>

      {error && <div className="error-message">{error}</div>}

      <div className="activity-filters">
        <input
          type="text"
          placeholder="Search activities..."
          value={filters.search}
          onChange={(e) => handleSearch(e.target.value)}
          className="filter-input"
        />
        
        <select
          value={filters.category}
          onChange={(e) => handleFilterChange('category', e.target.value)}
          className="filter-select"
        >
          <option value="">All Categories</option>
          {categories.map((cat) => (
            <option key={cat} value={cat}>
              {cat.charAt(0).toUpperCase() + cat.slice(1)}
            </option>
          ))}
        </select>

        <input
          type="number"
          placeholder="Max cost (₹)"
          value={filters.max_cost}
          onChange={(e) => handleFilterChange('max_cost', e.target.value)}
          min="0"
          className="filter-input"
        />

        <input
          type="number"
          placeholder="Max duration (h)"
          value={filters.max_duration}
          onChange={(e) => handleFilterChange('max_duration', e.target.value)}
          min="0"
          step="0.5"
          className="filter-input"
        />
      </div>

      {loading ? (
        <div className="loading">Loading activities...</div>
      ) : (
        <>
          <div className="activities-grid">
            {activities.map((activity) => (
              <div
                key={activity.id}
                className={`activity-card ${selectedActivities.has(activity.id) ? 'selected' : ''}`}
                onClick={() => toggleActivitySelection(activity.id)}
              >
                <div className="activity-card-header">
                  <input
                    type="checkbox"
                    checked={selectedActivities.has(activity.id)}
                    onChange={() => toggleActivitySelection(activity.id)}
                    className="activity-checkbox"
                  />
                  <span className="activity-category">
                    {activity.category.toUpperCase()}
                  </span>
                </div>
                
                <h4 className="activity-name">{activity.name}</h4>
                
                {activity.description && (
                  <p className="activity-description">{activity.description}</p>
                )}
                
                <div className="activity-meta">
                  <span className="activity-cost">💰 ₹{activity.estimated_cost}</span>
                  <span className="activity-duration">⏱ {activity.duration_hours}h</span>
                </div>
              </div>
            ))}
          </div>

          {activities.length === 0 && !loading && (
            <div className="no-activities">No activities found. Try adjusting your filters.</div>
          )}

          {pagination.hasMore && (
            <div className="load-more-container">
              <button className="btn-secondary" onClick={handleLoadMore}>
                Load More
              </button>
            </div>
          )}

          <div className="activity-actions">
            <div className="selected-count">
              {selectedActivities.size > 0 && (
                <span>{selectedActivities.size} activity(ies) selected</span>
              )}
            </div>
            <button
              className="btn-primary"
              onClick={handleAddActivities}
              disabled={selectedActivities.size === 0}
            >
              Add Selected ({selectedActivities.size})
            </button>
          </div>
        </>
      )}
    </div>
  );
};

export default ActivitySearch;
