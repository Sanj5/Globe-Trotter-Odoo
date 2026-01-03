import { useState } from "react";
import html2pdf from "html2pdf.js";
import "./explore.css";

const ItineraryPlanner = () => {
  const [destination, setDestination] = useState("");
  const [days, setDays] = useState("");
  const [budget, setBudget] = useState("");
  const [itinerary, setItinerary] = useState("");
  const [loading, setLoading] = useState(false);

  const fetchItinerary = async () => {
    if (!destination || !days || !budget) return;

    setLoading(true);
    setItinerary(""); // Clear previous itinerary

    try {
      const response = await fetch("http://localhost:5000/itinerary", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ destination, days, budget_range: budget }),
      });

      const data = await response.json();
      setItinerary(data.itinerary);

      // Add new trip to localStorage
      const savedTrips = JSON.parse(localStorage.getItem("savedTrips")) || [];
      const newTrip = {
        id: Date.now(),
        name: destination,
        description: `A ${days}-day trip planned with a budget of ₹${budget}`,
        image: `https://source.unsplash.com/400x300/?travel,${destination}`,
        itinerary: data.itinerary,
      };
      savedTrips.push(newTrip);
      localStorage.setItem("savedTrips", JSON.stringify(savedTrips));
    } catch (err) {
      console.error("Error:", err);
      setItinerary("❌ Failed to fetch itinerary. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const formatItinerary = (text) => {
    let formatted = text.replace(
      /(^|\n)([A-Za-z0-9\s]+:)/g,
      (match, p1, p2) => `${p1}<span style="color: #0077b6">${p2}</span>`
    );
    formatted = formatted.replace(/(?:\n|^)[\-\u2022]\s?(.*)/g, "\n• $1");
    return formatted;
  };

  const generatePDF = () => {
    const element = document.getElementById("itinerary-content");
    const options = {
      filename: `${destination}-itinerary.pdf`,
      image: { type: "jpeg", quality: 0.98 },
      html2canvas: { scale: 4 },
      jsPDF: { unit: "mm", format: "a4", orientation: "portrait" },
    };
    html2pdf().from(element).set(options).save();
  };

  return (
    <div className="explore">
      <h1>🌍 Personalized Travel Itinerary Planner</h1>
      <div className="search-container">
        <input
          type="text"
          placeholder="Enter Destination (e.g. Ooty)"
          value={destination}
          onChange={(e) => setDestination(e.target.value)}
        />
        <input
          type="number"
          min="1"
          placeholder="Number of Days"
          value={days}
          onChange={(e) => setDays(e.target.value)}
        />
        <input
          type="text"
          placeholder="Budget Range (e.g. 5000 - 8000)"
          value={budget}
          onChange={(e) => setBudget(e.target.value)}
        />
        <button onClick={fetchItinerary} className="search-button">
          {loading ? "Generating..." : "Generate Itinerary"}
        </button>
      </div>

      <div className="itinerary-output">
        {loading ? (
          <p>🧠 Generating itinerary, please wait...</p>
        ) : itinerary ? (
          <div
            id="itinerary-content"
            style={{ whiteSpace: "pre-wrap", lineHeight: "1.6" }}
            dangerouslySetInnerHTML={{ __html: formatItinerary(itinerary) }}
          />
        ) : (
          <p>Enter details above to get your plan!</p>
        )}
      </div>

      {/* Show the download button only if itinerary exists */}
      {itinerary && !loading && (
        <button onClick={generatePDF} className="download-button">
          Download Itinerary as PDF
        </button>
      )}
    </div>
  );
};

export default ItineraryPlanner;
