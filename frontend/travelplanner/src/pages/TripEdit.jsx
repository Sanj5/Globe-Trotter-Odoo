import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { tripAPI, stopAPI, cityAPI } from '../services/api';
import './CreateTrip.css';

const TripEdit = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [trip, setTrip] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [stopError, setStopError] = useState('');

  const [formData, setFormData] = useState({
    tripName: '',
    description: '',
    start_date: '',
    days: 5,
    budget_min: 30000,
    budget_max: 80000,
    preferences: '',
    cover_photo_url: ''
  });

  const [mainDestCity, setMainDestCity] = useState(null);
  const [mainDestQuery, setMainDestQuery] = useState('');
  const [mainDestResults, setMainDestResults] = useState([]);
  const [stops, setStops] = useState([]);
  const [cityResults, setCityResults] = useState([]);
  const [searchFilters, setSearchFilters] = useState({ country: '', region: '' });

  const [stopForm, setStopForm] = useState({
    cityQuery: '',
    cityId: null,
    start_date: '',
    end_date: '',
    notes: '',
    order_index: '',
  });

  useEffect(() => {
    loadTrip();
  }, [id]);

  useEffect(() => {
    if (trip?.stops) {
      const ordered = [...trip.stops].sort((a, b) => a.order_index - b.order_index);
      const mainStop = ordered[0];
      
      if (mainStop) {
        setMainDestCity(mainStop.city);
        setMainDestQuery(`${mainStop.city?.name}, ${mainStop.city?.country}`);
      }

      const intermediateStops = ordered.slice(1).map((stop, idx) => ({
        id: stop.id,
        cityId: stop.city_id,
        cityLabel: `${stop.city?.name}, ${stop.city?.country}`,
        start_date: stop.start_date,
        end_date: stop.end_date,
        notes: stop.notes,
        order_index: idx + 1,
      }));

      setStops(intermediateStops);

      // Update stop form dates
      if (trip.start_date) {
        setStopForm((prev) => ({
          ...prev,
          start_date: trip.start_date,
          end_date: trip.end_date || trip.start_date,
        }));
      }
    }
  }, [trip]);

  const loadTrip = async () => {
    setLoading(true);
    setError('');
    try {
      const res = await tripAPI.getById(id);
      const t = res.data.trip;
      setTrip(t);

      const startDate = new Date(t.start_date);
      const endDate = new Date(t.end_date);
      const days = Math.ceil((endDate - startDate) / (1000 * 60 * 60 * 24)) + 1;

      setFormData({
        tripName: t.name || '',
        description: t.description || '',
        start_date: t.start_date,
        days: days || 5,
        budget_min: t.budget_min || 30000,
        budget_max: t.budget_max || 80000,
        preferences: t.preferences || '',
        cover_photo_url: t.cover_photo_url || ''
      });
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to load trip');
    } finally {
      setLoading(false);
    }
  };

  const normalizeOrders = (list) => {
    const sorted = [...list].sort((a, b) => a.order_index - b.order_index);
    return sorted.map((item, idx) => ({ ...item, order_index: idx + 1 }));
  };

  const reorderOnChange = (list, id, newOrder) => {
    const max = list.length;
    const targetOrder = Math.max(1, Math.min(newOrder, max));
    const current = list.find((s) => s.id === id);
    if (!current) return list;
    const currentOrder = current.order_index;
    if (targetOrder === currentOrder) return list;

    return list.map((s) => {
      if (s.id === id) return { ...s, order_index: targetOrder };
      if (targetOrder < currentOrder && s.order_index >= targetOrder && s.order_index < currentOrder) {
        return { ...s, order_index: s.order_index + 1 };
      }
      if (targetOrder > currentOrder && s.order_index <= targetOrder && s.order_index > currentOrder) {
        return { ...s, order_index: s.order_index - 1 };
      }
      return s;
    });
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleMainDestSearch = async (query) => {
    setMainDestQuery(query);
    if (!query || query.length < 2) {
      setMainDestResults([]);
      return;
    }
    try {
      const res = await cityAPI.search({ q: query, limit: 6 });
      setMainDestResults(res.data.cities || []);
    } catch (err) {
      setMainDestResults([]);
    }
  };

  const handleSelectMainDest = (city) => {
    setMainDestCity(city);
    setMainDestQuery(`${city.name}, ${city.country}`);
    setMainDestResults([]);
  };

  const handleCitySearch = async (query) => {
    setStopForm((prev) => ({ ...prev, cityQuery: query }));
    if (!query || query.length < 2) {
      setCityResults([]);
      return;
    }
    try {
      const res = await cityAPI.search({
        q: query,
        country: searchFilters.country || undefined,
        region: searchFilters.region || undefined,
        limit: 12,
      });
      setCityResults(res.data.cities || []);
    } catch (err) {
      setCityResults([]);
    }
  };

  const handleFilterChange = (e) => {
    const { name, value } = e.target;
    setSearchFilters((prev) => ({ ...prev, [name]: value }));
    if (stopForm.cityQuery && stopForm.cityQuery.length >= 2) {
      handleCitySearch(stopForm.cityQuery);
    }
  };

  const handleSelectCity = (city) => {
    setStopForm((prev) => ({ ...prev, cityId: city.id, cityQuery: `${city.name}, ${city.country}` }));
    setCityResults([]);
  };

  const handleStopFormChange = (e) => {
    setStopForm({ ...stopForm, [e.target.name]: e.target.value });
  };

  const addLocalStop = () => {
    setStopError('');
    if (!stopForm.cityId) {
      return;
    }
    const nextOrder = stops.length + 1;
    const desired = stopForm.order_index ? Number(stopForm.order_index) : nextOrder;
    const order_index = Math.max(1, Math.min(desired, nextOrder));
    const tempId = `tmp-${Date.now()}-${Math.floor(Math.random() * 1000)}`;

    let updated = stops.map((s) => (
      s.order_index >= order_index
        ? { ...s, order_index: s.order_index + 1 }
        : s
    ));

    updated.push({
      id: tempId,
      cityId: stopForm.cityId,
      cityLabel: stopForm.cityQuery,
      start_date: stopForm.start_date,
      end_date: stopForm.end_date,
      notes: stopForm.notes,
      order_index,
    });

    updated = normalizeOrders(updated);
    setStops(updated);
    setStopForm({
      cityQuery: '',
      cityId: null,
      start_date: formData.start_date,
      end_date: stopForm.end_date,
      notes: '',
      order_index: '',
    });
  };

  const addLocalStopFromSearch = (city) => {
    setStopForm((prev) => ({ ...prev, cityId: city.id, cityQuery: `${city.name}, ${city.country}` }));
    setCityResults([]);
    addLocalStop();
  };

  const updateLocalStopField = (stopId, field, value) => {
    setStops((prev) => {
      const mapped = prev.map((s) => (s.id === stopId ? { ...s, [field]: field === 'order_index' ? Number(value) : value } : s));
      if (field === 'order_index') {
        const orderValue = Number(value) || 1;
        const reordered = reorderOnChange(mapped, stopId, orderValue);
        return normalizeOrders(reordered);
      }
      return mapped;
    });
  };

  const removeLocalStop = (id) => {
    setStops((prev) => normalizeOrders(prev.filter((s) => s.id !== id)));
  };

  const handleSave = async (e) => {
    e.preventDefault();
    setError('');
    setSaving(true);

    try {
      const startDate = new Date(formData.start_date);
      const endDate = new Date(startDate);
      endDate.setDate(startDate.getDate() + Number(formData.days) - 1);

      const updatePayload = {
        name: formData.tripName || 'My Trip',
        description: formData.description,
        start_date: startDate.toISOString().slice(0, 10),
        end_date: endDate.toISOString().slice(0, 10),
        cover_photo_url: formData.cover_photo_url,
        budget_min: Number(formData.budget_min),
        budget_max: Number(formData.budget_max),
        preferences: formData.preferences,
      };

      await tripAPI.update(id, updatePayload);

      // Handle main destination change
      if (mainDestCity && trip?.stops) {
        const mainStop = trip.stops.find((s) => s.order_index === 1);
        if (mainStop?.city_id !== mainDestCity.id) {
          // Delete old main stop and create new one
          if (mainStop) {
            await stopAPI.delete(mainStop.id);
          }
          const formattedStart = startDate.toISOString().slice(0, 10);
          const formattedEnd = endDate.toISOString().slice(0, 10);
          await stopAPI.add(id, {
            city_id: mainDestCity.id,
            start_date: formattedStart,
            end_date: formattedEnd,
            notes: 'Main destination',
            order_index: 1,
          });
        }
      }

      // Handle intermediate stops (only save new ones that don't have real IDs)
      const newStops = stops.filter((s) => s.id.toString().startsWith('tmp-'));
      for (let i = 0; i < newStops.length; i++) {
        const stop = newStops[i];
        await stopAPI.add(id, {
          city_id: stop.cityId,
          start_date: stop.start_date,
          end_date: stop.end_date,
          notes: stop.notes,
          order_index: mainDestCity ? i + 2 : i + 1,
        });
      }

      // Update existing stops
      const existingStops = stops.filter((s) => !s.id.toString().startsWith('tmp-'));
      for (const stop of existingStops) {
        await stopAPI.update(stop.id, {
          start_date: stop.start_date,
          end_date: stop.end_date,
          notes: stop.notes,
        });
      }

      // Small delay to ensure all changes are committed
      await new Promise(resolve => setTimeout(resolve, 300));

      navigate(`/trips/${id}`);
    } catch (error) {
      setError(error.response?.data?.error || 'Failed to save trip');
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <div className="create-trip-container"><div className="trip-detail-loading">Loading trip...</div></div>;
  if (error && !trip) return <div className="create-trip-container"><div className="trip-detail-error">{error}</div></div>;

  return (
    <div className="create-trip-container">
      <div className="create-trip-card">
        <h1>✏️ Edit Your Trip</h1>
        <p className="subtitle">Update trip details and manage your stops</p>

        {error && <div className="error-message">{error}</div>}

        <form onSubmit={handleSave} className="trip-form">
          <div className="section-card">
            <div className="section-header">
              <div>
                <p className="eyebrow">Trip basics</p>
                <h2>Trip Details</h2>
              </div>
              <div className="form-actions">
                <button 
                  type="button" 
                  className="btn-secondary"
                  onClick={() => navigate(`/trips/${id}`)}
                >
                  Cancel
                </button>
                <button 
                  type="submit" 
                  className="btn-primary"
                  disabled={saving}
                >
                  {saving ? 'Saving...' : 'Save Changes'}
                </button>
              </div>
            </div>

            <div className="grid-two">
              <div className="form-group">
                <label htmlFor="mainDest">Main Destination * (Search City)</label>
                <input
                  type="text"
                  id="mainDest"
                  value={mainDestQuery}
                  onChange={(e) => handleMainDestSearch(e.target.value)}
                  placeholder={mainDestQuery || "Search for your main city..."}
                  required
                />
                {mainDestResults.length > 0 && (
                  <div className="city-results cards">
                    {mainDestResults.map((city) => (
                      <div key={city.id} className="city-card-line">
                        <div>
                          <div className="city-name">{city.name}</div>
                          <div className="muted">{city.country} • Cost {city.cost_index ?? '—'} • Popularity {city.popularity_score ?? '—'}</div>
                        </div>
                        <button type="button" className="btn-primary" onClick={() => handleSelectMainDest(city)}>Select</button>
                      </div>
                    ))}
                  </div>
                )}
                {mainDestCity && (
                  <div className="selected-main-dest">
                    ✓ Selected: <strong>{mainDestCity.name}, {mainDestCity.country}</strong>
                    <button type="button" className="btn-small" onClick={() => { setMainDestCity(null); setMainDestQuery(''); }}>Change</button>
                  </div>
                )}
              </div>
              <div className="form-group">
                <label htmlFor="cover_photo_url">Cover Photo URL</label>
                <input
                  type="url"
                  id="cover_photo_url"
                  name="cover_photo_url"
                  value={formData.cover_photo_url}
                  onChange={handleChange}
                  placeholder={formData.cover_photo_url || "https://example.com/image.jpg"}
                />
                <input
                  type="file"
                  accept="image/*"
                  onChange={(e) => {
                    const file = e.target.files?.[0];
                    if (!file) return;
                    const reader = new FileReader();
                    reader.onload = (ev) => {
                      setFormData((prev) => ({ ...prev, cover_photo_url: ev.target?.result || prev.cover_photo_url }));
                    };
                    reader.readAsDataURL(file);
                  }}
                  className="file-input"
                />
              </div>
            </div>

            {formData.cover_photo_url && (
              <div className="image-preview">
                <img src={formData.cover_photo_url} alt="Preview" />
              </div>
            )}

            <div className="grid-two">
              <div className="form-group">
                <label htmlFor="start_date">Start Date *</label>
                <input
                  type="date"
                  id="start_date"
                  name="start_date"
                  value={formData.start_date}
                  onChange={handleChange}
                  placeholder={formData.start_date}
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="days">How many days? *</label>
                <input
                  type="number"
                  id="days"
                  name="days"
                  value={formData.days}
                  min="1"
                  max="30"
                  onChange={handleChange}
                  placeholder={formData.days.toString()}
                  required
                />
              </div>
            </div>

            <div className="grid-two">
              <div className="form-group">
                <label htmlFor="budget_min">Budget min (₹ INR)</label>
                <input
                  type="number"
                  id="budget_min"
                  name="budget_min"
                  value={formData.budget_min}
                  min="0"
                  onChange={handleChange}
                  placeholder={formData.budget_min.toString()}
                />
              </div>

              <div className="form-group">
                <label htmlFor="budget_max">Budget max (₹ INR)</label>
                <input
                  type="number"
                  id="budget_max"
                  name="budget_max"
                  value={formData.budget_max}
                  min={formData.budget_min}
                  onChange={handleChange}
                  placeholder={formData.budget_max.toString()}
                />
              </div>
            </div>

            <div className="form-group">
              <label htmlFor="description">Description</label>
              <textarea
                id="description"
                name="description"
                value={formData.description}
                onChange={handleChange}
                placeholder={formData.description || "Describe your trip, goals, and what you want to experience..."}
                rows="3"
              />
            </div>

            <div className="form-group">
              <label htmlFor="preferences">Preferences (comma separated)</label>
              <input
                type="text"
                id="preferences"
                name="preferences"
                value={formData.preferences}
                onChange={handleChange}
                placeholder={formData.preferences || "museums, food, beaches"}
              />
            </div>

            <div className="divider" />

            <div className="section-header compact">
              <div>
                <p className="eyebrow">Intermediate stops (optional)</p>
                <h3>Add other cities</h3>
                <p className="muted">Add more cities you want to visit after your main destination.</p>
              </div>
              {stopError && <div className="inline-error">{stopError}</div>}
            </div>

            <div className="grid-two">
              <div className="form-group">
                <label>City</label>
                <input
                  type="text"
                  name="cityQuery"
                  value={stopForm.cityQuery}
                  onChange={(e) => handleCitySearch(e.target.value)}
                  placeholder="Search city name"
                />
                <div className="filters-row">
                  <input
                    type="text"
                    name="country"
                    value={searchFilters.country}
                    onChange={handleFilterChange}
                    placeholder="Filter by country"
                  />
                  <input
                    type="text"
                    name="region"
                    value={searchFilters.region}
                    onChange={handleFilterChange}
                    placeholder="Filter by region"
                  />
                </div>
                {cityResults.length > 0 && (
                  <div className="city-results cards">
                    {cityResults.map((city) => (
                      <div key={city.id} className="city-card-line">
                        <div>
                          <div className="city-name">{city.name}</div>
                          <div className="muted">{city.country} • Cost {city.cost_index ?? '—'} • Popularity {city.popularity_score ?? '—'}</div>
                        </div>
                        <div className="city-actions">
                          <button type="button" className="btn-secondary" onClick={() => handleSelectCity(city)}>Select</button>
                          <button type="button" className="btn-primary" onClick={() => addLocalStopFromSearch(city)}>Add to Trip</button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
              <div className="grid-two compact">
                <div className="form-group">
                  <label>Start Date</label>
                  <input type="date" name="start_date" value={stopForm.start_date} onChange={handleStopFormChange} />
                </div>
                <div className="form-group">
                  <label>End Date</label>
                  <input type="date" name="end_date" value={stopForm.end_date} onChange={handleStopFormChange} />
                </div>
              </div>
            </div>

            <div className="grid-two compact">
              <div className="form-group">
                <label>Notes</label>
                <textarea name="notes" value={stopForm.notes} onChange={handleStopFormChange} rows="2" />
              </div>
              <div className="form-group">
                <label>Insert Position</label>
                <input
                  type="number"
                  name="order_index"
                  min="1"
                  max={(stops.length || 0) + 1}
                  value={stopForm.order_index}
                  onChange={handleStopFormChange}
                  placeholder={`1-${(stops.length || 0) + 1}`}
                />
              </div>
            </div>

            <div className="align-end">
              <button type="button" className="btn-secondary" onClick={() => setStopForm({
                cityQuery: '',
                cityId: null,
                start_date: formData.start_date,
                end_date: stopForm.end_date,
                notes: '',
                order_index: '',
              })}>Reset</button>
              <button type="button" className="btn-primary" onClick={addLocalStop}>Add Stop</button>
            </div>

            {stops.length > 0 && (
              <div className="stops-list">
                {stops
                  .slice()
                  .sort((a, b) => a.order_index - b.order_index)
                  .map((stop) => (
                  <div key={stop.id} className="stop-row">
                    <div className="stop-main">
                      <div className="stop-title">
                        <strong>{stop.cityLabel || 'City selected'}</strong>
                        <span className="muted">Order {stop.order_index}</span>
                      </div>
                      <div className="stop-dates">
                        <input
                          type="date"
                          value={stop.start_date}
                          onChange={(e) => updateLocalStopField(stop.id, 'start_date', e.target.value)}
                        />
                        <span>→</span>
                        <input
                          type="date"
                          value={stop.end_date}
                          onChange={(e) => updateLocalStopField(stop.id, 'end_date', e.target.value)}
                        />
                      </div>
                      <textarea
                        rows="2"
                        value={stop.notes}
                        onChange={(e) => updateLocalStopField(stop.id, 'notes', e.target.value)}
                        placeholder={stop.notes || "Notes"}
                      />
                    </div>
                    <div className="stop-actions">
                      <label className="form-label">Order</label>
                      <input
                        type="number"
                        min="1"
                        max={stops.length}
                        value={stop.order_index}
                        onChange={(e) => updateLocalStopField(stop.id, 'order_index', e.target.value)}
                      />
                      <button type="button" className="btn-danger" onClick={() => removeLocalStop(stop.id)}>Delete</button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </form>
      </div>
    </div>
  );
};

export default TripEdit;
