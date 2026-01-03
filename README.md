# GlobeTrotter - Complete Travel Planning Platform

A comprehensive, intelligent travel planning application that helps users design, organize, and share their travel experiences. Built with Flask, SQLite, Groq AI, and React.

## Features

### Complete Feature Set (All 13 Requirements)

1. **Login/Signup Screen** - User authentication with JWT tokens
2. **Dashboard/Home Screen** - Welcome page with stats, recent trips, and popular destinations
3. **Create Trip Screen** - Form to create new trips with dates and details
4. **My Trips Screen** - List view of all user trips with filtering
5. **Itinerary Builder** - Add cities, dates, and activities to trips
6. **Itinerary View** - Visual timeline/calendar of trip plans
7. **City Search** - Search and filter cities by location and cost
8. **Activity Search** - Browse and add activities by category
9. **Trip Budget & Cost Breakdown** - Detailed budget tracking and analysis
10. **Trip Calendar/Timeline** - Calendar-based itinerary visualization
11. **Shared/Public Itinerary** - Share trips via public links
12. **User Profile/Settings** - Manage profile and preferences
13. **AI-Powered Recommendations** - Groq AI for itinerary generation and suggestions

##  Tech Stack

### Backend
- **Flask** - Python web framework
- **SQLite** - Lightweight embedded database (no installation needed!)
- **SQLAlchemy** - ORM for database operations
- **Flask-JWT-Extended** - JWT authentication
- **Groq API** - AI-powered travel recommendations
- **Flask-CORS** - Cross-origin resource sharing

### Frontend
- **React** - UI framework
- **React Router** - Navigation
- **Axios** - HTTP client
- **Vite** - Build tool

##  Prerequisites

- Python 3.8+ (SQLite included)
- Node.js 16+
- Groq API key (provided)

## 🚀 Installation & Setup

### 1. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
# source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Initialize database with sample data
python init_db.py

# The .env file is already configured with:
# - Groq API key
# - SQLite database path (backend/globetrotter.db)
# - JWT secret keys

# Run the backend server
python app.py
```

The backend will run on `http://localhost:5000`

### 2. Frontend Setup

```bash
# Navigate to frontend directory
cd ../frontend/travelplanner

# Install dependencies
npm install

# Run development server
npm run dev
```

The frontend will run on `http://localhost:5173`

##  Project Structure

```
Globe-Trotter-Odoo/
├── backend/
│   ├── app.py                 # Main Flask application
│   ├── models.py              # Database models
│   ├── config.py              # Configuration
│   ├── groq_service.py        # Groq AI integration
│   ├── init_db.sql            # Database initialization
│   ├── requirements.txt       # Python dependencies
│   └── .env.example           # Environment variables template
│
└── frontend/
    └── travelplanner/
        ├── src/
        │   ├── components/    # React components
        │   ├── pages/         # Page components
        │   ├── services/      # API services
        │   ├── context/       # React context
        │   ├── App.jsx        # Main app component
        │   └── main.jsx       # Entry point
        ├── package.json
        └── vite.config.js
```

##  API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `GET /api/auth/me` - Get current user

### Trips
- `GET /api/trips` - Get all user trips
- `POST /api/trips` - Create new trip
- `GET /api/trips/:id` - Get trip details
- `PUT /api/trips/:id` - Update trip
- `DELETE /api/trips/:id` - Delete trip
- `POST /api/trips/:id/generate-itinerary` - AI generate itinerary
- `GET /api/trips/shared/:code` - Get shared trip
- `POST /api/trips/:id/copy` - Copy trip

### Cities & Activities
- `GET /api/cities/search` - Search cities
- `GET /api/cities/:id` - Get city details
- `GET /api/cities/:id/info` - Get AI city info
- `GET /api/activities/search` - Search activities
- `POST /api/activities/suggest` - AI suggest activities

### Stops & Itinerary
- `POST /api/trips/:id/stops` - Add stop to trip
- `PUT /api/stops/:id` - Update stop
- `DELETE /api/stops/:id` - Delete stop
- `POST /api/stops/:id/activities` - Add activity to stop
- `DELETE /api/itinerary-activities/:id` - Remove activity

### Budget
- `GET /api/trips/:id/budget` - Get trip budget
- `PUT /api/trips/:id/budget` - Update trip budget

### User Profile
- `PUT /api/users/profile` - Update profile
- `DELETE /api/users/profile` - Delete account

### Dashboard
- `GET /api/dashboard/stats` - Get dashboard statistics
- `GET /api/popular-cities` - Get popular cities

### Saved Destinations
- `GET /api/saved-destinations` - Get saved destinations
- `POST /api/saved-destinations` - Save destination
- `DELETE /api/saved-destinations/:id` - Remove saved destination

##  Groq AI Integration

The application uses Groq AI for:
- **Itinerary Generation** - Creates detailed day-by-day travel plans
- **Activity Suggestions** - Recommends activities based on interests
- **City Information** - Provides comprehensive city details

API Key: You need to add your own Groq API key in the `.env` file

##  Database Schema

### Tables
- **users** - User accounts
- **cities** - City information
- **activities** - Available activities
- **trips** - User trips
- **stops** - Cities in trip itinerary
- **itinerary_activities** - Activities scheduled in stops
- **budgets** - Trip budgets
- **saved_destinations** - User-saved cities

## Environment Variables

### Backend (.env)
```
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret
DATABASE_URL=postgresql://user:pass@localhost:5432/globetrotter
GROQ_API_KEY=your-groq-api-key
```

### Frontend (.env)
```
VITE_API_URL=http://localhost:5000/api
```

## Testing

### Test User Creation
```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"name":"Test User","email":"test@example.com","password":"password123"}'
```

### Test Trip Creation (with JWT token)
```bash
curl -X POST http://localhost:5000/api/trips \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"name":"Paris Trip","start_date":"2026-06-01","end_date":"2026-06-07"}'
```

## Usage Flow

1. **Register/Login** - Create account or login
2. **Dashboard** - View stats and popular destinations
3. **Create Trip** - Set trip name, dates, description
4. **Add Stops** - Search and add cities to visit
5. **Add Activities** - Browse or AI-suggest activities for each city
6. **Manage Budget** - Track costs and budget breakdown
7. **View Itinerary** - See complete trip timeline
8. **Share Trip** - Make trip public and share link

## 🛠️ Development

### Backend Development
```bash
# Run with auto-reload
python app.py

# Or use Flask CLI
flask run --debug
```

### Frontend Development
```bash
npm run dev
```

### Database Migrations
```bash
# Reset database (careful - deletes all data!)
psql -U postgres -d globetrotter -f init_db.sql

# Or use Flask commands
flask init-db
flask seed-db
```

## 📝 Notes

- The Groq API key is already configured
- Sample cities and activities are seeded automatically
- JWT tokens expire after 24 hours
- All dates are stored in UTC
- File uploads are supported for trip cover photos

## 🐛 Troubleshooting

### Database Connection Issues
- Verify PostgreSQL is running
- Check database credentials in .env
- Ensure database 'globetrotter' exists

### Backend Issues
- Verify virtual environment is activated
- Check all dependencies are installed
- Review Flask logs for errors

### Frontend Issues
- Clear browser cache
- Check API_URL in .env
- Verify backend is running
- Check browser console for errors

### CORS Issues
- Ensure Flask-CORS is installed
- Verify API_URL matches backend URL

## 📄 License

This project is created for educational purposes.



