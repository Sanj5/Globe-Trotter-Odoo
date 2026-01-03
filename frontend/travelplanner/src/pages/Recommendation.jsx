import "../styles.css";

const Recommendation = () => {
  const recommendedPlaces = [
    { name: "Santorini", reason: "Romantic getaways" },
    { name: "Iceland", reason: "Adventure lovers" },
    { name: "Kyoto", reason: "Cultural heritage" },
  ];

  return (
    <div className="recommendation">
      <h1>Your Personalized Recommendations</h1>
      <p>Based on your preferences, we recommend these places:</p>

      <div className="recommendation-list">
        {recommendedPlaces.map((place, index) => (
          <div key={index} className="recommendation-card">
            <h3>{place.name}</h3>
            <p>Perfect for: {place.reason}</p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Recommendation;
