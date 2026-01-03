import requests
from groq import Groq
import json

class GroqService:
    def __init__(self, api_key):
        self.client = Groq(api_key=api_key)
        # Updated to a supported model (see Groq deprecations docs)
        self.model = "llama-3.3-70b-versatile"
    
    def generate_itinerary(self, destination, days, budget_min, budget_max, preferences=None):
        """Generate a detailed travel itinerary using Groq AI"""
        
        preferences_text = ""
        if preferences:
            preferences_text = f"\nUser preferences: {', '.join(preferences)}"
        
        prompt = f"""Create a detailed {days}-day travel itinerary for {destination} with a budget of ₹{budget_min}-₹{budget_max}.
{preferences_text}

For each day, provide:
- Morning activities (with estimated cost)
- Afternoon activities (with estimated cost)
- Evening activities (with estimated cost)
- Recommended restaurants for breakfast, lunch, dinner (with price range)
- Accommodation suggestions (with nightly rate)
- Transportation tips (with estimated cost)
- Hidden gems and local tips

IF this is a multi-city itinerary, include transportation between cities:
- Mode of transport (flight, train, bus, car)
- Estimated travel time
- Estimated cost in INR
- Best booking platforms
- Travel tips

Format the response as JSON with this structure:
{{
  "days": [
    {{
      "day": 1,
      "title": "Day title",
      "activities": [
        {{
          "name": "Activity name",
          "time": "morning/afternoon/evening",
          "description": "Brief description",
          "cost": 500,
          "duration": 2.5,
          "category": "sightseeing/food/adventure/culture/shopping"
        }}
      ],
      "accommodation": {{
        "name": "Hotel name",
        "cost": 3000,
        "description": "Brief description"
      }},
      "meals": [
        {{
          "type": "breakfast/lunch/dinner",
          "suggestion": "Restaurant name",
          "cost": 400
        }}
      ],
      "transport_to_next_day": {{
        "from": "Current city",
        "to": "Next city",
        "modes": [
          {{
            "mode": "flight/train/bus/car",
            "duration": "2 hours",
            "cost": 2000,
            "booking_platform": "MakeMyTrip/IRCTC/RedBus/Google Maps",
            "notes": "Best time to book"
          }}
        ]
      }}
    }}
  ],
  "budget_breakdown": {{
    "accommodation": 21000,
    "food": 7000,
    "activities": 9000,
    "transport": 6000,
    "misc": 2000,
    "total": 45000
  }},
  "tips": ["Tip 1", "Tip 2", "Tip 3"]
}}

Ensure the total stays within budget and all costs are in INR ₹."""

        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert travel planner. Provide detailed, realistic, and budget-conscious travel itineraries. Always respond with valid JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                model=self.model,
                temperature=0.7,
                max_tokens=4000,
            )
            
            response_text = chat_completion.choices[0].message.content
            
            # Try to parse JSON
            try:
                # Extract JSON if wrapped in markdown code blocks
                if "```json" in response_text:
                    response_text = response_text.split("```json")[1].split("```")[0].strip()
                elif "```" in response_text:
                    response_text = response_text.split("```")[1].split("```")[0].strip()
                
                return json.loads(response_text)
            except json.JSONDecodeError:
                # Return as text if JSON parsing fails
                return {"raw_text": response_text}
                
        except Exception as e:
            raise Exception(f"Groq API error: {str(e)}")
    
    def suggest_activities(self, city_name, interests, budget_per_activity=None):
        """Suggest activities for a specific city based on interests"""
        
        budget_text = f" with budget around ${budget_per_activity} per activity" if budget_per_activity else ""
        
        prompt = f"""Suggest 10 activities in {city_name} for someone interested in: {', '.join(interests)}{budget_text}.

Respond with JSON:
{{
  "activities": [
    {{
      "name": "Activity name",
      "description": "Brief description",
      "category": "sightseeing/food/adventure/culture/shopping",
      "estimated_cost": 50,
      "duration_hours": 2.5,
      "best_time": "morning/afternoon/evening/anytime"
    }}
  ]
}}"""

        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are a local travel expert. Suggest authentic and diverse activities. Always respond with valid JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                model=self.model,
                temperature=0.8,
                max_tokens=2000,
            )
            
            response_text = chat_completion.choices[0].message.content
            
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            return json.loads(response_text)
            
        except Exception as e:
            raise Exception(f"Groq API error: {str(e)}")
    
    def get_city_info(self, city_name, country=None):
        """Get comprehensive information about a city"""
        
        location = f"{city_name}, {country}" if country else city_name
        
        prompt = f"""Provide comprehensive information about {location} for travelers.

Respond with JSON:
{{
  "city": "{city_name}",
  "country": "Country name",
  "description": "2-3 sentence description",
  "best_time_to_visit": "Season/months",
  "average_daily_cost": 150,
  "cost_index": 1.2,
  "currency": "INR",
  "popular_for": ["beaches", "history", "nightlife"],
  "must_see": ["Attraction 1", "Attraction 2", "Attraction 3"],
  "local_tips": ["Tip 1", "Tip 2"]
}}"""

        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are a travel information expert. Provide accurate, helpful city information. Always respond with valid JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                model=self.model,
                temperature=0.5,
                max_tokens=1000,
            )
            
            response_text = chat_completion.choices[0].message.content
            
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            return json.loads(response_text)
            
        except Exception as e:
            raise Exception(f"Groq API error: {str(e)}")
