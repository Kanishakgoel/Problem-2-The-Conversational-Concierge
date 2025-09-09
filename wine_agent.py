# wine_agent.py
import os
import re
from typing import Literal
import requests
import json
from datetime import datetime
from bs4 import BeautifulSoup

# Simple in-memory knowledge base for wine business
WINE_KNOWLEDGE = {
    "about": "Château Napa Valley was founded in 1985 and specializes in premium Cabernet Sauvignon, Chardonnay, and Pinot Noir wines from Napa Valley's finest vineyards.",
    "wines": {
        "cabernet sauvignon": "Estate Cabernet Sauvignon 2019 - $95 - Rich dark fruit flavors with hints of oak",
        "chardonnay": "Reserve Chardonnay 2020 - $75 - Buttery texture with citrus notes",
        "pinot noir": "Pinot Noir 2021 - $65 - Elegant red fruit profile"
    },
    "hours": "Tasting Room Hours: Monday-Saturday: 10AM-5PM, Sunday: 11AM-4PM",
    "contact": "Phone: (707) 555-0123 | Email: info@chateaunapa.com | Address: 123 Vineyard Road, Napa, CA 94558",
    "tasting": "We offer wine tastings daily. Reservations recommended on weekends.",
    "shipping": "We ship to most US states. Shipping costs vary by location.",
    "events": "We host wine pairing dinners every Friday evening and vineyard tours on Saturdays."
}

# Enhanced search function with multiple fallbacks
def enhanced_search(query: str) -> str:
    try:
        # Try DuckDuckGo first
        try:
            from langchain_community.tools import DuckDuckGoSearchRun
            search_tool = DuckDuckGoSearchRun()
            result = search_tool.run(query)
            if result and len(result) > 50:
                return result
        except:
            pass
        
        # Fallback to Google search via requests
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            url = f"https://www.google.com/search?q={requests.utils.quote(query)}"
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract search results
            results = []
            for g in soup.find_all('div', class_='tF2Cxc'):
                title = g.find('h3')
                if title:
                    results.append(title.text)
            
            if results:
                return ". ".join(results[:3])  # Return top 3 results
        except:
            pass
        
        # Final fallback: use a knowledge graph approach
        return f"I searched for information about '{query}'. For the most accurate information about wine-related topics, I recommend checking reputable wine resources or our website."
        
    except Exception as e:
        print(f"Search error: {e}")
        return f"I encountered a search issue. For information about '{query}', please visit our website or contact us directly."

# Weather function with multiple fallbacks
def get_weather() -> str:
    try:
        # First try: Open-Meteo API
        try:
            url = "https://api.open-meteo.com/v1/forecast"
            params = {
                "latitude": 38.2975,
                "longitude": -122.2869,
                "current": "temperature_2m,weather_code",
                "temperature_unit": "fahrenheit",
                "timezone": "auto"
            }
            response = requests.get(url, params=params, timeout=5)
            data = response.json()
            
            weather_codes = {
                0: "clear sky", 1: "mainly clear", 2: "partly cloudy", 3: "overcast",
                45: "foggy", 48: "foggy", 51: "light drizzle", 53: "moderate drizzle",
                61: "light rain", 63: "moderate rain", 65: "heavy rain"
            }
            
            temp = data['current']['temperature_2m']
            condition = weather_codes.get(data['current']['weather_code'], "pleasant")
            return json.dumps({"temperature": temp, "condition": condition})
        except:
            pass
        
        # Fallback: Use weather.com via web scraping (simplified)
        try:
            # This is a simplified example - in production, use proper weather APIs
            return json.dumps({"temperature": 72, "condition": "sunny", "source": "estimated"})
        except:
            pass
        
        return "Weather information currently unavailable"
        
    except Exception as e:
        print(f"Weather API error: {e}")
        return "Weather information currently unavailable"

# Enhanced keyword-based response system
def enhanced_response(user_input: str) -> str:
    user_input_lower = user_input.lower()
    
    # Direct matches
    direct_matches = {
        'hours': WINE_KNOWLEDGE["hours"],
        'open': WINE_KNOWLEDGE["hours"],
        'time': WINE_KNOWLEDGE["hours"],
        'price': "Our wines range from $65 to $95. Cabernet: $95, Chardonnay: $75, Pinot Noir: $65.",
        'cost': "Our wines range from $65 to $95. Cabernet: $95, Chardonnay: $75, Pinot Noir: $65.",
        'contact': WINE_KNOWLEDGE["contact"],
        'address': WINE_KNOWLEDGE["contact"],
        'phone': "Our phone number is (707) 555-0123",
        'email': "Our email is info@chateaunapa.com",
        'about': WINE_KNOWLEDGE["about"],
        'story': WINE_KNOWLEDGE["about"],
        'history': WINE_KNOWLEDGE["about"],
        'tasting': WINE_KNOWLEDGE["tasting"],
        'tour': "We offer vineyard tours on Saturdays at 11AM and 2PM.",
        'events': WINE_KNOWLEDGE["events"],
        'shipping': WINE_KNOWLEDGE["shipping"],
        'delivery': WINE_KNOWLEDGE["shipping"]
    }
    
    for keyword, response in direct_matches.items():
        if keyword in user_input_lower:
            return response
    
    # Wine-specific matches
    wine_matches = {
        'cabernet': WINE_KNOWLEDGE["wines"]["cabernet sauvignon"],
        'chardonnay': WINE_KNOWLEDGE["wines"]["chardonnay"],
        'pinot': WINE_KNOWLEDGE["wines"]["pinot noir"],
        'red wine': "We offer Cabernet Sauvignon and Pinot Noir. Both are excellent choices!",
        'white wine': "Our Reserve Chardonnay is a wonderful white wine option.",
        'wine list': "We offer Cabernet Sauvignon ($95), Chardonnay ($75), and Pinot Noir ($65)."
    }
    
    for keyword, response in wine_matches.items():
        if keyword in user_input_lower:
            return response
    
    return None

# Router function
def router(user_input: str) -> Literal["knowledge", "search", "weather", "simple"]:
    user_input_lower = user_input.lower()
    
    # Check if weather is needed
    weather_keywords = ['weather', 'temperature', 'forecast', 'hot', 'cold', 'rain', 'sunny']
    if any(keyword in user_input_lower for keyword in weather_keywords):
        return "weather"
    
    # Check if we have a simple pre-defined response
    if enhanced_response(user_input):
        return "simple"
    
    # Check if it's a wine-related question
    wine_keywords = ['wine', 'vineyard', 'tasting', 'cabernet', 'chardonnay', 
                    'pinot', 'napa', 'winery', 'bottle', 'vintage', 'grape',
                    'pairing', 'reservation', 'tour', 'event']
    
    if any(keyword in user_input_lower for keyword in wine_keywords):
        return "knowledge"
    
    return "search"

# Knowledge base node
def knowledge_node(user_input: str):
    try:
        # First try enhanced response
        enhanced_resp = enhanced_response(user_input)
        if enhanced_resp:
            return enhanced_resp
            
        # If no direct match, provide general wine information
        return "I'd be happy to help with wine-related questions! We specialize in Cabernet Sauvignon, Chardonnay, and Pinot Noir. What specific information are you looking for?"
            
    except Exception as e:
        print(f"Knowledge node error: {e}")
        return "I specialize in wine knowledge. Please ask me about our wines, tasting hours, or wine-related topics."

# Search node
def search_node(user_input: str):
    try:
        search_result = enhanced_search(user_input)
        return f"I found this information: {search_result}"
            
    except Exception as e:
        print(f"Search node error: {e}")
        return "I'm having trouble with external searches right now. Please try asking about our wines or visit our website for more information."

# Weather node
def weather_node(user_input: str):
    try:
        weather_info = get_weather()
        
        if weather_info != "Weather information currently unavailable":
            weather_data = json.loads(weather_info)
            temp = weather_data.get('temperature', '72')
            condition = weather_data.get('condition', 'pleasant')
            
            # Add wine recommendations based on weather
            wine_tips = {
                'sunny': "Perfect day for our crisp Chardonnay on the patio!",
                'clear': "Great weather for wine tasting. Our Cabernet would be wonderful today.",
                'cloudy': "A nice Pinot Noir would be perfect for this weather.",
                'rain': "Cozy up indoors with a glass of our rich Cabernet Sauvignon.",
                'foggy': "Napa Valley fog makes for great wine! Try our Pinot Noir."
            }
            
            tip = "Perfect day for wine tasting!"
            for weather_type, wine_tip in wine_tips.items():
                if weather_type in condition:
                    tip = wine_tip
                    break
            
            return f"Current weather in Napa Valley: {temp}°F and {condition}. {tip}"
        else:
            return "I can't access current weather information, but Napa Valley typically has wonderful weather for wine tasting year-round!"
            
    except Exception as e:
        print(f"Weather node error: {e}")
        return "Napa Valley enjoys a Mediterranean climate perfect for wine growing. Our tasting room is open daily!"

# Simple response node
def simple_node(user_input: str):
    response = enhanced_response(user_input)
    if response:
        return response
    return "I'm here to help with information about our wines, tasting hours, and Napa Valley. What would you like to know?"

# Main chat function
def chat_with_agent(message: str):
    try:
        if not message or not message.strip():
            return "Please ask me something about our wines or Napa Valley!"
        
        # First use the router to determine the path
        route = router(message)
        
        # Then execute the appropriate node
        if route == "knowledge":
            response = knowledge_node(message)
        elif route == "search":
            response = search_node(message)
        elif route == "weather":
            response = weather_node(message)
        elif route == "simple":
            response = simple_node(message)
        else:
            response = "I'm here to help with information about our wines and Napa Valley. What would you like to know?"
        
        return response
        
    except Exception as e:
        print(f"Chat error: {e}")
        return "Welcome to Château Napa Valley! I can help with information about our wines, tasting hours, and more. What would you like to know?"

# Example usage
if __name__ == "__main__":
    print("Welcome to Château Napa Valley Wine Assistant!")
    print("Type 'quit' to exit\n")
    
    while True:
        user_input = input("You: ")
        if user_input.lower() in ['quit', 'exit', 'bye']:
            print("Thank you for visiting Château Napa Valley! 🍷")
            break
        
        response = chat_with_agent(user_input)
        print(f"\nAssistant: {response}\n")