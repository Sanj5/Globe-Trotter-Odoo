from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from datetime import datetime, timedelta, date
from werkzeug.utils import secure_filename
import os
import uuid
import secrets
import json

from models import db, User, City, Activity, Trip, Stop, ItineraryActivity, Budget, SavedDestination
from sqlalchemy import text
from config import Config
from groq_service import GroqService

def _ensure_ai_itinerary_column():
    """Add ai_itinerary column to trips if missing (SQLite-friendly, no migration tooling)."""
    engine = db.engine
    with engine.connect() as conn:
        result = conn.execute(text("PRAGMA table_info(trips);"))
        rows = result.fetchall()
        # If table not yet created, skip
        if not rows:
            return
        columns = {row[1] for row in rows}
        if 'ai_itinerary' not in columns:
            conn.execute(text("ALTER TABLE trips ADD COLUMN ai_itinerary TEXT;"))
            conn.commit()

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
CORS(app, resources={r"/api/*": {"origins": ["http://localhost:5173", "http://localhost:5174", "http://127.0.0.1:5173", "http://127.0.0.1:5174"]}}, supports_credentials=True)
db.init_app(app)

# Session-based auth
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Compatibility helpers to replace previous JWT usage
def jwt_required():
    return login_required

def get_jwt_identity():
    return current_user.id if current_user.is_authenticated else None

def create_access_token(identity):
    # Session cookie handles auth; token retained only for response compatibility
    return 'session-token'

# Initialize Groq service
groq_service = GroqService(app.config['GROQ_API_KEY'])

# Create upload folder
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# ==================== AUTHENTICATION ENDPOINTS ====================

@app.route('/api/auth/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.json
        email = data.get('email')
        password = data.get('password')
        name = data.get('name')
        
        if not email or not password or not name:
            return jsonify({'error': 'Email, password, and name are required'}), 400
        
        # Check if user exists
        if User.query.filter_by(email=email).first():
            return jsonify({'error': 'Email already registered'}), 409
        
        # Create new user
        user = User(email=email, name=name)
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()

        # Log the user in (session cookie)
        login_user(user)
        
        return jsonify({
            'message': 'User registered successfully',
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/api/auth/login', methods=['POST'])
def login():
    """Login user"""
    try:
        data = request.json
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        
        user = User.query.filter_by(email=email).first()
        
        if not user or not user.check_password(password):
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Start user session
        login_user(user)
        
        return jsonify({
            'message': 'Login successful',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/auth/logout', methods=['POST'])
@login_required
def logout():
    """Logout user and clear session"""
    logout_user()
    return jsonify({'message': 'Logged out successfully'}), 200


@app.route('/api/auth/me', methods=['GET'])
@login_required
def get_current_user():
    """Get current authenticated user"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({'user': user.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== USER PROFILE ENDPOINTS ====================

@app.route('/api/users/profile', methods=['PUT'])
@login_required
def update_profile():
    """Update user profile"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.json
        
        if 'name' in data:
            user.name = data['name']
        if 'photo_url' in data:
            user.photo_url = data['photo_url']
        if 'language_preference' in data:
            user.language_preference = data['language_preference']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Profile updated successfully',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/api/users/profile', methods=['DELETE'])
@login_required
def delete_account():
    """Delete user account"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({'message': 'Account deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ==================== CITY ENDPOINTS ====================

@app.route('/api/cities/search', methods=['GET'])
def search_cities():
    """Search cities by name, country, or region"""
    try:
        query = request.args.get('q', '').strip()
        country = request.args.get('country', '').strip()
        region = request.args.get('region', '').strip()
        limit = request.args.get('limit', 20, type=int)
        
        cities_query = City.query
        
        if query:
            cities_query = cities_query.filter(
                db.or_(
                    City.name.ilike(f'%{query}%'),
                    City.country.ilike(f'%{query}%')
                )
            )
        
        if country:
            cities_query = cities_query.filter(City.country.ilike(f'%{country}%'))
        
        if region:
            cities_query = cities_query.filter(City.region.ilike(f'%{region}%'))
        
        cities = cities_query.order_by(City.popularity_score.desc()).limit(limit).all()
        
        return jsonify({
            'cities': [city.to_dict() for city in cities],
            'count': len(cities)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/cities/<int:city_id>', methods=['GET'])
def get_city(city_id):
    """Get city details"""
    try:
        city = City.query.get(city_id)
        
        if not city:
            return jsonify({'error': 'City not found'}), 404
        
        return jsonify({'city': city.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/cities/<int:city_id>/info', methods=['GET'])
def get_city_ai_info(city_id):
    """Get AI-generated city information"""
    try:
        city = City.query.get(city_id)
        
        if not city:
            return jsonify({'error': 'City not found'}), 404
        
        # Get AI-generated info
        info = groq_service.get_city_info(city.name, city.country)
        
        return jsonify(info), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== ACTIVITY ENDPOINTS ====================

@app.route('/api/activities/suggest', methods=['POST'])
def suggest_activities():
    """Get AI-suggested activities for a city"""
    try:
        data = request.json
        city_name = data.get('city_name')
        interests = data.get('interests', [])
        budget = data.get('budget_per_activity')
        
        if not city_name:
            return jsonify({'error': 'City name is required'}), 400
        
        suggestions = groq_service.suggest_activities(city_name, interests, budget)
        
        return jsonify(suggestions), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== TRIP ENDPOINTS ====================

@app.route('/api/trips', methods=['GET'])
@login_required
def get_user_trips():
    """Get all trips for current user"""
    try:
        user_id = get_jwt_identity()
        trips = Trip.query.filter_by(user_id=user_id).order_by(Trip.created_at.desc()).all()
        
        return jsonify({
            'trips': [trip.to_dict() for trip in trips],
            'count': len(trips)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/trips', methods=['POST'])
@login_required
def create_trip():
    """Create a new trip"""
    try:
        user_id = get_jwt_identity()
        data = request.json
        
        name = data.get('name')
        start_date = datetime.fromisoformat(data.get('start_date')).date()
        end_date = datetime.fromisoformat(data.get('end_date')).date()
        description = data.get('description', '')
        cover_photo_url = data.get('cover_photo_url', '')
        
        if not name or not start_date or not end_date:
            return jsonify({'error': 'Name, start_date, and end_date are required'}), 400
        
        if start_date > end_date:
            return jsonify({'error': 'Start date must be before end date'}), 400
        
        # Create trip
        trip = Trip(
            user_id=user_id,
            name=name,
            description=description,
            start_date=start_date,
            end_date=end_date,
            cover_photo_url=cover_photo_url,
            share_code=secrets.token_urlsafe(8)
        )
        
        db.session.add(trip)
        db.session.commit()
        
        # Create empty budget
        budget = Budget(trip_id=trip.id)
        db.session.add(budget)
        db.session.commit()
        
        return jsonify({
            'message': 'Trip created successfully',
            'trip': trip.to_dict(include_stops=True)
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/api/trips/<int:trip_id>', methods=['GET'])
@login_required
def get_trip(trip_id):
    """Get trip details"""
    try:
        user_id = get_jwt_identity()
        trip = Trip.query.get(trip_id)
        
        if not trip:
            return jsonify({'error': 'Trip not found'}), 404
        
        if trip.user_id != user_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        return jsonify({'trip': trip.to_dict(include_stops=True)}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/trips/<int:trip_id>', methods=['PUT'])
@login_required
def update_trip(trip_id):
    """Update trip"""
    try:
        user_id = get_jwt_identity()
        trip = Trip.query.get(trip_id)
        
        if not trip:
            return jsonify({'error': 'Trip not found'}), 404
        
        if trip.user_id != user_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        data = request.json
        
        if 'name' in data:
            trip.name = data['name']
        if 'description' in data:
            trip.description = data['description']
        if 'start_date' in data:
            trip.start_date = datetime.fromisoformat(data['start_date']).date()
        if 'end_date' in data:
            trip.end_date = datetime.fromisoformat(data['end_date']).date()
        if 'cover_photo_url' in data:
            trip.cover_photo_url = data['cover_photo_url']
        if 'is_public' in data:
            trip.is_public = data['is_public']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Trip updated successfully',
            'trip': trip.to_dict(include_stops=True)
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/api/trips/<int:trip_id>', methods=['DELETE'])
@login_required
def delete_trip(trip_id):
    """Delete trip"""
    try:
        user_id = get_jwt_identity()
        trip = Trip.query.get(trip_id)
        
        if not trip:
            return jsonify({'error': 'Trip not found'}), 404
        
        if trip.user_id != user_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        db.session.delete(trip)
        db.session.commit()
        
        return jsonify({'message': 'Trip deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ==================== STOP (CITY) ENDPOINTS ====================

@app.route('/api/trips/<int:trip_id>/stops', methods=['POST'])
@login_required
def add_stop(trip_id):
    """Add a city stop to trip"""
    try:
        user_id = get_jwt_identity()
        trip = Trip.query.get(trip_id)
        
        if not trip:
            return jsonify({'error': 'Trip not found'}), 404
        
        if trip.user_id != user_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        data = request.json
        city_id = data.get('city_id')
        start_date = datetime.fromisoformat(data.get('start_date')).date()
        end_date = datetime.fromisoformat(data.get('end_date')).date()
        notes = data.get('notes', '')
        insert_order = data.get('order_index')
        
        if not city_id or not start_date or not end_date:
            return jsonify({'error': 'city_id, start_date, and end_date are required'}), 400
        
        # Determine order index (supports inserting in the middle)
        max_order = db.session.query(db.func.max(Stop.order_index)).filter_by(trip_id=trip_id).scalar() or 0
        if insert_order is None:
            order_index = max_order + 1
        else:
            try:
                order_index = int(insert_order)
            except ValueError:
                return jsonify({'error': 'order_index must be an integer'}), 400
            order_index = max(1, min(order_index, max_order + 1))
            if order_index <= max_order:
                # Shift existing stops down to make room
                Stop.query.filter(Stop.trip_id == trip_id, Stop.order_index >= order_index).update({Stop.order_index: Stop.order_index + 1}, synchronize_session=False)
        
        stop = Stop(
            trip_id=trip_id,
            city_id=city_id,
            order_index=order_index,
            start_date=start_date,
            end_date=end_date,
            notes=notes
        )
        
        db.session.add(stop)
        db.session.commit()
        
        return jsonify({
            'message': 'Stop added successfully',
            'stop': stop.to_dict(include_activities=True)
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/api/stops/<int:stop_id>', methods=['PUT'])
@login_required
def update_stop(stop_id):
    """Update a stop"""
    try:
        user_id = get_jwt_identity()
        stop = Stop.query.get(stop_id)
        
        if not stop:
            return jsonify({'error': 'Stop not found'}), 404
        
        if stop.trip.user_id != user_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        data = request.json
        
        if 'start_date' in data:
            stop.start_date = datetime.fromisoformat(data['start_date']).date()
        if 'end_date' in data:
            stop.end_date = datetime.fromisoformat(data['end_date']).date()
        if 'notes' in data:
            stop.notes = data['notes']
        if 'order_index' in data:
            total = Stop.query.filter_by(trip_id=stop.trip_id).count()
            try:
                new_order = int(data['order_index'])
            except ValueError:
                return jsonify({'error': 'order_index must be an integer'}), 400
            new_order = max(1, min(new_order, total))
            old_order = stop.order_index
            if new_order != old_order:
                if new_order < old_order:
                    # Shift down: increment those in target range
                    Stop.query.filter(
                        Stop.trip_id == stop.trip_id,
                        Stop.order_index >= new_order,
                        Stop.order_index < old_order
                    ).update({Stop.order_index: Stop.order_index + 1}, synchronize_session=False)
                else:
                    # Shift up: decrement those between old and new
                    Stop.query.filter(
                        Stop.trip_id == stop.trip_id,
                        Stop.order_index <= new_order,
                        Stop.order_index > old_order
                    ).update({Stop.order_index: Stop.order_index - 1}, synchronize_session=False)
                stop.order_index = new_order
        
        db.session.commit()
        
        return jsonify({
            'message': 'Stop updated successfully',
            'stop': stop.to_dict(include_activities=True)
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/api/stops/<int:stop_id>', methods=['DELETE'])
@login_required
def delete_stop(stop_id):
    """Delete a stop"""
    try:
        user_id = get_jwt_identity()
        stop = Stop.query.get(stop_id)
        
        if not stop:
            return jsonify({'error': 'Stop not found'}), 404
        
        if stop.trip.user_id != user_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        db.session.delete(stop)
        db.session.commit()
        
        return jsonify({'message': 'Stop deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ==================== ITINERARY ACTIVITY ENDPOINTS ====================

@app.route('/api/stops/<int:stop_id>/activities', methods=['POST'])
@login_required
def add_activity_to_stop(stop_id):
    """Add an activity to a stop"""
    try:
        user_id = get_jwt_identity()
        stop = Stop.query.get(stop_id)
        
        if not stop:
            return jsonify({'error': 'Stop not found'}), 404
        
        if stop.trip.user_id != user_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        data = request.json
        activity_id = data.get('activity_id')
        day_number = data.get('day_number', 1)
        time_of_day = data.get('time_of_day', 'morning')
        custom_notes = data.get('custom_notes', '')
        estimated_cost_override = data.get('estimated_cost_override')
        
        if not activity_id:
            return jsonify({'error': 'activity_id is required'}), 400
        
        itinerary_activity = ItineraryActivity(
            stop_id=stop_id,
            activity_id=activity_id,
            day_number=day_number,
            time_of_day=time_of_day,
            custom_notes=custom_notes,
            estimated_cost_override=estimated_cost_override
        )
        
        db.session.add(itinerary_activity)
        db.session.commit()
        
        return jsonify({
            'message': 'Activity added to itinerary',
            'activity': itinerary_activity.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/api/itinerary-activities/<int:activity_id>', methods=['DELETE'])
@login_required
def remove_activity_from_itinerary(activity_id):
    """Remove an activity from itinerary"""
    try:
        user_id = get_jwt_identity()
        itinerary_activity = ItineraryActivity.query.get(activity_id)
        
        if not itinerary_activity:
            return jsonify({'error': 'Activity not found'}), 404
        
        if itinerary_activity.stop.trip.user_id != user_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        db.session.delete(itinerary_activity)
        db.session.commit()
        
        return jsonify({'message': 'Activity removed from itinerary'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ==================== ACTIVITY SEARCH & BROWSE ENDPOINTS ====================

@app.route('/api/cities/<int:city_id>/activities', methods=['GET'])
@login_required
def browse_activities_by_city(city_id):
    """Browse activities in a city with filters"""
    try:
        city = City.query.get(city_id)
        
        if not city:
            return jsonify({'error': 'City not found'}), 404
        
        # Get filter parameters
        category = request.args.get('category')  # sightseeing, food, adventure, culture, shopping
        max_cost = request.args.get('max_cost', type=float)
        max_duration = request.args.get('max_duration', type=float)
        limit = request.args.get('limit', 20, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        query = Activity.query.filter_by(city_id=city_id)
        
        # Apply filters
        if category:
            query = query.filter_by(category=category)
        
        if max_cost is not None:
            query = query.filter(Activity.estimated_cost <= max_cost)
        
        if max_duration is not None:
            query = query.filter(Activity.duration_hours <= max_duration)
        
        # Get total count
        total_count = query.count()
        
        # If no activities in DB, generate using Groq
        if total_count == 0:
            try:
                ai_activities = groq_service.suggest_activities(city.name, ['cultural', 'adventure', 'food'], budget_per_activity=1500)
                
                # Save generated activities to database
                if ai_activities and 'activities' in ai_activities:
                    for act_data in ai_activities['activities']:
                        new_activity = Activity(
                            city_id=city_id,
                            name=act_data.get('name', 'Activity'),
                            description=act_data.get('description', ''),
                            category=act_data.get('category', 'sightseeing'),
                            estimated_cost=act_data.get('estimated_cost', 1000),
                            duration_hours=act_data.get('duration_hours', 2.0)
                        )
                        db.session.add(new_activity)
                    db.session.commit()
                    # Re-query after adding activities
                    query = Activity.query.filter_by(city_id=city_id)
                    if category:
                        query = query.filter_by(category=category)
                    if max_cost is not None:
                        query = query.filter(Activity.estimated_cost <= max_cost)
                    if max_duration is not None:
                        query = query.filter(Activity.duration_hours <= max_duration)
                    total_count = query.count()
            except Exception as groq_err:
                print(f"Groq error generating activities: {groq_err}")
                # Continue with empty results if Groq fails
                pass
        
        # Apply pagination
        activities = query.order_by(Activity.estimated_cost).limit(limit).offset(offset).all()
        
        return jsonify({
            'city': city.to_dict(),
            'activities': [a.to_dict() for a in activities],
            'pagination': {
                'total': total_count,
                'limit': limit,
                'offset': offset,
                'has_more': (offset + limit) < total_count
            },
            'available_categories': ['sightseeing', 'food', 'adventure', 'culture', 'shopping']
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/activities/search', methods=['GET'])
@login_required
def search_activities():
    """Search activities across all cities"""
    try:
        query_str = request.args.get('q', '').strip()
        category = request.args.get('category')
        max_cost = request.args.get('max_cost', type=float)
        city_id = request.args.get('city_id', type=int)
        limit = request.args.get('limit', 20, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        query = Activity.query
        
        # Text search on name and description
        if query_str:
            query = query.filter(
                (Activity.name.ilike(f'%{query_str}%')) |
                (Activity.description.ilike(f'%{query_str}%'))
            )
        
        # Filter by category
        if category:
            query = query.filter_by(category=category)
        
        # Filter by cost
        if max_cost is not None:
            query = query.filter(Activity.estimated_cost <= max_cost)
        
        # Filter by city
        if city_id:
            query = query.filter_by(city_id=city_id)
        
        total_count = query.count()
        
        # If no results found and searching by city, try Groq
        if total_count == 0 and city_id:
            try:
                city = City.query.get(city_id)
                if city:
                    interests = []
                    if category:
                        interests.append(category)
                    if not interests:
                        interests = ['cultural', 'adventure', 'food']
                    
                    ai_activities = groq_service.suggest_activities(city.name, interests, budget_per_activity=max_cost or 1500)
                    
                    # Save generated activities to database
                    if ai_activities and 'activities' in ai_activities:
                        for act_data in ai_activities['activities']:
                            new_activity = Activity(
                                city_id=city_id,
                                name=act_data.get('name', 'Activity'),
                                description=act_data.get('description', ''),
                                category=act_data.get('category', 'sightseeing'),
                                estimated_cost=act_data.get('estimated_cost', 1000),
                                duration_hours=act_data.get('duration_hours', 2.0)
                            )
                            db.session.add(new_activity)
                        db.session.commit()
                        # Re-query after adding activities
                        query = Activity.query
                        if query_str:
                            query = query.filter(
                                (Activity.name.ilike(f'%{query_str}%')) |
                                (Activity.description.ilike(f'%{query_str}%'))
                            )
                        if category:
                            query = query.filter_by(category=category)
                        if max_cost is not None:
                            query = query.filter(Activity.estimated_cost <= max_cost)
                        if city_id:
                            query = query.filter_by(city_id=city_id)
                        total_count = query.count()
            except Exception as groq_err:
                print(f"Groq error generating activities: {groq_err}")
                pass
        
        activities = query.order_by(Activity.estimated_cost).limit(limit).offset(offset).all()
        
        return jsonify({
            'activities': [a.to_dict() for a in activities],
            'pagination': {
                'total': total_count,
                'limit': limit,
                'offset': offset,
                'has_more': (offset + limit) < total_count
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/activities/categories', methods=['GET'])
@login_required
def get_activity_categories():
    """Get all available activity categories with stats"""
    try:
        categories = ['sightseeing', 'food', 'adventure', 'culture', 'shopping']
        
        stats = {}
        for cat in categories:
            count = Activity.query.filter_by(category=cat).count()
            avg_cost = db.session.query(db.func.avg(Activity.estimated_cost)).filter_by(category=cat).scalar()
            stats[cat] = {
                'count': count,
                'average_cost': float(avg_cost) if avg_cost else 0
            }
        
        return jsonify({
            'categories': categories,
            'stats': stats
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/cities/<int:city_id>/activities/refresh', methods=['POST'])
@login_required
def refresh_activities_for_city(city_id):
    """Refresh/update activities for a city using Groq AI"""
    try:
        city = City.query.get(city_id)
        if not city:
            return jsonify({'error': 'City not found'}), 404
        
        # Get interests from request or use defaults
        data = request.json or {}
        interests = data.get('interests', ['cultural', 'adventure', 'food'])
        max_budget = data.get('max_budget', 2000)
        
        try:
            # Generate new activities using Groq
            ai_activities = groq_service.suggest_activities(city.name, interests, budget_per_activity=max_budget)
            
            new_activities_count = 0
            if ai_activities and 'activities' in ai_activities:
                for act_data in ai_activities['activities']:
                    # Check if activity already exists
                    existing = Activity.query.filter_by(
                        city_id=city_id,
                        name=act_data.get('name', '')
                    ).first()
                    
                    if not existing:
                        new_activity = Activity(
                            city_id=city_id,
                            name=act_data.get('name', 'Activity'),
                            description=act_data.get('description', ''),
                            category=act_data.get('category', 'sightseeing'),
                            estimated_cost=act_data.get('estimated_cost', 1000),
                            duration_hours=act_data.get('duration_hours', 2.0)
                        )
                        db.session.add(new_activity)
                        new_activities_count += 1
                
                if new_activities_count > 0:
                    db.session.commit()
            
            # Get all activities for the city
            all_activities = Activity.query.filter_by(city_id=city_id).all()
            
            return jsonify({
                'message': f'Refreshed activities for {city.name}',
                'new_activities_added': new_activities_count,
                'total_activities': len(all_activities),
                'activities': [a.to_dict() for a in all_activities]
            }), 200
            
        except Exception as groq_err:
            return jsonify({
                'error': f'Failed to generate activities: {str(groq_err)}'
            }), 500
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== BUDGET ENDPOINTS ====================

@app.route('/api/trips/<int:trip_id>/budget', methods=['GET'])
@login_required
def get_trip_budget(trip_id):
    """Get budget for a trip"""
    try:
        user_id = get_jwt_identity()
        trip = Trip.query.get(trip_id)
        
        if not trip:
            return jsonify({'error': 'Trip not found'}), 404
        
        if trip.user_id != user_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        if not trip.budget:
            # Create budget if not exists
            budget = Budget(trip_id=trip_id)
            db.session.add(budget)
            db.session.commit()
        
        # Calculate activities cost
        activities_cost = 0
        for stop in trip.stops:
            for activity in stop.itinerary_activities:
                activities_cost += activity.estimated_cost_override or activity.activity.estimated_cost
        
        trip.budget.activities_cost = activities_cost
        
        # Calculate total
        trip.budget.total_budget = (
            trip.budget.transport_cost +
            trip.budget.accommodation_cost +
            trip.budget.food_cost +
            trip.budget.activities_cost +
            trip.budget.misc_cost
        )
        
        db.session.commit()
        
        return jsonify({'budget': trip.budget.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/trips/<int:trip_id>/budget', methods=['PUT'])
@login_required
def update_trip_budget(trip_id):
    """Update budget for a trip"""
    try:
        user_id = get_jwt_identity()
        trip = Trip.query.get(trip_id)
        
        if not trip:
            return jsonify({'error': 'Trip not found'}), 404
        
        if trip.user_id != user_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        if not trip.budget:
            budget = Budget(trip_id=trip_id)
            db.session.add(budget)
        else:
            budget = trip.budget
        
        data = request.json
        
        if 'transport_cost' in data:
            budget.transport_cost = data['transport_cost']
        if 'accommodation_cost' in data:
            budget.accommodation_cost = data['accommodation_cost']
        if 'food_cost' in data:
            budget.food_cost = data['food_cost']
        if 'misc_cost' in data:
            budget.misc_cost = data['misc_cost']
        if 'currency' in data:
            budget.currency = data['currency']
        
        # Recalculate total
        budget.total_budget = (
            budget.transport_cost +
            budget.accommodation_cost +
            budget.food_cost +
            budget.activities_cost +
            budget.misc_cost
        )
        
        db.session.commit()
        
        return jsonify({
            'message': 'Budget updated successfully',
            'budget': budget.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ==================== AI ITINERARY GENERATION ====================

@app.route('/api/trips/<int:trip_id>/generate-itinerary', methods=['POST'])
@login_required
def generate_ai_itinerary(trip_id):
    """Generate AI itinerary for a trip"""
    try:
        user_id = get_jwt_identity()
        trip = Trip.query.get(trip_id)
        
        if not trip:
            return jsonify({'error': 'Trip not found'}), 404
        
        if trip.user_id != user_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        data = request.json
        budget_min = data.get('budget_min', 1000)
        budget_max = data.get('budget_max', 5000)
        preferences = data.get('preferences', [])
        
        # Build destination string from all stops (fallback to trip name)
        destination = trip.name
        if trip.stops:
            stop_names = [stop.city.name for stop in trip.stops if stop.city and stop.city.name]
            if stop_names:
                # Deduplicate while keeping order
                seen = set()
                ordered_unique = []
                for nm in stop_names:
                    if nm not in seen:
                        seen.add(nm)
                        ordered_unique.append(nm)
                destination = ", ".join(ordered_unique)
        
        days = (trip.end_date - trip.start_date).days + 1
        
        # Generate itinerary
        itinerary_data = groq_service.generate_itinerary(
            destination, days, budget_min, budget_max, preferences
        )

        # Persist AI itinerary to trip for future display
        trip.ai_itinerary = json.dumps(itinerary_data)
        db.session.commit()
        
        return jsonify({
            'message': 'Itinerary generated successfully',
            'itinerary': itinerary_data
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== SHARED/PUBLIC TRIP ENDPOINTS ====================

@app.route('/api/trips/shared/<share_code>', methods=['GET'])
def get_shared_trip(share_code):
    """Get public/shared trip"""
    try:
        trip = Trip.query.filter_by(share_code=share_code).first()
        
        if not trip:
            return jsonify({'error': 'Trip not found'}), 404
        
        if not trip.is_public:
            return jsonify({'error': 'Trip is not public'}), 403
        
        return jsonify({'trip': trip.to_dict(include_stops=True)}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/trips/<int:trip_id>/copy', methods=['POST'])
@login_required
def copy_trip(trip_id):
    """Copy a trip to current user's account"""
    try:
        user_id = get_jwt_identity()
        original_trip = Trip.query.get(trip_id)
        
        if not original_trip:
            return jsonify({'error': 'Trip not found'}), 404
        
        # Create new trip
        new_trip = Trip(
            user_id=user_id,
            name=f"{original_trip.name} (Copy)",
            description=original_trip.description,
            start_date=original_trip.start_date,
            end_date=original_trip.end_date,
            cover_photo_url=original_trip.cover_photo_url,
            share_code=secrets.token_urlsafe(8)
        )
        
        db.session.add(new_trip)
        db.session.flush()
        
        # Copy stops
        for stop in original_trip.stops:
            new_stop = Stop(
                trip_id=new_trip.id,
                city_id=stop.city_id,
                order_index=stop.order_index,
                start_date=stop.start_date,
                end_date=stop.end_date,
                notes=stop.notes
            )
            db.session.add(new_stop)
            db.session.flush()
            
            # Copy activities
            for activity in stop.itinerary_activities:
                new_activity = ItineraryActivity(
                    stop_id=new_stop.id,
                    activity_id=activity.activity_id,
                    day_number=activity.day_number,
                    time_of_day=activity.time_of_day,
                    custom_notes=activity.custom_notes,
                    estimated_cost_override=activity.estimated_cost_override
                )
                db.session.add(new_activity)
        
        # Copy budget
        if original_trip.budget:
            new_budget = Budget(
                trip_id=new_trip.id,
                total_budget=original_trip.budget.total_budget,
                transport_cost=original_trip.budget.transport_cost,
                accommodation_cost=original_trip.budget.accommodation_cost,
                food_cost=original_trip.budget.food_cost,
                activities_cost=original_trip.budget.activities_cost,
                misc_cost=original_trip.budget.misc_cost,
                currency=original_trip.budget.currency
            )
            db.session.add(new_budget)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Trip copied successfully',
            'trip': new_trip.to_dict(include_stops=True)
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ==================== SAVED DESTINATIONS ====================

@app.route('/api/saved-destinations', methods=['GET'])
@login_required
def get_saved_destinations():
    """Get user's saved destinations"""
    try:
        user_id = get_jwt_identity()
        saved = SavedDestination.query.filter_by(user_id=user_id).order_by(SavedDestination.saved_at.desc()).all()
        
        return jsonify({
            'destinations': [item.to_dict() for item in saved],
            'count': len(saved)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/saved-destinations', methods=['POST'])
@login_required
def save_destination():
    """Save a destination"""
    try:
        user_id = get_jwt_identity()
        data = request.json
        city_id = data.get('city_id')
        
        if not city_id:
            return jsonify({'error': 'city_id is required'}), 400
        
        # Check if already saved
        existing = SavedDestination.query.filter_by(user_id=user_id, city_id=city_id).first()
        if existing:
            return jsonify({'message': 'Destination already saved'}), 200
        
        saved = SavedDestination(user_id=user_id, city_id=city_id)
        db.session.add(saved)
        db.session.commit()
        
        return jsonify({
            'message': 'Destination saved successfully',
            'destination': saved.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/api/saved-destinations/<int:saved_id>', methods=['DELETE'])
@login_required
def remove_saved_destination(saved_id):
    """Remove a saved destination"""
    try:
        user_id = get_jwt_identity()
        saved = SavedDestination.query.get(saved_id)
        
        if not saved:
            return jsonify({'error': 'Saved destination not found'}), 404
        
        if saved.user_id != user_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        db.session.delete(saved)
        db.session.commit()
        
        return jsonify({'message': 'Destination removed from saved'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ==================== DASHBOARD/STATS ENDPOINTS ====================

@app.route('/api/dashboard/stats', methods=['GET'])
@login_required
def get_dashboard_stats():
    """Get dashboard statistics"""
    try:
        user_id = get_jwt_identity()
        
        # Count trips
        total_trips = Trip.query.filter_by(user_id=user_id).count()
        upcoming_trips = Trip.query.filter(
            Trip.user_id == user_id,
            Trip.start_date >= date.today()
        ).count()
        
        # Recent trips
        recent_trips = Trip.query.filter_by(user_id=user_id).order_by(Trip.updated_at.desc()).limit(5).all()
        
        # Saved destinations count
        saved_count = SavedDestination.query.filter_by(user_id=user_id).count()

        # Budget highlights
        budget_total = db.session.query(db.func.coalesce(db.func.sum(Budget.total_budget), 0.0)).join(Trip).filter(Trip.user_id == user_id).scalar()
        
        return jsonify({
            'total_trips': total_trips,
            'upcoming_trips': upcoming_trips,
            'saved_destinations': saved_count,
            'budget_total': float(budget_total) if budget_total is not None else 0.0,
            'recent_trips': [trip.to_dict() for trip in recent_trips]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/popular-cities', methods=['GET'])
def get_popular_cities():
    """Get popular cities"""
    try:
        limit = request.args.get('limit', 10, type=int)
        cities = City.query.order_by(City.popularity_score.desc()).limit(limit).all()
        
        return jsonify({
            'cities': [city.to_dict() for city in cities]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== HEALTH CHECK ====================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'GlobeTrotter API is running'
    }), 200


# ==================== DATABASE INITIALIZATION ====================

@app.cli.command()
def init_db():
    """Initialize database"""
    db.create_all()
    _ensure_ai_itinerary_column()
    print("Database initialized successfully!")


@app.cli.command()
def seed_db():
    """Seed database with sample data"""
    # Add sample cities
    cities_data = [
        {'name': 'Paris', 'country': 'France', 'region': 'Europe', 'cost_index': 1.5, 'popularity_score': 95},
        {'name': 'Tokyo', 'country': 'Japan', 'region': 'Asia', 'cost_index': 1.8, 'popularity_score': 90},
        {'name': 'New York', 'country': 'USA', 'region': 'North America', 'cost_index': 2.0, 'popularity_score': 92},
        {'name': 'London', 'country': 'UK', 'region': 'Europe', 'cost_index': 1.7, 'popularity_score': 88},
        {'name': 'Bali', 'country': 'Indonesia', 'region': 'Asia', 'cost_index': 0.6, 'popularity_score': 85},
        {'name': 'Barcelona', 'country': 'Spain', 'region': 'Europe', 'cost_index': 1.2, 'popularity_score': 87},
        {'name': 'Dubai', 'country': 'UAE', 'region': 'Middle East', 'cost_index': 1.6, 'popularity_score': 83},
        {'name': 'Rome', 'country': 'Italy', 'region': 'Europe', 'cost_index': 1.3, 'popularity_score': 89},
        # India
        {'name': 'Delhi', 'country': 'India', 'region': 'Asia', 'cost_index': 0.8, 'popularity_score': 90},
        {'name': 'Mumbai', 'country': 'India', 'region': 'Asia', 'cost_index': 1.0, 'popularity_score': 92},
        {'name': 'Bengaluru', 'country': 'India', 'region': 'Asia', 'cost_index': 0.9, 'popularity_score': 85},
        {'name': 'Hyderabad', 'country': 'India', 'region': 'Asia', 'cost_index': 0.8, 'popularity_score': 84},
        {'name': 'Chennai', 'country': 'India', 'region': 'Asia', 'cost_index': 0.85, 'popularity_score': 82},
        {'name': 'Kolkata', 'country': 'India', 'region': 'Asia', 'cost_index': 0.75, 'popularity_score': 80},
        {'name': 'Jaipur', 'country': 'India', 'region': 'Asia', 'cost_index': 0.7, 'popularity_score': 86},
        {'name': 'Agra', 'country': 'India', 'region': 'Asia', 'cost_index': 0.65, 'popularity_score': 88},
        {'name': 'Goa', 'country': 'India', 'region': 'Asia', 'cost_index': 0.7, 'popularity_score': 87},
        {'name': 'Udaipur', 'country': 'India', 'region': 'Asia', 'cost_index': 0.7, 'popularity_score': 84},
        {'name': 'Varanasi', 'country': 'India', 'region': 'Asia', 'cost_index': 0.6, 'popularity_score': 83},
        {'name': 'Rishikesh', 'country': 'India', 'region': 'Asia', 'cost_index': 0.55, 'popularity_score': 78},
    ]
    
    for city_data in cities_data:
        city = City(**city_data)
        db.session.add(city)
    
    db.session.commit()
    
    # Add sample activities for some cities
    cities_dict = {city.name: city.id for city in City.query.all()}
    
    activities_data = [
        # Paris
        {'city_name': 'Paris', 'name': 'Eiffel Tower Visit', 'category': 'sightseeing', 'cost': 1500, 'duration': 2.5, 'description': 'Iconic tower with panoramic views of Paris'},
        {'city_name': 'Paris', 'name': 'Louvre Museum', 'category': 'culture', 'cost': 1800, 'duration': 3.0, 'description': 'World\'s largest art museum'},
        {'city_name': 'Paris', 'name': 'Seine River Cruise', 'category': 'sightseeing', 'cost': 1200, 'duration': 1.5, 'description': 'Scenic boat tour of Paris'},
        {'city_name': 'Paris', 'name': 'French Cooking Class', 'category': 'food', 'cost': 2500, 'duration': 3.0, 'description': 'Learn to cook classic French dishes'},
        
        # Tokyo
        {'city_name': 'Tokyo', 'name': 'Senso-ji Temple', 'category': 'culture', 'cost': 800, 'duration': 2.0, 'description': 'Historic Buddhist temple'},
        {'city_name': 'Tokyo', 'name': 'Shibuya Crossing', 'category': 'sightseeing', 'cost': 500, 'duration': 1.0, 'description': 'World\'s busiest pedestrian crossing'},
        {'city_name': 'Tokyo', 'name': 'Sushi Making Class', 'category': 'food', 'cost': 3000, 'duration': 2.5, 'description': 'Learn authentic sushi preparation'},
        
        # Mumbai - Extended list with diverse activities
        {'city_name': 'Mumbai', 'name': 'Gateway of India', 'category': 'sightseeing', 'cost': 500, 'duration': 1.0, 'description': 'Iconic monument overlooking Arabian Sea'},
        {'city_name': 'Mumbai', 'name': 'Marine Drive Walk', 'category': 'sightseeing', 'cost': 0, 'duration': 1.5, 'description': 'Scenic waterfront promenade with sunset views'},
        {'city_name': 'Mumbai', 'name': 'Haji Ali Dargah', 'category': 'culture', 'cost': 200, 'duration': 1.0, 'description': 'Sacred Islamic shrine in the Arabian Sea'},
        {'city_name': 'Mumbai', 'name': 'Taj Mahal Palace Hotel Tour', 'category': 'culture', 'cost': 800, 'duration': 1.5, 'description': 'Iconic heritage hotel with architectural grandeur'},
        {'city_name': 'Mumbai', 'name': 'Street Food Tour in Chowpatty', 'category': 'food', 'cost': 1500, 'duration': 2.5, 'description': 'Explore Mumbai\'s famous street food scene'},
        {'city_name': 'Mumbai', 'name': 'Bollywood Studio Tour', 'category': 'culture', 'cost': 2000, 'duration': 3.0, 'description': 'Behind-the-scenes Bollywood experience'},
        {'city_name': 'Mumbai', 'name': 'Elefanta Caves Day Trip', 'category': 'sightseeing', 'cost': 2500, 'duration': 6.0, 'description': 'UNESCO World Heritage cave temples'},
        {'city_name': 'Mumbai', 'name': 'Dharavi Slum Tour', 'category': 'culture', 'cost': 1200, 'duration': 2.0, 'description': 'Authentic community experience in Asia\'s largest slum'},
        {'city_name': 'Mumbai', 'name': 'Crawford Market Exploration', 'category': 'shopping', 'cost': 1000, 'duration': 2.0, 'description': 'Historic market with colorful spices and goods'},
        {'city_name': 'Mumbai', 'name': 'Sunset Yoga at Chowpatty', 'category': 'adventure', 'cost': 500, 'duration': 1.5, 'description': 'Relaxing yoga session by the beach'},
        {'city_name': 'Mumbai', 'name': 'Food Tasting at Mahim', 'category': 'food', 'cost': 2000, 'duration': 2.0, 'description': 'Authentic Maharashtrian cuisine tasting'},
        {'city_name': 'Mumbai', 'name': 'Kala Ghoda Art District Walk', 'category': 'culture', 'cost': 800, 'duration': 2.0, 'description': 'Art galleries, street art and heritage buildings'},
        
        # Agra
        {'city_name': 'Agra', 'name': 'Taj Mahal', 'category': 'sightseeing', 'cost': 1500, 'duration': 3.0, 'description': 'UNESCO World Heritage monument'},
        {'city_name': 'Agra', 'name': 'Agra Fort', 'category': 'culture', 'cost': 1000, 'duration': 2.0, 'description': 'Historic Mughal fortress'},
        
        # Goa
        {'city_name': 'Goa', 'name': 'Beach Resort Relaxation', 'category': 'sightseeing', 'cost': 2000, 'duration': 4.0, 'description': 'Unwind on pristine beaches'},
        {'city_name': 'Goa', 'name': 'Water Sports Adventure', 'category': 'adventure', 'cost': 3000, 'duration': 3.0, 'description': 'Jet skiing, parasailing, and more'},
        {'city_name': 'Goa', 'name': 'Seafood Feast', 'category': 'food', 'cost': 1500, 'duration': 2.0, 'description': 'Traditional Goan seafood dinner'},
        
        # Delhi
        {'city_name': 'Delhi', 'name': 'Red Fort', 'category': 'sightseeing', 'cost': 800, 'duration': 2.0, 'description': 'Historic Mughal fortress'},
        {'city_name': 'Delhi', 'name': 'Old Delhi Walking Tour', 'category': 'culture', 'cost': 1000, 'duration': 2.5, 'description': 'Explore narrow lanes and bazaars'},
        {'city_name': 'Delhi', 'name': 'Yoga Class', 'category': 'adventure', 'cost': 500, 'duration': 1.5, 'description': 'Traditional yoga session'},
    ]
    
    for activity_data in activities_data:
        city_name = activity_data.pop('city_name')
        if city_name in cities_dict:
            activity = Activity(
                city_id=cities_dict[city_name],
                name=activity_data['name'],
                category=activity_data['category'],
                estimated_cost=activity_data['cost'],
                duration_hours=activity_data['duration'],
                description=activity_data['description']
            )
            db.session.add(activity)
    
    db.session.commit()
    print("Database seeded with sample data and activities!")


# ==================== RUN SERVER ====================

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        _ensure_ai_itinerary_column()
    app.run(debug=True, port=5000, host='0.0.0.0')
