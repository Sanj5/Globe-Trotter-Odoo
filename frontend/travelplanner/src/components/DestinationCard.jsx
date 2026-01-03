const DestinationCard = ({ place, onAddToPlanner }) => {
  return (
    <div className="destination-card">
      <img src={place.image} alt={place.name} />
      <h3>{place.name}</h3>
      <p>{place.description}</p>
      <button onClick={onAddToPlanner}>Add to Planner</button>
    </div>
  );
};

export default DestinationCard;
