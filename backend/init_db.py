"""
Initialize SQLite database and seed with sample data
Run this once before starting the application: python init_db.py
"""

from app import app, db
from models import City, Activity
from datetime import datetime

def init_database():
    """Create all tables and seed initial data"""
    
    with app.app_context():
        # Drop all tables (if you want to reset)
        # db.drop_all()
        
        # Create all tables
        print("Creating database tables...")
        db.create_all()
        print("✅ Tables created successfully!")
        
        # Check if data already exists
        if City.query.first():
            print("⚠️  Database already contains data. Skipping seed.")
            return
        
        # Seed cities
        print("\nSeeding cities...")
        cities_data = [
            {'name': 'Paris', 'country': 'France', 'region': 'Europe', 
             'description': 'The City of Light, known for the Eiffel Tower, art, and cuisine.',
             'cost_index': 1.5, 'popularity_score': 95, 'latitude': 48.8566, 'longitude': 2.3522},
            
            {'name': 'Tokyo', 'country': 'Japan', 'region': 'Asia',
             'description': 'A bustling metropolis blending tradition and technology.',
             'cost_index': 1.8, 'popularity_score': 90, 'latitude': 35.6762, 'longitude': 139.6503},
            
            {'name': 'New York', 'country': 'USA', 'region': 'North America',
             'description': 'The city that never sleeps, famous for Times Square and Central Park.',
             'cost_index': 2.0, 'popularity_score': 92, 'latitude': 40.7128, 'longitude': -74.0060},
            
            {'name': 'London', 'country': 'UK', 'region': 'Europe',
             'description': 'Historic capital with iconic landmarks like Big Ben and Buckingham Palace.',
             'cost_index': 1.7, 'popularity_score': 88, 'latitude': 51.5074, 'longitude': -0.1278},
            
            {'name': 'Bali', 'country': 'Indonesia', 'region': 'Asia',
             'description': 'Tropical paradise with beautiful beaches and temples.',
             'cost_index': 0.6, 'popularity_score': 85, 'latitude': -8.3405, 'longitude': 115.0920},
            
            {'name': 'Barcelona', 'country': 'Spain', 'region': 'Europe',
             'description': 'Vibrant city known for Gaudi architecture and Mediterranean beaches.',
             'cost_index': 1.2, 'popularity_score': 87, 'latitude': 41.3851, 'longitude': 2.1734},
            
            {'name': 'Dubai', 'country': 'UAE', 'region': 'Middle East',
             'description': 'Luxury destination with stunning skyscrapers and shopping.',
             'cost_index': 1.6, 'popularity_score': 83, 'latitude': 25.2048, 'longitude': 55.2708},
            
            {'name': 'Rome', 'country': 'Italy', 'region': 'Europe',
             'description': 'Ancient city with Colosseum, Vatican, and delicious cuisine.',
             'cost_index': 1.3, 'popularity_score': 89, 'latitude': 41.9028, 'longitude': 12.4964},
            
            {'name': 'Bangkok', 'country': 'Thailand', 'region': 'Asia',
             'description': 'Vibrant city with temples, street food, and nightlife.',
             'cost_index': 0.7, 'popularity_score': 86, 'latitude': 13.7563, 'longitude': 100.5018},
            
            {'name': 'Amsterdam', 'country': 'Netherlands', 'region': 'Europe',
             'description': 'Charming city with canals, museums, and cycling culture.',
             'cost_index': 1.4, 'popularity_score': 84, 'latitude': 52.3676, 'longitude': 4.9041},
            
            {'name': 'Sydney', 'country': 'Australia', 'region': 'Oceania',
             'description': 'Harbor city with Opera House and beautiful beaches.',
             'cost_index': 1.9, 'popularity_score': 87, 'latitude': -33.8688, 'longitude': 151.2093},
            
            {'name': 'Istanbul', 'country': 'Turkey', 'region': 'Europe/Asia',
             'description': 'Historic city bridging two continents with rich culture.',
             'cost_index': 0.8, 'popularity_score': 85, 'latitude': 41.0082, 'longitude': 28.9784},
            
            {'name': 'Singapore', 'country': 'Singapore', 'region': 'Asia',
             'description': 'Modern city-state with stunning gardens and diverse food.',
             'cost_index': 1.7, 'popularity_score': 88, 'latitude': 1.3521, 'longitude': 103.8198},
            
            {'name': 'Prague', 'country': 'Czech Republic', 'region': 'Europe',
             'description': 'Medieval city with beautiful architecture and beer culture.',
             'cost_index': 0.9, 'popularity_score': 83, 'latitude': 50.0755, 'longitude': 14.4378},
            
            {'name': 'Lisbon', 'country': 'Portugal', 'region': 'Europe',
             'description': 'Coastal capital with hills, trams, and pastel buildings.',
             'cost_index': 1.0, 'popularity_score': 82, 'latitude': 38.7223, 'longitude': -9.1393},
        ]
        
        cities = []
        for city_data in cities_data:
            city = City(**city_data)
            db.session.add(city)
            cities.append(city)
        
        db.session.commit()
        print(f"✅ Added {len(cities)} cities")
        
        # Seed activities
        print("\nSeeding activities...")
        activities_data = [
            # Paris activities (city_id will be 1)
            {'city_id': 1, 'name': 'Eiffel Tower Visit', 'description': 'Visit the iconic Eiffel Tower and enjoy panoramic city views.',
             'category': 'sightseeing', 'estimated_cost': 30, 'duration_hours': 2.5},
            {'city_id': 1, 'name': 'Louvre Museum', 'description': 'Explore the world\'s largest art museum with Mona Lisa.',
             'category': 'culture', 'estimated_cost': 20, 'duration_hours': 3.0},
            {'city_id': 1, 'name': 'Seine River Cruise', 'description': 'Romantic boat cruise along the Seine River.',
             'category': 'sightseeing', 'estimated_cost': 25, 'duration_hours': 1.5},
            {'city_id': 1, 'name': 'Montmartre Walking Tour', 'description': 'Explore the artistic neighborhood with Sacré-Cœur.',
             'category': 'culture', 'estimated_cost': 15, 'duration_hours': 2.0},
            {'city_id': 1, 'name': 'French Cooking Class', 'description': 'Learn to cook authentic French cuisine.',
             'category': 'food', 'estimated_cost': 85, 'duration_hours': 3.5},
            
            # Tokyo activities (city_id will be 2)
            {'city_id': 2, 'name': 'Tokyo Skytree', 'description': 'Visit Japan\'s tallest structure for breathtaking views.',
             'category': 'sightseeing', 'estimated_cost': 28, 'duration_hours': 2.0},
            {'city_id': 2, 'name': 'Senso-ji Temple', 'description': 'Historic Buddhist temple in Asakusa district.',
             'category': 'culture', 'estimated_cost': 0, 'duration_hours': 1.5},
            {'city_id': 2, 'name': 'Tsukiji Market Tour', 'description': 'Explore the famous fish market and try fresh sushi.',
             'category': 'food', 'estimated_cost': 40, 'duration_hours': 2.5},
            {'city_id': 2, 'name': 'Shibuya Crossing', 'description': 'Experience the world\'s busiest pedestrian crossing.',
             'category': 'sightseeing', 'estimated_cost': 0, 'duration_hours': 1.0},
            {'city_id': 2, 'name': 'Sumo Wrestling Experience', 'description': 'Watch or participate in traditional sumo wrestling.',
             'category': 'culture', 'estimated_cost': 60, 'duration_hours': 2.0},
            
            # New York activities (city_id will be 3)
            {'city_id': 3, 'name': 'Statue of Liberty Tour', 'description': 'Ferry tour to the iconic Statue of Liberty.',
             'category': 'sightseeing', 'estimated_cost': 25, 'duration_hours': 3.0},
            {'city_id': 3, 'name': 'Central Park Walk', 'description': 'Stroll through Manhattan\'s famous urban park.',
             'category': 'sightseeing', 'estimated_cost': 0, 'duration_hours': 2.0},
            {'city_id': 3, 'name': 'Broadway Show', 'description': 'Watch a world-class musical or play.',
             'category': 'culture', 'estimated_cost': 120, 'duration_hours': 2.5},
            {'city_id': 3, 'name': 'Empire State Building', 'description': 'Observation deck with stunning NYC views.',
             'category': 'sightseeing', 'estimated_cost': 42, 'duration_hours': 1.5},
            {'city_id': 3, 'name': 'Food Tour in Brooklyn', 'description': 'Taste diverse cuisines in Brooklyn neighborhoods.',
             'category': 'food', 'estimated_cost': 75, 'duration_hours': 3.0},
            
            # Bali activities (city_id will be 5)
            {'city_id': 5, 'name': 'Tanah Lot Temple', 'description': 'Visit the iconic sea temple at sunset.',
             'category': 'culture', 'estimated_cost': 5, 'duration_hours': 2.0},
            {'city_id': 5, 'name': 'Rice Terrace Walk', 'description': 'Trek through stunning Tegallalang rice terraces.',
             'category': 'sightseeing', 'estimated_cost': 3, 'duration_hours': 2.5},
            {'city_id': 5, 'name': 'Surfing Lesson', 'description': 'Learn to surf on Bali\'s famous beaches.',
             'category': 'adventure', 'estimated_cost': 35, 'duration_hours': 2.0},
            {'city_id': 5, 'name': 'Ubud Monkey Forest', 'description': 'Explore sanctuary with playful monkeys.',
             'category': 'sightseeing', 'estimated_cost': 7, 'duration_hours': 1.5},
            {'city_id': 5, 'name': 'Balinese Spa Treatment', 'description': 'Relax with traditional massage and spa.',
             'category': 'culture', 'estimated_cost': 25, 'duration_hours': 2.0},
        ]
        
        for activity_data in activities_data:
            activity = Activity(**activity_data)
            db.session.add(activity)
        
        db.session.commit()
        print(f"✅ Added {len(activities_data)} activities")
        
        print("\n" + "="*50)
        print("🎉 Database initialized successfully!")
        print("="*50)
        print("\n📊 Summary:")
        print(f"   - {len(cities)} cities")
        print(f"   - {len(activities_data)} activities")
        print("\n✅ Ready to start the application!")
        print("   Run: python app.py\n")

if __name__ == '__main__':
    init_database()
