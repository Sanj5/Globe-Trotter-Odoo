from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import json

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    photo_url = db.Column(db.String(255))
    language_preference = db.Column(db.String(10), default='en')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    trips = db.relationship('Trip', backref='user', lazy=True, cascade='all, delete-orphan')
    saved_destinations = db.relationship('SavedDestination', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'photo_url': self.photo_url,
            'language_preference': self.language_preference,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class City(db.Model):
    __tablename__ = 'cities'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    country = db.Column(db.String(100), nullable=False)
    region = db.Column(db.String(100))
    description = db.Column(db.Text)
    cost_index = db.Column(db.Float, default=1.0)  # Relative cost (1.0 = average)
    popularity_score = db.Column(db.Integer, default=0)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    image_url = db.Column(db.String(255))
    
    # Relationships
    activities = db.relationship('Activity', backref='city', lazy=True)
    stops = db.relationship('Stop', backref='city', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'country': self.country,
            'region': self.region,
            'description': self.description,
            'cost_index': self.cost_index,
            'popularity_score': self.popularity_score,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'image_url': self.image_url
        }


class Activity(db.Model):
    __tablename__ = 'activities'
    
    id = db.Column(db.Integer, primary_key=True)
    city_id = db.Column(db.Integer, db.ForeignKey('cities.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50))  # sightseeing, food, adventure, culture, shopping
    estimated_cost = db.Column(db.Float, default=0.0)
    duration_hours = db.Column(db.Float, default=2.0)
    image_url = db.Column(db.String(255))
    
    # Relationships
    itinerary_activities = db.relationship('ItineraryActivity', backref='activity', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'city_id': self.city_id,
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'estimated_cost': self.estimated_cost,
            'duration_hours': self.duration_hours,
            'image_url': self.image_url
        }


class Trip(db.Model):
    __tablename__ = 'trips'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    cover_photo_url = db.Column(db.String(255))
    is_public = db.Column(db.Boolean, default=False)
    share_code = db.Column(db.String(50), unique=True)
    ai_itinerary = db.Column(db.Text)  # stored JSON from AI generator
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    stops = db.relationship('Stop', backref='trip', lazy=True, cascade='all, delete-orphan', order_by='Stop.order_index')
    budget = db.relationship('Budget', backref='trip', uselist=False, cascade='all, delete-orphan')
    
    def to_dict(self, include_stops=False):
        result = {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'description': self.description,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'cover_photo_url': self.cover_photo_url,
            'is_public': self.is_public,
            'share_code': self.share_code,
            'ai_itinerary': json.loads(self.ai_itinerary) if self.ai_itinerary else None,
            'stops_count': len(self.stops) if self.stops is not None else 0,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'total_days': (self.end_date - self.start_date).days + 1 if self.start_date and self.end_date else 0
        }
        
        if include_stops:
            result['stops'] = [stop.to_dict(include_activities=True) for stop in self.stops]
            result['budget'] = self.budget.to_dict() if self.budget else None
        
        return result


class Stop(db.Model):
    __tablename__ = 'stops'
    
    id = db.Column(db.Integer, primary_key=True)
    trip_id = db.Column(db.Integer, db.ForeignKey('trips.id'), nullable=False)
    city_id = db.Column(db.Integer, db.ForeignKey('cities.id'), nullable=False)
    order_index = db.Column(db.Integer, nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    notes = db.Column(db.Text)
    
    # Relationships
    itinerary_activities = db.relationship('ItineraryActivity', backref='stop', lazy=True, cascade='all, delete-orphan', order_by='ItineraryActivity.day_number, ItineraryActivity.time_of_day')
    
    def to_dict(self, include_activities=False):
        result = {
            'id': self.id,
            'trip_id': self.trip_id,
            'city_id': self.city_id,
            'city': self.city.to_dict() if self.city else None,
            'order_index': self.order_index,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'notes': self.notes,
            'duration_days': (self.end_date - self.start_date).days + 1 if self.start_date and self.end_date else 0
        }
        
        if include_activities:
            result['activities'] = [activity.to_dict() for activity in self.itinerary_activities]
        
        return result


class ItineraryActivity(db.Model):
    __tablename__ = 'itinerary_activities'
    
    id = db.Column(db.Integer, primary_key=True)
    stop_id = db.Column(db.Integer, db.ForeignKey('stops.id'), nullable=False)
    activity_id = db.Column(db.Integer, db.ForeignKey('activities.id'), nullable=False)
    day_number = db.Column(db.Integer, nullable=False)  # Which day of the stop
    time_of_day = db.Column(db.String(20))  # morning, afternoon, evening, night
    custom_notes = db.Column(db.Text)
    estimated_cost_override = db.Column(db.Float)  # Override activity's default cost
    
    def to_dict(self):
        return {
            'id': self.id,
            'stop_id': self.stop_id,
            'activity_id': self.activity_id,
            'activity': self.activity.to_dict() if self.activity else None,
            'day_number': self.day_number,
            'time_of_day': self.time_of_day,
            'custom_notes': self.custom_notes,
            'estimated_cost': self.estimated_cost_override or (self.activity.estimated_cost if self.activity else 0)
        }


class Budget(db.Model):
    __tablename__ = 'budgets'
    
    id = db.Column(db.Integer, primary_key=True)
    trip_id = db.Column(db.Integer, db.ForeignKey('trips.id'), nullable=False)
    total_budget = db.Column(db.Float, default=0.0)
    transport_cost = db.Column(db.Float, default=0.0)
    accommodation_cost = db.Column(db.Float, default=0.0)
    food_cost = db.Column(db.Float, default=0.0)
    activities_cost = db.Column(db.Float, default=0.0)
    misc_cost = db.Column(db.Float, default=0.0)
    currency = db.Column(db.String(10), default='INR')
    
    def to_dict(self):
        return {
            'id': self.id,
            'trip_id': self.trip_id,
            'total_budget': self.total_budget,
            'transport_cost': self.transport_cost,
            'accommodation_cost': self.accommodation_cost,
            'food_cost': self.food_cost,
            'activities_cost': self.activities_cost,
            'misc_cost': self.misc_cost,
            'currency': self.currency,
            'breakdown': {
                'transport': self.transport_cost,
                'accommodation': self.accommodation_cost,
                'food': self.food_cost,
                'activities': self.activities_cost,
                'misc': self.misc_cost
            }
        }


class SavedDestination(db.Model):
    __tablename__ = 'saved_destinations'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    city_id = db.Column(db.Integer, db.ForeignKey('cities.id'), nullable=False)
    saved_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    city = db.relationship('City', backref='saved_by_users')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'city': self.city.to_dict() if self.city else None,
            'saved_at': self.saved_at.isoformat() if self.saved_at else None
        }
