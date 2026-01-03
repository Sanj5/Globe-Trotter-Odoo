import React from "react";
import { useParams } from "react-router-dom";
import tajMahal from "../assets/Tajmahal.jpeg";
import jaipur from "../assets/jaipur.jpeg";
import goa from "../assets/goa.jpeg";
import mysore from "../assets/mysore.jpeg";
import varanasi from "../assets/varanasi.jpeg";
import kerala from "../assets/kerala.jpeg";
import ranthambore from "../assets/ranthambore.jpeg";
import meenakshi from "../assets/meenakshitemple.jpeg";

const destinationDetails = [
  {
    name: "Taj Mahal",
    location: "Agra, Uttar Pradesh",
    description: "A symbol of love, this white marble mausoleum is a UNESCO World Heritage Site.",
    image: tajMahal,
    detailedDescription:
      "The Taj Mahal is an iconic mausoleum built by Emperor Shah Jahan in memory of his wife Mumtaz Mahal. It is an epitome of Mughal architecture and attracts millions of visitors every year.",
  },
  {
    name: "Jaipur - The Pink City",
    location: "Rajasthan",
    description: "Known for its palaces, forts, and vibrant culture.",
    image: jaipur,
    detailedDescription:
      "Jaipur, also known as the Pink City, is famous for its majestic forts, palaces, and vibrant markets. The city is a perfect blend of history and modernity.",
  },
  {
    name: "Goa Beaches",
    location: "Goa",
    description: "Famous for its golden beaches, nightlife, and Portuguese heritage.",
    image: goa,
    detailedDescription:
      "Goa is known for its beautiful beaches, vibrant nightlife, and rich Portuguese heritage. It attracts tourists from all over the world for its serene beaches and unique blend of culture.",
  },
  // Add detailed descriptions for other places here...
];

const DestinationDetail = () => {
  const { name } = useParams();
  const decodedName = decodeURIComponent(name); // Decode URL parameter

  console.log("Decoded Destination Name: ", decodedName); // Log to verify decoding works
  const destination = destinationDetails.find((place) => place.name === decodedName);

  if (!destination) {
    return <h2>Destination not found</h2>;
  }

  return (
    <div className="destination-detail">
      <h1>{destination.name}</h1>
      <img src={destination.image} alt={destination.name} className="destination-img" />
      <p><strong>Location:</strong> {destination.location}</p>
      <p><strong>Description:</strong> {destination.detailedDescription}</p>
    </div>
  );
};

export default DestinationDetail;
