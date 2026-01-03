import React from "react";
import { Link } from "react-router-dom";
import "./Home.css";
import tajMahal from "../assets/Tajmahal.jpeg";
import jaipur from "../assets/jaipur.jpeg";
import goa from "../assets/goa.jpeg";
import mysore from "../assets/mysore.jpeg";
import varanasi from "../assets/varanasi.jpeg";
import kerala from "../assets/kerala.jpeg";
import ranthambore from "../assets/ranthambore.jpeg";
import meenakshi from "../assets/meenakshitemple.jpeg";

const popularDestinations = [
  {
    name: "Taj Mahal",
    location: "Agra, Uttar Pradesh",
    description: "A symbol of love, this white marble mausoleum is a UNESCO World Heritage Site.",
    image: tajMahal,
  },
  {
    name: "Jaipur - The Pink City",
    location: "Rajasthan",
    description: "Known for its palaces, forts, and vibrant culture.",
    image: jaipur,
  },
  {
    name: "Goa Beaches",
    location: "Goa",
    description: "Famous for its golden beaches, nightlife, and Portuguese heritage.",
    image: goa,
  },
  {
    name: "Mysore Palace",
    location: "Karnataka",
    description: "A historical palace that showcases Indo-Saracenic architecture.",
    image: mysore,
  },
  {
    name: "Varanasi Ghats",
    location: "Uttar Pradesh",
    description: "A spiritual city along the Ganges, known for its ghats and temples.",
    image: varanasi,
  },
  {
    name: "Kerala Backwaters",
    location: "Kerala",
    description: "Experience serene houseboat cruises through lush green landscapes.",
    image: kerala,
  },
  {
    name: "Ranthambore National Park",
    location: "Rajasthan",
    description: "A famous wildlife sanctuary home to majestic tigers and diverse flora & fauna.",
    image: ranthambore,
  },
  {
    name: "Meenakshi Temple",
    location: "Tamil Nadu",
    description: "A stunning Dravidian-style temple with vibrant sculptures in Madurai.",
    image: meenakshi,
  },
];

const Home = () => {
  return (
    <div className="home">
      <h1>Explore Popular Tourist Destinations in India</h1>
      <p>Discover breathtaking locations and plan your journey with ease!</p>

      <div className="destination-grid">
        {popularDestinations.map((place, index) => (
          <Link to={`/destination/${place.name}`} key={index} className="destination-card">
            <img src={place.image} alt={place.name} className="destination-img" />
            <div className="destination-info">
              <h3>{place.name}</h3>
              <p><strong>{place.location}</strong></p>
              <p>{place.description}</p>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
};

export default Home;
