import requests

def get_weather(location):
    # OpenWeatherMap API endpoint for current weather data
    api_url = "https://api.openweathermap.org/data/2.5/weather"
    
    # Parameters for the API request
    params = {
        'q': location,
        'appid': 'e9eb6cb32c281bfae47205f21fa4f70b',
        'units': 'metric',  # Use 'imperial' for Fahrenheit
    }

    # Make the API request
    response = requests.get(api_url, params=params)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Parse the JSON response
        weather_data = response.json()

        # Extract relevant weather information
        temperature = weather_data['main']['temp']
        precipitation = weather_data.get('rain', {}).get('1h', 0)  # Precipitation in the last 1 hour
        humidity = weather_data['main']['humidity']
        wind_speed = weather_data['wind']['speed']
        wind_direction = weather_data['wind']['deg']

        # return the weather information
        return location,temperature,precipitation,humidity,wind_speed,wind_direction
    else:
        print(f"Error: Unable to fetch weather data for {location}. Status Code: {response.status_code}")
