import { useState } from "react";
import "./TravelPlanner.css"; // Make sure you include your custom CSS file
import { useNavigate } from "react-router-dom";

const TravelPlanner = () => {
  const navigate = useNavigate();
  const [tripDetails, setTripDetails] = useState({
    tripName: "",
    numDays: 1,
    selectedPlaces: [],
    tripType: "",
    budget: 0,
  });
  const [itinerary, setItinerary] = useState([]);
  const [suggestedActivities, setSuggestedActivities] = useState([
    { name: "Visit Beach", type: "Adventure" },
    { name: "Historical Museum", type: "Cultural" },
    { name: "Mountain Hike", type: "Adventure" },
    // More activity suggestions...
  ]);

  const handleTripDetailsChange = (e) => {
    const { name, value } = e.target;
    setTripDetails((prevDetails) => ({
      ...prevDetails,
      [name]: value,
    }));
  };

  const handlePlaceSelect = (place) => {
    if (!tripDetails.selectedPlaces.includes(place)) {
      setTripDetails((prevDetails) => ({
        ...prevDetails,
        selectedPlaces: [...prevDetails.selectedPlaces, place],
      }));
    }
  };

  const handleItineraryChange = (activity, day) => {
    const updatedItinerary = [...itinerary];
    updatedItinerary[day] = activity;
    setItinerary(updatedItinerary);
  };

  const handleSaveTrip = () => {
    // Save the trip (e.g., store in database or local storage)
    alert("Trip saved successfully!");
    navigate("/saved-trips");
  };

  return (
    <div className="travel-planner">
      <h1>Plan Your Trip</h1>

      <form className="trip-form">
        <div className="form-group">
          <label>Trip Name:</label>
          <input
            type="text"
            name="tripName"
            value={tripDetails.tripName}
            onChange={handleTripDetailsChange}
            placeholder="Enter your trip name"
          />
        </div>

        <div className="form-group">
          <label>Number of Days:</label>
          <input
            type="number"
            name="numDays"
            value={tripDetails.numDays}
            onChange={handleTripDetailsChange}
            min="1"
          />
        </div>

        <div className="form-group">
          <label>Destinations:</label>
          <div className="places-selector">
            <button
              type="button"
              onClick={() => handlePlaceSelect("Beach")}
            >
              Beach
            </button>
            <button
              type="button"
              onClick={() => handlePlaceSelect("Mountains")}
            >
              Mountains
            </button>
            <button
              type="button"
              onClick={() => handlePlaceSelect("City Tour")}
            >
              City Tour
            </button>
          </div>
        </div>

        <div className="form-group">
          <label>Trip Type:</label>
          <select
            name="tripType"
            value={tripDetails.tripType}
            onChange={handleTripDetailsChange}
          >
            <option value="">Select Trip Type</option>
            <option value="Adventure">Adventure</option>
            <option value="Relaxation">Relaxation</option>
            <option value="Cultural">Cultural</option>
          </select>
        </div>

        <div className="form-group">
          <label>Budget (in ₹ INR):</label>
          <input
            type="number"
            name="budget"
            value={tripDetails.budget}
            onChange={handleTripDetailsChange}
            min="0"
          />
        </div>
      </form>

      <div className="itinerary-section">
        <h2>Plan Your Itinerary</h2>
        <div className="itinerary-days">
          {Array.from({ length: tripDetails.numDays }).map((_, day) => (
            <div key={day} className="day-itinerary">
              <h3>Day {day + 1}</h3>
              <select
                onChange={(e) => handleItineraryChange(e.target.value, day)}
              >
                <option value="">Select Activity</option>
                {suggestedActivities.map((activity, index) => (
                  <option key={index} value={activity.name}>
                    {activity.name}
                  </option>
                ))}
              </select>
            </div>
          ))}
        </div>
      </div>

      <div className="trip-summary">
        <h2>Trip Summary</h2>
        <p>
          <strong>Trip Name:</strong> {tripDetails.tripName || "N/A"}
        </p>
        <p>
          <strong>Number of Days:</strong> {tripDetails.numDays}
        </p>
        <p>
          <strong>Destinations:</strong> {tripDetails.selectedPlaces.join(", ")}
        </p>
        <p>
          <strong>Trip Type:</strong> {tripDetails.tripType || "N/A"}
        </p>
        <p>
          <strong>Budget:</strong> ${tripDetails.budget || "N/A"}
        </p>
      </div>

      <button className="save-trip-btn" onClick={handleSaveTrip}>
        Save Trip
      </button>
    </div>
  );
};

export default TravelPlanner;
