import requests, os
from dotenv import load_dotenv

load_dotenv()

def get_coordinates(city):
    api_key = os.getenv('HERE_API_KEY')
    url = f"https://geocode.search.hereapi.com/v1/geocode?q={city}&apiKey={api_key}"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        if data['items']:
            position = data['items'][0]['position']
            return position['lat'], position['lng']
        else:
            return None
    else:
        print(f"Erreur lors de la requête : {response.status_code}")
        return None


