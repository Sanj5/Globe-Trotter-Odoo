import React, { useEffect, useState } from "react";
import { useParams, Link, useNavigate } from "react-router-dom";
import { tripAPI } from "../services/api";
import ActivitySearch from "../components/ActivitySearch";
import ActivityModal from "../components/ActivityModal";
import "./tripDetail.css";

const TripDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [trip, setTrip] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [aiLoading, setAiLoading] = useState(false);
  const [aiError, setAiError] = useState("");
  const [aiItinerary, setAiItinerary] = useState(null);
  const [aiBudgetNote, setAiBudgetNote] = useState("");
  const [activityModalOpen, setActivityModalOpen] = useState(false);
  const [selectedStopId, setSelectedStopId] = useState(null);
  const [selectedCityId, setSelectedCityId] = useState(null);

  useEffect(() => {
    const loadTrip = async () => {
      try {
        const res = await tripAPI.getById(id);
        setTrip(res.data.trip);
        setAiItinerary(res.data.trip?.ai_itinerary || null);
        setAiBudgetNote(res.data.trip?.ai_budget_note || "");
      } catch (err) {
        setError(err.response?.data?.error || "Failed to load trip");
      } finally {
        setLoading(false);
      }
    };
    loadTrip();
  }, [id]);

  const openActivitySearch = (stopId, cityId) => {
    setSelectedStopId(stopId);
    setSelectedCityId(cityId);
    setActivityModalOpen(true);
  };

  const handleActivityAdded = async () => {
    // Reload trip to see new activities
    try {
      const res = await tripAPI.getById(id);
      setTrip(res.data.trip);
      setActivityModalOpen(false);
    } catch (err) {
      console.error('Failed to reload trip');
    }
  };

  const handleGenerateAI = async () => {
    if (!trip) return;
    setAiError("");
    setAiBudgetNote("");
    setAiLoading(true);
    const budgetTotal = trip?.budget?.total_budget;
    const budgetMin = budgetTotal ? Math.max(1000, Math.round(budgetTotal * 0.8)) : 30000;
    const budgetMax = budgetTotal ? Math.round(budgetTotal * 1.1) : 80000;
    try {
      const res = await tripAPI.generateItinerary(trip.id, {
        budget_min: budgetMin,
        budget_max: budgetMax,
        preferences: [],
      });
      setAiItinerary(res.data.itinerary);
      setAiBudgetNote(res.data.budget_note || res.data.note || "");
      setTrip((prev) => prev ? { ...prev, ai_itinerary: res.data.itinerary } : prev);
    } catch (err) {
      setAiError(err.response?.data?.error || "Failed to generate itinerary");
    } finally {
      setAiLoading(false);
    }
  };

  if (loading) return <div className="trip-detail-loading">Loading trip...</div>;
  if (error) return <div className="trip-detail-error">{error}</div>;
  if (!trip) return <div className="trip-detail-error">Trip not found</div>;

  return (
    <div className="trip-detail">
      <div className="trip-detail-header">
        <div>
          <h1>{trip.name}</h1>
          <p className="trip-dates">{trip.start_date} → {trip.end_date} • {trip.total_days} days</p>
          {trip.description && <p className="trip-desc">{trip.description}</p>}
        </div>
        <div className="trip-actions">
          <Link className="btn-primary" to="/trips">Back to My Trips</Link>
          <Link className="btn-secondary" to={`/trips/${trip.id}/edit`}>Edit Trip</Link>
        </div>
      </div>

      {trip.cover_photo_url && (
        <div className="trip-cover">
          <img src={trip.cover_photo_url} alt={trip.name} />
        </div>
      )}

      <section className="trip-section">
        <h2>Itinerary</h2>
        {trip.stops && trip.stops.length > 0 ? (
          <div className="stops-list">
            {trip.stops.map((stop) => (
              <div key={stop.id} className="stop-card">
                <div className="stop-header">
                  <h3>{stop.city?.name}</h3>
                  <span className="stop-dates">{stop.start_date} → {stop.end_date}</span>
                </div>
                <p className="stop-notes">{stop.notes || "No notes"}</p>
                <div className="activities">
                  <div className="activities-header">
                    <h4>🎯 Activities</h4>
                    <button 
                      className="btn-small" 
                      onClick={() => openActivitySearch(stop.id, stop.city_id)}
                    >
                      + Add Activities
                    </button>
                  </div>
                  {stop.activities && stop.activities.length > 0 ? (
                    <ul>
                      {stop.activities.map((act) => (
                        <li key={act.id}>
                          {act.time_of_day ? `${act.time_of_day}: ` : ""}{act.activity?.name || "Activity"}
                          {act.activity?.category ? ` (${act.activity.category})` : ""}
                          {act.activity?.description ? ` — ${act.activity.description}` : ""}
                          {typeof act.estimated_cost_override !== "undefined" && act.estimated_cost_override !== null
                            ? ` • ~₹${act.estimated_cost_override}`
                            : act.activity?.estimated_cost ? ` • ~₹${act.activity.estimated_cost}` : ""}
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <p className="muted">No activities yet. Click "Add Activities" to browse and select.</p>
                  )}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="muted">
            <p>No stops yet. Add cities to your trip.</p>
          </div>
        )}
      </section>

      <section className="trip-section">
        <div className="trip-section-header">
          <h2>AI Draft Itinerary</h2>
          <button className="btn-primary" onClick={handleGenerateAI} disabled={aiLoading}>
            {aiLoading ? "Generating..." : "Generate"}
          </button>
        </div>
        {aiError && <div className="trip-detail-error">{aiError}</div>}
        {aiBudgetNote && <div className="trip-detail-warning">{aiBudgetNote}</div>}
        {aiItinerary ? (
          <div className="ai-itinerary">
            {aiItinerary.days && aiItinerary.days.map((day, idx) => (
              <div key={idx} className="ai-day">
                <h4>Day {day.day || idx + 1}{day.title ? `: ${day.title}` : ""}</h4>
                {day.summary && <p>{day.summary}</p>}
                
                {day.activities && day.activities.length > 0 && (
                  <div className="activities-section">
                    <h5>🎯 Activities</h5>
                    <ul>
                      {day.activities.map((act, i) => (
                        <li key={i}>
                          {act.time ? `${act.time}: ` : ""}{act.name}
                          {act.category ? ` (${act.category})` : ""}
                          {act.description ? ` — ${act.description}` : ""}
                          {typeof act.cost !== "undefined" ? ` • ~₹${act.cost}` : ""}
                          {act.duration ? ` • ${act.duration}h` : ""}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
                
                {day.transport_to_next_day && (
                  <div className="transport-section">
                    <h5>🚆 Travel to {day.transport_to_next_day.to}</h5>
                    {day.transport_to_next_day.modes && day.transport_to_next_day.modes.map((mode, i) => (
                      <div key={i} className="transport-option">
                        <p><strong>{mode.mode.toUpperCase()}</strong></p>
                        <ul className="transport-details">
                          {mode.duration && <li>⏱ Duration: {mode.duration}</li>}
                          {typeof mode.cost !== "undefined" && <li>💰 Cost: ~₹{mode.cost}</li>}
                          {mode.booking_platform && <li>🔖 Book on: {mode.booking_platform}</li>}
                          {mode.notes && <li>ℹ️ {mode.notes}</li>}
                        </ul>
                      </div>
                    ))}
                  </div>
                )}
                
                {day.accommodation && (
                  <div className="accommodation-section">
                    <h5>🏨 Stay</h5>
                    <p><strong>{day.accommodation.name}</strong></p>
                    {day.accommodation.description && <p>{day.accommodation.description}</p>}
                    {typeof day.accommodation.cost !== "undefined" && <p>Cost: ~₹{day.accommodation.cost}/night</p>}
                  </div>
                )}
                
                {day.meals && day.meals.length > 0 && (
                  <div className="meals-section">
                    <h5>🍽️ Food</h5>
                    <ul>
                      {day.meals.map((meal, i) => (
                        <li key={i}>
                          <strong>{meal.type}:</strong> {meal.suggestion}
                          {typeof meal.cost !== "undefined" ? ` • ~₹${meal.cost}` : ""}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            ))}
            
            {aiItinerary.budget_breakdown && (
              <div className="budget-breakdown-section">
                <h4>💵 Budget Breakdown</h4>
                <div className="budget-table">
                  {Object.entries(aiItinerary.budget_breakdown).map(([key, value]) => (
                    <div key={key} className="budget-row">
                      <span className="budget-label">{key.charAt(0).toUpperCase() + key.slice(1)}:</span>
                      <span className="budget-amount">₹{value}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {trip?.stops && trip.stops.some((s) => s.activities && s.activities.length > 0) && (
              <div className="activities-section">
                <h4>✅ Your Added Activities (when to go)</h4>
                {trip.stops.map((stop) => (
                  <div key={stop.id} className="activities-subsection">
                    <p><strong>{stop.city?.name}</strong> • {stop.start_date} → {stop.end_date}</p>
                    <ul>
                      {stop.activities.map((act) => (
                        <li key={act.id}>
                          {`Day ${act.day_number || 1}`} {act.time_of_day ? `• ${act.time_of_day}` : ""} — {act.activity?.name || "Activity"}
                          {act.activity?.category ? ` (${act.activity.category})` : ""}
                          {typeof act.estimated_cost !== "undefined" ? ` • ₹${act.estimated_cost}` : (act.activity?.estimated_cost ? ` • ₹${act.activity.estimated_cost}` : "")}
                        </li>
                      ))}
                    </ul>
                  </div>
                ))}
              </div>
            )}
          </div>
        ) : (
          <p className="muted">Use AI to Generate a draft to see suggestions.</p>
        )}
      </section>

      {activityModalOpen && selectedStopId && selectedCityId && (
        <ActivityModal onClose={() => setActivityModalOpen(false)}>
          <ActivitySearch 
            cityId={selectedCityId} 
            stopId={selectedStopId}
            tripId={trip.id}
            onActivityAdded={handleActivityAdded}
            onClose={() => setActivityModalOpen(false)}
          />
        </ActivityModal>
      )}
    </div>
  );
};

export default TripDetail;
