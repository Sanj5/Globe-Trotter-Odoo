-- GlobeTrotter Database Initialization Script
-- PostgreSQL

-- Drop existing tables if they exist (be careful in production!)
DROP TABLE IF EXISTS saved_destinations CASCADE;
DROP TABLE IF EXISTS itinerary_activities CASCADE;
DROP TABLE IF EXISTS budgets CASCADE;
DROP TABLE IF EXISTS stops CASCADE;
DROP TABLE IF EXISTS activities CASCADE;
DROP TABLE IF EXISTS trips CASCADE;
DROP TABLE IF EXISTS cities CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- Create Users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(100) NOT NULL,
    photo_url VARCHAR(255),
    language_preference VARCHAR(10) DEFAULT 'en',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create Cities table
CREATE TABLE cities (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    country VARCHAR(100) NOT NULL,
    region VARCHAR(100),
    description TEXT,
    cost_index FLOAT DEFAULT 1.0,
    popularity_score INTEGER DEFAULT 0,
    latitude FLOAT,
    longitude FLOAT,
    image_url VARCHAR(255)
);

-- Create Activities table
CREATE TABLE activities (
    id SERIAL PRIMARY KEY,
    city_id INTEGER NOT NULL REFERENCES cities(id) ON DELETE CASCADE,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    category VARCHAR(50),
    estimated_cost FLOAT DEFAULT 0.0,
    duration_hours FLOAT DEFAULT 2.0,
    image_url VARCHAR(255)
);

-- Create Trips table
CREATE TABLE trips (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    cover_photo_url VARCHAR(255),
    is_public BOOLEAN DEFAULT FALSE,
    share_code VARCHAR(50) UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create Stops table
CREATE TABLE stops (
    id SERIAL PRIMARY KEY,
    trip_id INTEGER NOT NULL REFERENCES trips(id) ON DELETE CASCADE,
    city_id INTEGER NOT NULL REFERENCES cities(id) ON DELETE CASCADE,
    order_index INTEGER NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    notes TEXT
);

-- Create Itinerary Activities table
CREATE TABLE itinerary_activities (
    id SERIAL PRIMARY KEY,
    stop_id INTEGER NOT NULL REFERENCES stops(id) ON DELETE CASCADE,
    activity_id INTEGER NOT NULL REFERENCES activities(id) ON DELETE CASCADE,
    day_number INTEGER NOT NULL,
    time_of_day VARCHAR(20),
    custom_notes TEXT,
    estimated_cost_override FLOAT
);

-- Create Budgets table
CREATE TABLE budgets (
    id SERIAL PRIMARY KEY,
    trip_id INTEGER NOT NULL REFERENCES trips(id) ON DELETE CASCADE,
    total_budget FLOAT DEFAULT 0.0,
    transport_cost FLOAT DEFAULT 0.0,
    accommodation_cost FLOAT DEFAULT 0.0,
    food_cost FLOAT DEFAULT 0.0,
    activities_cost FLOAT DEFAULT 0.0,
    misc_cost FLOAT DEFAULT 0.0,
    currency VARCHAR(10) DEFAULT 'USD'
);

-- Create Saved Destinations table
CREATE TABLE saved_destinations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    city_id INTEGER NOT NULL REFERENCES cities(id) ON DELETE CASCADE,
    saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, city_id)
);

-- Create indexes for better performance
CREATE INDEX idx_trips_user_id ON trips(user_id);
CREATE INDEX idx_trips_share_code ON trips(share_code);
CREATE INDEX idx_stops_trip_id ON stops(trip_id);
CREATE INDEX idx_activities_city_id ON activities(city_id);
CREATE INDEX idx_itinerary_activities_stop_id ON itinerary_activities(stop_id);
CREATE INDEX idx_saved_destinations_user_id ON saved_destinations(user_id);

-- Insert sample cities
INSERT INTO cities (name, country, region, description, cost_index, popularity_score, latitude, longitude) VALUES
('Paris', 'France', 'Europe', 'The City of Light, known for the Eiffel Tower, art, and cuisine.', 1.5, 95, 48.8566, 2.3522),
('Tokyo', 'Japan', 'Asia', 'A bustling metropolis blending tradition and technology.', 1.8, 90, 35.6762, 139.6503),
('New York', 'USA', 'North America', 'The city that never sleeps, famous for Times Square and Central Park.', 2.0, 92, 40.7128, -74.0060),
('London', 'UK', 'Europe', 'Historic capital with iconic landmarks like Big Ben and Buckingham Palace.', 1.7, 88, 51.5074, -0.1278),
('Bali', 'Indonesia', 'Asia', 'Tropical paradise with beautiful beaches and temples.', 0.6, 85, -8.3405, 115.0920),
('Barcelona', 'Spain', 'Europe', 'Vibrant city known for Gaudi architecture and Mediterranean beaches.', 1.2, 87, 41.3851, 2.1734),
('Dubai', 'UAE', 'Middle East', 'Luxury destination with stunning skyscrapers and shopping.', 1.6, 83, 25.2048, 55.2708),
('Rome', 'Italy', 'Europe', 'Ancient city with Colosseum, Vatican, and delicious cuisine.', 1.3, 89, 41.9028, 12.4964),
('Bangkok', 'Thailand', 'Asia', 'Vibrant city with temples, street food, and nightlife.', 0.7, 86, 13.7563, 100.5018),
('Amsterdam', 'Netherlands', 'Europe', 'Charming city with canals, museums, and cycling culture.', 1.4, 84, 52.3676, 4.9041),
('Sydney', 'Australia', 'Oceania', 'Harbor city with Opera House and beautiful beaches.', 1.9, 87, -33.8688, 151.2093),
('Istanbul', 'Turkey', 'Europe/Asia', 'Historic city bridging two continents with rich culture.', 0.8, 85, 41.0082, 28.9784),
('Singapore', 'Singapore', 'Asia', 'Modern city-state with stunning gardens and diverse food.', 1.7, 88, 1.3521, 103.8198),
('Prague', 'Czech Republic', 'Europe', 'Medieval city with beautiful architecture and beer culture.', 0.9, 83, 50.0755, 14.4378),
('Lisbon', 'Portugal', 'Europe', 'Coastal capital with hills, trams, and pastel buildings.', 1.0, 82, 38.7223, -9.1393);

-- Insert sample activities for Paris
INSERT INTO activities (city_id, name, description, category, estimated_cost, duration_hours) VALUES
(1, 'Eiffel Tower Visit', 'Visit the iconic Eiffel Tower and enjoy panoramic city views.', 'sightseeing', 30, 2.5),
(1, 'Louvre Museum', 'Explore the world''s largest art museum with Mona Lisa.', 'culture', 20, 3.0),
(1, 'Seine River Cruise', 'Romantic boat cruise along the Seine River.', 'sightseeing', 25, 1.5),
(1, 'Montmartre Walking Tour', 'Explore the artistic neighborhood with Sacré-Cœur.', 'culture', 15, 2.0),
(1, 'French Cooking Class', 'Learn to cook authentic French cuisine.', 'food', 85, 3.5);

-- Insert sample activities for Tokyo
INSERT INTO activities (city_id, name, description, category, estimated_cost, duration_hours) VALUES
(2, 'Tokyo Skytree', 'Visit Japan''s tallest structure for breathtaking views.', 'sightseeing', 28, 2.0),
(2, 'Senso-ji Temple', 'Historic Buddhist temple in Asakusa district.', 'culture', 0, 1.5),
(2, 'Tsukiji Market Tour', 'Explore the famous fish market and try fresh sushi.', 'food', 40, 2.5),
(2, 'Shibuya Crossing', 'Experience the world''s busiest pedestrian crossing.', 'sightseeing', 0, 1.0),
(2, 'Sumo Wrestling Experience', 'Watch or participate in traditional sumo wrestling.', 'culture', 60, 2.0);

-- Insert sample activities for New York
INSERT INTO activities (city_id, name, description, category, estimated_cost, duration_hours) VALUES
(3, 'Statue of Liberty Tour', 'Ferry tour to the iconic Statue of Liberty.', 'sightseeing', 25, 3.0),
(3, 'Central Park Walk', 'Stroll through Manhattan''s famous urban park.', 'sightseeing', 0, 2.0),
(3, 'Broadway Show', 'Watch a world-class musical or play.', 'culture', 120, 2.5),
(3, 'Empire State Building', 'Observation deck with stunning NYC views.', 'sightseeing', 42, 1.5),
(3, 'Food Tour in Brooklyn', 'Taste diverse cuisines in Brooklyn neighborhoods.', 'food', 75, 3.0);

-- Insert sample activities for Bali
INSERT INTO activities (city_id, name, description, category, estimated_cost, duration_hours) VALUES
(5, 'Tanah Lot Temple', 'Visit the iconic sea temple at sunset.', 'culture', 5, 2.0),
(5, 'Rice Terrace Walk', 'Trek through stunning Tegallalang rice terraces.', 'sightseeing', 3, 2.5),
(5, 'Surfing Lesson', 'Learn to surf on Bali''s famous beaches.', 'adventure', 35, 2.0),
(5, 'Ubud Monkey Forest', 'Explore sanctuary with playful monkeys.', 'sightseeing', 7, 1.5),
(5, 'Balinese Spa Treatment', 'Relax with traditional massage and spa.', 'culture', 25, 2.0);

COMMENT ON TABLE users IS 'Stores user account information';
COMMENT ON TABLE cities IS 'Stores city information for trip planning';
COMMENT ON TABLE activities IS 'Stores activities available in each city';
COMMENT ON TABLE trips IS 'Stores user-created trips';
COMMENT ON TABLE stops IS 'Stores cities/stops within each trip';
COMMENT ON TABLE itinerary_activities IS 'Links activities to trip stops with scheduling info';
COMMENT ON TABLE budgets IS 'Stores budget information for each trip';
COMMENT ON TABLE saved_destinations IS 'Stores user-saved destinations for future reference';
